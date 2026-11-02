import pandas as pd
from src.generate_data import build_dataset

def test_requested_accession_count_is_created(): assert len(build_dataset(1000)['accessions'])==1000

def test_primary_identifiers_are_unique():
    t=build_dataset(1000); keys={'patients':'patient_id','providers':'provider_id','clients':'client_account_id','payers':'payer_id','tests':'test_code','diagnoses':'diagnosis_code','accessions':'accession_id','eligibility':'eligibility_id','claims':'claim_id','denials':'denial_id','work_queue':'work_item_id','claim_history':'event_id'}
    for n,k in keys.items(): assert t[n][k].is_unique

def test_claim_financial_relationships_are_sensible():
    c=build_dataset(1000)['claims']; assert (c.allowed_amount<=c.charge_amount).all(); assert (c.expected_reimbursement<=c.allowed_amount).all(); assert (c.payment_amount<=c.expected_reimbursement).all(); assert (c[['charge_amount','allowed_amount','expected_reimbursement','payment_amount']]>=0).all().all()

def test_recovery_never_exceeds_denied_balance():
    d=build_dataset(1000)['denials']; assert (d.recovered_amount<=d.denied_amount).all()

def test_client_region_and_call_point_are_consistent():
    t=build_dataset(1000); a=t['accessions'].merge(t['clients'],on='client_account_id',suffixes=('','_client')); assert (a.region==a.region_client).all(); assert (a.call_point==a.call_point_client).all()

def test_dataset_is_reproducible(): pd.testing.assert_frame_equal(build_dataset(500)['accessions'],build_dataset(500)['accessions'])
