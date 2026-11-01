from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "generated"
ANALYTICS_DIR = ROOT / "data" / "analytics"
AS_OF_DATE = pd.Timestamp("2026-10-31")

ICD10_PATTERN = re.compile(r"^[A-TV-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?$")

# These combinations are educational simulation rules only. They are not payer coverage policies.
SIMULATED_POLICY = {
    "83036": {"E11.9", "R73.03"},
    "84443": {"E03.9", "R53.83"},
    "80061": {"E78.5", "I10", "Z00.00"},
    "82728": {"D64.9", "R53.83"},
    "83540": {"D64.9", "R53.83"},
    "82306": {"E55.9", "R53.83"},
    "82607": {"D64.9", "R53.83"},
    "81001": {"R35.0", "Z00.00"},
    "80053": {"E11.9", "I10", "Z00.00", "R53.83"},
    "85025": {"D64.9", "R53.83", "Z00.00"},
}


def load_tables(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    names = ["patients", "providers", "payers", "accessions", "eligibility", "claims", "denials", "work_queue", "claim_history"]
    missing = [name for name in names if not (data_dir / f"{name}.csv").exists()]
    if missing:
        raise FileNotFoundError("Generate the synthetic dataset first. Missing: " + ", ".join(missing))
    return {name: pd.read_csv(data_dir / f"{name}.csv") for name in names}


def validate_diagnoses(accessions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in accessions.itertuples(index=False):
        diagnosis = row.diagnosis_code if isinstance(row.diagnosis_code, str) else ""
        if not diagnosis:
            result, action = "Missing diagnosis", "Provider clarification"
        elif not ICD10_PATTERN.match(diagnosis):
            result, action = "Malformed diagnosis", "Coding data correction"
        elif diagnosis not in SIMULATED_POLICY.get(str(row.test_code), set()):
            result, action = "Simulated policy review", "Documentation review"
        else:
            result, action = "Pass", "No action"
        rows.append({"accession_id": row.accession_id, "diagnosis_result": result, "diagnosis_action": action})
    return pd.DataFrame(rows)


def validate_eligibility(accessions: pd.DataFrame, eligibility: pd.DataFrame) -> pd.DataFrame:
    frame = accessions[["accession_id"]].merge(eligibility, on="accession_id", how="left")
    conditions = [
        frame["coverage_status"].eq("Inactive"),
        frame["coverage_status"].eq("Unable to verify"),
        frame["subscriber_match"].eq("Mismatch"),
        frame["subscriber_match"].eq("Missing"),
        frame["authorization_status"].eq("Missing"),
    ]
    choices = ["Inactive coverage", "Eligibility verification", "Subscriber mismatch", "Subscriber information missing", "Authorization review"]
    frame["eligibility_result"] = np.select(conditions, choices, default="Pass")
    return frame[["accession_id", "eligibility_result"]]


def detect_duplicates(accessions: pd.DataFrame) -> pd.DataFrame:
    frame = accessions.copy()
    exact_keys = ["patient_id", "service_date", "test_code", "provider_id"]
    frame["exact_group_size"] = frame.groupby(exact_keys)["accession_id"].transform("size")
    frame["duplicate_result"] = np.where(frame["exact_group_size"] > 1, "Review exact match", "No duplicate signal")

    frame["service_date_dt"] = pd.to_datetime(frame["service_date"])
    frame = frame.sort_values(["patient_id", "test_code", "service_date_dt", "accession_id"])
    prior_date = frame.groupby(["patient_id", "test_code"])["service_date_dt"].shift(1)
    days_from_prior = (frame["service_date_dt"] - prior_date).dt.days
    possible = frame["duplicate_result"].eq("No duplicate signal") & days_from_prior.between(0, 2)
    frame.loc[possible, "duplicate_result"] = "Review near match"
    frame["duplicate_review_status"] = np.where(frame["duplicate_result"].eq("No duplicate signal"), "Not required", "Manual review")
    return frame[["accession_id", "duplicate_result", "duplicate_review_status"]].sort_values("accession_id")


def build_exception_queue(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    accessions = tables["accessions"].copy()
    payers = tables["payers"][["payer_id", "payer_name", "filing_limit_days"]]
    diagnosis = validate_diagnoses(accessions)
    eligibility = validate_eligibility(accessions, tables["eligibility"])
    duplicates = detect_duplicates(accessions)

    frame = accessions.merge(payers, on="payer_id").merge(diagnosis, on="accession_id").merge(eligibility, on="accession_id").merge(duplicates, on="accession_id")
    frame["service_date"] = pd.to_datetime(frame["service_date"])
    frame["filing_deadline"] = frame["service_date"] + pd.to_timedelta(frame["filing_limit_days"], unit="D")
    frame["days_to_filing"] = (frame["filing_deadline"] - AS_OF_DATE).dt.days

    def reason(row: pd.Series) -> str:
        reasons = []
        if row["diagnosis_result"] != "Pass":
            reasons.append(row["diagnosis_result"])
        if row["eligibility_result"] != "Pass":
            reasons.append(row["eligibility_result"])
        if row["duplicate_result"] != "No duplicate signal":
            reasons.append(row["duplicate_result"])
        return "; ".join(reasons)

    frame["exception_reason"] = frame.apply(reason, axis=1)
    frame = frame[frame["exception_reason"].ne("")].copy()
    urgency = np.clip((60 - frame["days_to_filing"]) / 60, 0, 1)
    value = np.clip(frame["charge_amount"] / 100, 0, 1)
    resolvability = np.where(frame["eligibility_result"].eq("Pass"), 0.78, 0.62)
    frame["priority_score"] = np.round(urgency * 50 + value * 25 + resolvability * 25, 2)
    frame["priority"] = pd.cut(frame["priority_score"], bins=[-1, 45, 65, 100], labels=["Routine", "High", "Urgent"])
    frame["revenue_at_risk"] = frame["charge_amount"]
    frame["queue_status"] = np.where(frame["days_to_filing"] < 0, "Escalated", "Open")
    frame["provider_message"] = np.where(
        frame["diagnosis_result"].eq("Missing diagnosis"),
        "Please provide the diagnosis documented for this laboratory order so billing can be completed accurately.",
        np.where(frame["diagnosis_result"].eq("Simulated policy review"), "Please confirm the clinical documentation associated with this laboratory order. No diagnosis change is requested.", "")
    )
    cols = ["accession_id", "patient_id", "provider_id", "payer_name", "service_date", "test_code", "diagnosis_code", "exception_reason", "diagnosis_action", "days_to_filing", "filing_deadline", "charge_amount", "revenue_at_risk", "priority_score", "priority", "queue_status", "provider_message"]
    return frame[cols].sort_values(["priority_score", "charge_amount"], ascending=False)


def denial_metrics(claims: pd.DataFrame, denials: pd.DataFrame) -> dict[str, float]:
    denied_claims = claims[claims["claim_status"].eq("Denied")]
    resolved = denials[denials["resolution_date"].notna()].copy()
    if not resolved.empty:
        resolved["days_to_resolution"] = (pd.to_datetime(resolved["resolution_date"]) - pd.to_datetime(resolved["denial_date"])).dt.days
    total_denied = float(denials["denied_amount"].sum())
    recovered = float(denials["recovered_amount"].sum())
    return {
        "claims_submitted": float(len(claims)),
        "denied_claims": float(len(denied_claims)),
        "denial_rate": float(len(denied_claims) / len(claims)) if len(claims) else 0.0,
        "denied_dollars": total_denied,
        "recovered_dollars": recovered,
        "recovery_rate": recovered / total_denied if total_denied else 0.0,
        "average_resolution_days": float(resolved["days_to_resolution"].mean()) if not resolved.empty else 0.0,
        "gross_charges": float(claims["charge_amount"].sum()),
        "allowed_amounts": float(claims["allowed_amount"].sum()),
        "expected_reimbursement": float(claims["expected_reimbursement"].sum()),
        "actual_payments": float(claims["payment_amount"].sum() + recovered),
    }


def run_analytics(data_dir: Path = DATA_DIR, output_dir: Path = ANALYTICS_DIR) -> dict[str, object]:
    tables = load_tables(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnosis = validate_diagnoses(tables["accessions"])
    eligibility = validate_eligibility(tables["accessions"], tables["eligibility"])
    duplicates = detect_duplicates(tables["accessions"])
    queue = build_exception_queue(tables)
    metrics = denial_metrics(tables["claims"], tables["denials"])

    diagnosis.to_csv(output_dir / "diagnosis_validation.csv", index=False)
    eligibility.to_csv(output_dir / "eligibility_validation.csv", index=False)
    duplicates.to_csv(output_dir / "duplicate_review.csv", index=False)
    queue.to_csv(output_dir / "exception_queue.csv", index=False)
    pd.DataFrame([metrics]).to_csv(output_dir / "revenue_metrics.csv", index=False)
    return {"diagnosis": diagnosis, "eligibility": eligibility, "duplicates": duplicates, "queue": queue, "metrics": metrics}


if __name__ == "__main__":
    results = run_analytics()
    print(f"Exception queue rows: {len(results['queue']):,}")
    print(f"Denial rate: {results['metrics']['denial_rate']:.1%}")
    print(f"Recovered dollars: ${results['metrics']['recovered_dollars']:,.2f}")
