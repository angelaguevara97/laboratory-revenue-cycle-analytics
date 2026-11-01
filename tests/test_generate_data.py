import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generate_data import build_dataset


def test_requested_accession_count_is_created():
    tables = build_dataset(1_000)
    assert len(tables["accessions"]) == 1_000


def test_primary_identifiers_are_unique():
    tables = build_dataset(1_000)
    key_map = {
        "patients": "patient_id",
        "providers": "provider_id",
        "payers": "payer_id",
        "accessions": "accession_id",
        "eligibility": "eligibility_id",
        "claims": "claim_id",
        "denials": "denial_id",
        "work_queue": "work_item_id",
        "claim_history": "event_id",
    }
    for table_name, key in key_map.items():
        assert tables[table_name][key].is_unique


def test_claim_financial_relationships_are_sensible():
    claims = build_dataset(1_000)["claims"]
    assert (claims["allowed_amount"] <= claims["charge_amount"]).all()
    assert (claims["expected_reimbursement"] <= claims["allowed_amount"]).all()
    assert (claims["payment_amount"] <= claims["expected_reimbursement"]).all()
    assert (claims[["charge_amount", "allowed_amount", "expected_reimbursement", "payment_amount"]] >= 0).all().all()


def test_denials_reference_existing_claims():
    tables = build_dataset(1_000)
    assert set(tables["denials"]["claim_id"]).issubset(set(tables["claims"]["claim_id"]))


def test_work_queue_references_existing_accessions():
    tables = build_dataset(1_000)
    assert set(tables["work_queue"]["accession_id"]).issubset(set(tables["accessions"]["accession_id"]))


def test_dataset_is_reproducible():
    first = build_dataset(500)["accessions"]
    second = build_dataset(500)["accessions"]
    pd.testing.assert_frame_equal(first, second)
