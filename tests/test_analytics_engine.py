import pandas as pd

from src.analytics_engine import detect_duplicates, denial_metrics, validate_diagnoses


def test_missing_diagnosis_routes_to_provider_clarification():
    frame = pd.DataFrame([{"accession_id": "A1", "test_code": "83036", "diagnosis_code": None}])
    result = validate_diagnoses(frame).iloc[0]
    assert result["diagnosis_result"] == "Missing diagnosis"
    assert result["diagnosis_action"] == "Provider clarification"


def test_malformed_diagnosis_is_data_correction_not_medical_necessity():
    frame = pd.DataFrame([{"accession_id": "A1", "test_code": "83036", "diagnosis_code": "BADCODE"}])
    result = validate_diagnoses(frame).iloc[0]
    assert result["diagnosis_result"] == "Malformed diagnosis"
    assert result["diagnosis_action"] == "Coding data correction"


def test_simulated_policy_review_does_not_change_diagnosis():
    frame = pd.DataFrame([{"accession_id": "A1", "test_code": "83036", "diagnosis_code": "I10"}])
    result = validate_diagnoses(frame).iloc[0]
    assert result["diagnosis_result"] == "Simulated policy review"
    assert result["diagnosis_action"] == "Documentation review"


def test_exact_duplicate_is_sent_to_manual_review():
    frame = pd.DataFrame([
        {"accession_id": "A1", "patient_id": "P1", "service_date": "2026-10-01", "test_code": "83036", "provider_id": "D1"},
        {"accession_id": "A2", "patient_id": "P1", "service_date": "2026-10-01", "test_code": "83036", "provider_id": "D1"},
    ])
    result = detect_duplicates(frame)
    assert (result["duplicate_result"] == "Review exact match").all()
    assert (result["duplicate_review_status"] == "Manual review").all()


def test_denial_metrics_separate_charge_expected_and_payment():
    claims = pd.DataFrame([
        {"claim_id": "C1", "claim_status": "Denied", "charge_amount": 200.0, "allowed_amount": 120.0, "expected_reimbursement": 100.0, "payment_amount": 0.0},
        {"claim_id": "C2", "claim_status": "Paid", "charge_amount": 100.0, "allowed_amount": 70.0, "expected_reimbursement": 60.0, "payment_amount": 60.0},
    ])
    denials = pd.DataFrame([
        {"claim_id": "C1", "denied_amount": 100.0, "recovered_amount": 80.0, "denial_date": "2026-10-01", "resolution_date": "2026-10-11"}
    ])
    metrics = denial_metrics(claims, denials)
    assert metrics["denial_rate"] == 0.5
    assert metrics["recovery_rate"] == 0.8
    assert metrics["gross_charges"] == 300.0
    assert metrics["expected_reimbursement"] == 160.0
    assert metrics["actual_payments"] == 140.0
