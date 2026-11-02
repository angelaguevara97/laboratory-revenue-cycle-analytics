from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; DATA_DIR=ROOT/'data'/'generated'; ANALYTICS_DIR=ROOT/'data'/'analytics'; AS_OF_DATE=pd.Timestamp('2026-10-31')
ICD10_PATTERN=re.compile(r'^[A-TV-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?$')
SIMULATED_POLICY={'83036':{'E11.9','R73.03'},'84443':{'E03.9','R53.83'},'80061':{'E78.5','I10','Z00.00'},'82728':{'D64.9','R53.83'},'82306':{'E55.9','R53.83'},'82607':{'D64.9','R53.83'},'80053':{'E11.9','I10','Z00.00','R53.83'},'85025':{'D64.9','R53.83','Z00.00'},'84153':{'Z12.5','R97.20'},'86308':{'B27.90','R50.9'},'87591':{'Z11.3','A74.9'},'87491':{'Z11.3','A54.9'}}
NAMES=['patients','providers','clients','payers','tests','diagnoses','accessions','eligibility','claims','denials','work_queue','claim_history']
def load_tables(data_dir=DATA_DIR):
    missing=[n for n in NAMES if not (data_dir/f'{n}.csv').exists()]
    if missing: raise FileNotFoundError('Generate synthetic data first. Missing '+', '.join(missing))
    return {n:pd.read_csv(data_dir/f'{n}.csv') for n in NAMES}
def validate_diagnoses(accessions):
    rows=[]
    for r in accessions.itertuples(index=False):
        dx=r.diagnosis_code if isinstance(r.diagnosis_code,str) else ''
        if not dx: result,action='Missing diagnosis','Provider clarification'
        elif not ICD10_PATTERN.match(dx): result,action='Malformed diagnosis','Coding data correction'
        elif dx not in SIMULATED_POLICY.get(str(r.test_code),set()): result,action='Simulated policy review','Documentation review'
        else: result,action='Pass','No action'
        rows.append({'accession_id':r.accession_id,'diagnosis_result':result,'diagnosis_action':action})
    return pd.DataFrame(rows)
def detect_duplicates(accessions):
    f=accessions.copy(); keys=['patient_id','service_date','test_code','provider_id']; f['exact_group_size']=f.groupby(keys)['accession_id'].transform('size'); f['duplicate_result']=np.where(f.exact_group_size>1,'Review exact match','No duplicate signal'); f['duplicate_review_status']=np.where(f.duplicate_result.eq('No duplicate signal'),'Not required','Manual review'); return f[['accession_id','duplicate_result','duplicate_review_status']]
def claim_fact(t):
    c=t['claims'].merge(t['accessions'],on='accession_id',suffixes=('_claim','')).merge(t['payers'],on='payer_id').merge(t['tests'],on='test_code').merge(t['diagnoses'],on='diagnosis_code',how='left'); f=c.merge(t['denials'],on='claim_id',how='left'); f['is_denied']=f.claim_status.eq('Denied'); f['denied_amount']=f.denied_amount.fillna(0.0); f['recovered_amount']=f.recovered_amount.fillna(0.0); f['diagnosis_related']=f.diagnosis_related.fillna(False).astype(bool); f['service_date']=pd.to_datetime(f.service_date); f['submission_date']=pd.to_datetime(f.submission_date); f['month']=f.submission_date.dt.to_period('M').astype(str); return f
def filter_fact(f,filters=None):
    out=f.copy()
    for col,values in (filters or {}).items():
        if values and col in out: out=out[out[col].isin(values)]
    return out
def kpis(f):
    claims=f.claim_id.nunique(); denied=f.loc[f.is_denied,'claim_id'].nunique(); dd=f.denied_amount.sum(); rec=f.recovered_amount.sum(); return {'total_claims':claims,'denied_claims':denied,'denial_rate':denied/claims if claims else 0,'billed_dollars':f.charge_amount_claim.sum(),'denied_dollars':dd,'recovered_dollars':rec,'recovery_rate':rec/dd if dd else 0}
def grouped_metrics(f,group):
    rows=[]
    for key,g in f.groupby(group,dropna=False):
        m=kpis(g); m[group]=key; m['avg_denied_dollars']=m['denied_dollars']/m['denied_claims'] if m['denied_claims'] else 0; rows.append(m)
    return pd.DataFrame(rows)
def diagnosis_analytics(f):
    x=f[f.diagnosis_related].copy(); return grouped_metrics(x,'diagnosis_code').merge(f[['diagnosis_code','diagnosis_description']].drop_duplicates(),on='diagnosis_code',how='left') if len(x) else pd.DataFrame()
def recovery_opportunities(f):
    d=f[f.is_denied].copy(); d['outstanding']=np.maximum(d.denied_amount-d.recovered_amount,0); prob=np.where(d.resolution_status.eq('Recovered'),.80,np.where(d.resolution_status.eq('Pending'),.58,.22)); age=np.clip((AS_OF_DATE-pd.to_datetime(d.denial_date)).dt.days,0,None); complexity=d.denial_category.map({'Eligibility':.35,'Diagnosis documentation':.55,'Authorization':.60,'Duplicate claim':.45,'Medical necessity':.75,'Timely filing':.85,'Other administrative':.50}).fillna(.5); d['estimated_recoverable']=np.round(d.outstanding*prob,2); d['priority_score']=np.round(np.clip(d.outstanding/150,0,1)*40+prob*30+np.clip(age/90,0,1)*15+(1-complexity)*15,2); return d
def build_exception_queue(t):
    a=t['accessions'].merge(t['work_queue'],on='accession_id').merge(t['payers'][['payer_id','payer_name','line_of_business']],on='payer_id').merge(t['tests'],on='test_code'); return a.merge(validate_diagnoses(t['accessions']),on='accession_id').merge(detect_duplicates(t['accessions']),on='accession_id')
def data_quality_checks(t):
    return {'duplicate_accession_ids':int(t['accessions'].accession_id.duplicated().sum()),'duplicate_claim_ids':int(t['claims'].claim_id.duplicated().sum()),'negative_financial_values':int((t['claims'][['charge_amount','allowed_amount','expected_reimbursement','payment_amount']]<0).sum().sum()),'recovery_over_denied':int((t['denials'].recovered_amount>t['denials'].denied_amount).sum()),'unknown_payers':int((~t['accessions'].payer_id.isin(t['payers'].payer_id)).sum()),'unknown_tests':int((~t['accessions'].test_code.isin(t['tests'].test_code)).sum())}
def run_analytics(data_dir=DATA_DIR,output_dir=ANALYTICS_DIR):
    t=load_tables(data_dir); output_dir.mkdir(parents=True,exist_ok=True); f=claim_fact(t); q=build_exception_queue(t); rec=recovery_opportunities(f); metrics=kpis(f); dq=data_quality_checks(t); f.to_csv(output_dir/'claim_fact.csv',index=False); q.to_csv(output_dir/'exception_queue.csv',index=False); rec.to_csv(output_dir/'recovery_opportunities.csv',index=False); pd.DataFrame([metrics]).to_csv(output_dir/'revenue_metrics.csv',index=False); pd.DataFrame([dq]).to_csv(output_dir/'data_quality.csv',index=False); return {'fact':f,'queue':q,'recovery':rec,'metrics':metrics,'data_quality':dq}
if __name__=='__main__':
    r=run_analytics(); print(f"Claims {r['metrics']['total_claims']:,} Denial rate {r['metrics']['denial_rate']:.1%}")
