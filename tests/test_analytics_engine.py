import pandas as pd
from src.generate_data import build_dataset
from src.analytics_engine import validate_diagnoses, detect_duplicates, claim_fact, kpis, grouped_metrics, data_quality_checks

def test_missing_diagnosis_routes_to_provider_clarification():
    r=validate_diagnoses(pd.DataFrame([{'accession_id':'A1','test_code':'83036','diagnosis_code':None}])).iloc[0]; assert r.diagnosis_action=='Provider clarification'

def test_simulated_policy_review_does_not_change_diagnosis():
    r=validate_diagnoses(pd.DataFrame([{'accession_id':'A1','test_code':'83036','diagnosis_code':'I10'}])).iloc[0]; assert r.diagnosis_action=='Documentation review'

def test_exact_duplicate_is_sent_to_manual_review():
    f=pd.DataFrame([{'accession_id':'A1','patient_id':'P1','service_date':'2026-10-01','test_code':'83036','provider_id':'D1'},{'accession_id':'A2','patient_id':'P1','service_date':'2026-10-01','test_code':'83036','provider_id':'D1'}]); assert (detect_duplicates(f).duplicate_review_status=='Manual review').all()

def test_grouped_claim_counts_reconcile():
    t=build_dataset(2000); f=claim_fact(t); g=grouped_metrics(f,'region'); assert g.total_claims.sum()==f.claim_id.nunique()

def test_data_quality_controls_pass_generated_data():
    q=data_quality_checks(build_dataset(2000)); assert all(v==0 for v in q.values())

def test_kpis_do_not_double_count_claims():
    t=build_dataset(2000); f=claim_fact(t); m=kpis(f); assert m['total_claims']==len(t['claims']); assert m['denied_claims']==len(t['denials'])
