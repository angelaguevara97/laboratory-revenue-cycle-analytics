from __future__ import annotations

import argparse
import random
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
DEFAULT_ACCESSIONS = 25_000
ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "data" / "generated"
DATABASE_PATH = ROOT / "database" / "lab_revenue_cycle.db"
SCHEMA_PATH = ROOT / "database" / "schema.sql"

TEST_CATALOG = {
    "80053": ("Comprehensive metabolic panel", 68.0),
    "85025": ("Complete blood count", 42.0),
    "83036": ("Hemoglobin A1c", 49.0),
    "84443": ("Thyroid stimulating hormone", 58.0),
    "80061": ("Lipid panel", 61.0),
    "81001": ("Urinalysis", 31.0),
    "82728": ("Ferritin", 55.0),
    "83540": ("Iron", 44.0),
    "82306": ("Vitamin D", 86.0),
    "82607": ("Vitamin B12", 63.0),
}

DIAGNOSIS_CODES = [
    "E11.9",
    "E78.5",
    "I10",
    "R53.83",
    "D64.9",
    "E03.9",
    "R73.03",
    "Z00.00",
    "R35.0",
    "E55.9",
]

PAYER_ROWS = [
    ("PAY001", "Simulated Commercial Plan A", "Commercial", 90),
    ("PAY002", "Simulated Commercial Plan B", "Commercial", 120),
    ("PAY003", "Simulated Medicare Like Plan", "Government Simulation", 365),
    ("PAY004", "Simulated Medicaid Like Plan", "Government Simulation", 180),
    ("PAY005", "Simulated Regional Plan", "Commercial", 120),
]

SPECIALTIES = [
    "Primary Care",
    "Endocrinology",
    "Cardiology",
    "Internal Medicine",
    "Rheumatology",
    "Nephrology",
    "Gastroenterology",
]

STATES = ["NJ", "NY", "PA", "CT"]


def identifiers(prefix: str, count: int, width: int = 7) -> list[str]:
    return [f"{prefix}{i:0{width}d}" for i in range(1, count + 1)]


def make_patients(rng: np.random.Generator, count: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": identifiers("PT", count),
            "birth_year": rng.integers(1935, 2009, count),
            "sex": rng.choice(["F", "M", "X"], count, p=[0.505, 0.485, 0.01]),
            "state": rng.choice(STATES, count, p=[0.68, 0.18, 0.10, 0.04]),
        }
    )


def make_providers(rng: np.random.Generator, count: int = 650) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "provider_id": identifiers("PR", count, 5),
            "specialty": rng.choice(SPECIALTIES, count),
            "state": rng.choice(STATES, count, p=[0.70, 0.17, 0.09, 0.04]),
        }
    )


def make_payers() -> pd.DataFrame:
    return pd.DataFrame(
        PAYER_ROWS,
        columns=["payer_id", "payer_name", "payer_type", "filing_limit_days"],
    )


def make_accessions(
    rng: np.random.Generator,
    patients: pd.DataFrame,
    providers: pd.DataFrame,
    payers: pd.DataFrame,
    count: int,
) -> pd.DataFrame:
    end_date = pd.Timestamp("2026-10-31")
    service_offsets = rng.integers(0, 240, count)
    service_dates = end_date - pd.to_timedelta(service_offsets, unit="D")
    test_codes = rng.choice(list(TEST_CATALOG), count)
    base_charges = np.array([TEST_CATALOG[code][1] for code in test_codes])
    charges = np.round(base_charges * rng.uniform(0.92, 1.12, count), 2)
    diagnosis = rng.choice(DIAGNOSIS_CODES, count).astype(object)

    missing_mask = rng.random(count) < 0.035
    malformed_mask = (~missing_mask) & (rng.random(count) < 0.015)
    diagnosis[missing_mask] = None
    diagnosis[malformed_mask] = rng.choice(["BADCODE", "123.XX", "E11..9"], malformed_mask.sum())

    frame = pd.DataFrame(
        {
            "accession_id": identifiers("ACC", count),
            "patient_id": rng.choice(patients["patient_id"], count),
            "provider_id": rng.choice(providers["provider_id"], count),
            "payer_id": rng.choice(payers["payer_id"], count, p=[0.31, 0.24, 0.20, 0.12, 0.13]),
            "service_date": service_dates.strftime("%Y-%m-%d"),
            "collection_date": service_dates.strftime("%Y-%m-%d"),
            "test_code": test_codes,
            "diagnosis_code": diagnosis,
            "charge_amount": charges,
            "accession_status": "Ready for billing",
        }
    )

    issue_mask = missing_mask | malformed_mask
    frame.loc[issue_mask, "accession_status"] = "Billing review"

    duplicate_count = max(1, int(count * 0.012))
    duplicate_targets = rng.choice(np.arange(1, count), duplicate_count, replace=False)
    sources = rng.choice(np.arange(0, count), duplicate_count, replace=False)
    for target, source in zip(duplicate_targets, sources):
        for column in ["patient_id", "provider_id", "payer_id", "service_date", "collection_date", "test_code", "diagnosis_code", "charge_amount"]:
            frame.at[target, column] = frame.at[source, column]

    return frame


def make_eligibility(rng: np.random.Generator, accessions: pd.DataFrame) -> pd.DataFrame:
    count = len(accessions)
    coverage = rng.choice(["Active", "Inactive", "Unable to verify"], count, p=[0.93, 0.045, 0.025])
    subscriber = rng.choice(["Match", "Mismatch", "Missing"], count, p=[0.955, 0.03, 0.015])
    authorization = rng.choice(["Not required", "Present", "Missing"], count, p=[0.72, 0.25, 0.03])
    service_dates = pd.to_datetime(accessions["service_date"])
    checked_dates = service_dates - pd.to_timedelta(rng.integers(0, 4, count), unit="D")
    return pd.DataFrame(
        {
            "eligibility_id": identifiers("ELG", count),
            "accession_id": accessions["accession_id"],
            "coverage_status": coverage,
            "subscriber_match": subscriber,
            "authorization_status": authorization,
            "checked_date": checked_dates.dt.strftime("%Y-%m-%d"),
        }
    )


def make_claims(
    rng: np.random.Generator,
    accessions: pd.DataFrame,
    eligibility: pd.DataFrame,
) -> pd.DataFrame:
    eligible_mask = (
        (eligibility["coverage_status"] == "Active")
        & (eligibility["subscriber_match"] == "Match")
        & (eligibility["authorization_status"] != "Missing")
        & (accessions["accession_status"] == "Ready for billing")
    )
    submitted = accessions.loc[eligible_mask].copy().reset_index(drop=True)
    count = len(submitted)
    service_dates = pd.to_datetime(submitted["service_date"])
    submission_dates = service_dates + pd.to_timedelta(rng.integers(1, 13, count), unit="D")
    allowed_ratio = rng.uniform(0.42, 0.78, count)
    allowed = np.round(submitted["charge_amount"].to_numpy() * allowed_ratio, 2)
    expected = np.round(allowed * rng.uniform(0.82, 0.98, count), 2)
    denial_mask = rng.random(count) < 0.095
    payment = expected.copy()
    payment[denial_mask] = 0.0
    statuses = np.where(denial_mask, "Denied", "Paid")

    return pd.DataFrame(
        {
            "claim_id": identifiers("CLM", count),
            "accession_id": submitted["accession_id"],
            "submission_date": submission_dates.dt.strftime("%Y-%m-%d"),
            "claim_type": "Original",
            "charge_amount": submitted["charge_amount"].to_numpy(),
            "allowed_amount": allowed,
            "expected_reimbursement": expected,
            "payment_amount": payment,
            "claim_status": statuses,
            "original_claim_id": None,
        }
    )


def make_denials(rng: np.random.Generator, claims: pd.DataFrame) -> pd.DataFrame:
    denied = claims.loc[claims["claim_status"] == "Denied"].copy().reset_index(drop=True)
    count = len(denied)
    categories = rng.choice(
        ["Eligibility", "Coding or documentation", "Authorization", "Duplicate review", "Other administrative"],
        count,
        p=[0.29, 0.30, 0.15, 0.12, 0.14],
    )
    reason_map = {
        "Eligibility": "SIM ELIG",
        "Coding or documentation": "SIM DOC",
        "Authorization": "SIM AUTH",
        "Duplicate review": "SIM DUP",
        "Other administrative": "SIM ADMIN",
    }
    denial_dates = pd.to_datetime(denied["submission_date"]) + pd.to_timedelta(rng.integers(7, 31, count), unit="D")
    resolution = rng.choice(["Recovered", "Pending", "Written off"], count, p=[0.56, 0.29, 0.15])
    resolution_days = rng.integers(4, 46, count)
    resolution_dates = denial_dates + pd.to_timedelta(resolution_days, unit="D")
    resolution_date_text = resolution_dates.strftime("%Y-%m-%d").astype(object)
    resolution_date_text[resolution == "Pending"] = None
    recovered = np.where(
        resolution == "Recovered",
        np.round(denied["expected_reimbursement"].to_numpy() * rng.uniform(0.75, 1.0, count), 2),
        0.0,
    )

    return pd.DataFrame(
        {
            "denial_id": identifiers("DEN", count),
            "claim_id": denied["claim_id"],
            "denial_category": categories,
            "simulated_reason_code": [reason_map[value] for value in categories],
            "denial_date": denial_dates.dt.strftime("%Y-%m-%d"),
            "denied_amount": denied["expected_reimbursement"].to_numpy(),
            "resolution_status": resolution,
            "resolution_date": resolution_date_text,
            "recovered_amount": recovered,
        }
    )


def make_work_queue(
    rng: np.random.Generator,
    accessions: pd.DataFrame,
    eligibility: pd.DataFrame,
    payers: pd.DataFrame,
) -> pd.DataFrame:
    merged = accessions.merge(eligibility, on="accession_id").merge(
        payers[["payer_id", "filing_limit_days"]], on="payer_id"
    )
    diagnosis_issue = merged["accession_status"] == "Billing review"
    coverage_issue = merged["coverage_status"] != "Active"
    subscriber_issue = merged["subscriber_match"] != "Match"
    authorization_issue = merged["authorization_status"] == "Missing"
    any_issue = diagnosis_issue | coverage_issue | subscriber_issue | authorization_issue
    queue = merged.loc[any_issue].copy().reset_index(drop=True)

    def classify(row: pd.Series) -> str:
        if row["accession_status"] == "Billing review":
            return "Diagnosis or documentation review"
        if row["coverage_status"] != "Active":
            return "Eligibility review"
        if row["subscriber_match"] != "Match":
            return "Subscriber information review"
        return "Authorization review"

    queue["exception_type"] = queue.apply(classify, axis=1)
    service_date = pd.to_datetime(queue["service_date"])
    filing_date = service_date + pd.to_timedelta(queue["filing_limit_days"], unit="D")
    as_of = pd.Timestamp("2026-10-31")
    days_remaining = (filing_date - as_of).dt.days
    filing_urgency = np.clip((60 - days_remaining) / 60, 0, 1)
    value_score = np.clip(queue["charge_amount"] / 100, 0, 1)
    resolution_probability = np.round(rng.uniform(0.45, 0.92, len(queue)), 2)
    priority = np.round((filing_urgency * 50) + (value_score * 25) + (resolution_probability * 25), 2)

    created = service_date + pd.to_timedelta(rng.integers(0, 5, len(queue)), unit="D")
    follow_up = created + pd.to_timedelta(rng.integers(2, 11, len(queue)), unit="D")

    return pd.DataFrame(
        {
            "work_item_id": identifiers("WQ", len(queue)),
            "accession_id": queue["accession_id"],
            "exception_type": queue["exception_type"],
            "priority_score": priority,
            "queue_status": rng.choice(["Open", "Pending", "Resolved", "Escalated"], len(queue), p=[0.50, 0.25, 0.20, 0.05]),
            "created_date": created.dt.strftime("%Y-%m-%d"),
            "follow_up_date": follow_up.dt.strftime("%Y-%m-%d"),
            "resolution_probability": resolution_probability,
        }
    )


def make_claim_history(claims: pd.DataFrame, denials: pd.DataFrame) -> pd.DataFrame:
    events: list[dict[str, object]] = []
    event_number = 1
    for row in claims.itertuples(index=False):
        events.append(
            {
                "event_id": f"EVT{event_number:08d}",
                "claim_id": row.claim_id,
                "event_type": "Submitted",
                "event_date": row.submission_date,
                "notes": "Synthetic original claim submitted",
            }
        )
        event_number += 1
    for row in denials.itertuples(index=False):
        events.append(
            {
                "event_id": f"EVT{event_number:08d}",
                "claim_id": row.claim_id,
                "event_type": "Denied",
                "event_date": row.denial_date,
                "notes": f"Synthetic denial category: {row.denial_category}",
            }
        )
        event_number += 1
    return pd.DataFrame(events)


def write_outputs(tables: dict[str, pd.DataFrame]) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    for name, frame in tables.items():
        frame.to_csv(GENERATED_DIR / f"{name}.csv", index=False)

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf8"))
        for name, frame in tables.items():
            frame.to_sql(name, connection, if_exists="append", index=False)


def build_dataset(accession_count: int = DEFAULT_ACCESSIONS) -> dict[str, pd.DataFrame]:
    random.seed(SEED)
    rng = np.random.default_rng(SEED)
    patient_count = max(8_000, int(accession_count * 0.58))
    patients = make_patients(rng, patient_count)
    providers = make_providers(rng)
    payers = make_payers()
    accessions = make_accessions(rng, patients, providers, payers, accession_count)
    eligibility = make_eligibility(rng, accessions)
    claims = make_claims(rng, accessions, eligibility)
    denials = make_denials(rng, claims)
    work_queue = make_work_queue(rng, accessions, eligibility, payers)
    claim_history = make_claim_history(claims, denials)
    return {
        "patients": patients,
        "providers": providers,
        "payers": payers,
        "accessions": accessions,
        "eligibility": eligibility,
        "claims": claims,
        "denials": denials,
        "work_queue": work_queue,
        "claim_history": claim_history,
    }


def summarize(tables: dict[str, pd.DataFrame]) -> None:
    print("Synthetic laboratory revenue cycle dataset created")
    for name, frame in tables.items():
        print(f"{name}: {len(frame):,} rows")
    claims = tables["claims"]
    denials = tables["denials"]
    denial_rate = len(denials) / len(claims) if len(claims) else 0
    recovered = denials["recovered_amount"].sum()
    print(f"Initial denial rate: {denial_rate:.1%}")
    print(f"Synthetic recovered revenue: ${recovered:,.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic laboratory revenue cycle data")
    parser.add_argument("--accessions", type=int, default=DEFAULT_ACCESSIONS)
    args = parser.parse_args()
    tables = build_dataset(args.accessions)
    write_outputs(tables)
    summarize(tables)


if __name__ == "__main__":
    main()
