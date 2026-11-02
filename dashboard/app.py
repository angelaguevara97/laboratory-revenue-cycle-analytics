from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.generate_data import build_dataset,write_outputs
from src.analytics_engine import run_analytics,load_tables,claim_fact,filter_fact,kpis,grouped_metrics,diagnosis_analytics,recovery_opportunities,build_exception_queue
DATA=ROOT/'data'/'generated'; ANALYTICS=ROOT/'data'/'analytics'
st.set_page_config(page_title='Laboratory Revenue Cycle Analytics',page_icon='🧪',layout='wide',initial_sidebar_state='expanded')
st.markdown("""<style>.block-container{padding-top:1.4rem;max-width:1550px}.stMetric{background:#fff;border:1px solid #dce4df;border-radius:10px;padding:12px}.synthetic{background:#E8F3EC;border-left:5px solid #00843D;padding:10px 14px;border-radius:6px;color:#333}[data-testid='stSidebar']{background:#F5F7F8}</style>""",unsafe_allow_html=True)
if not (ANALYTICS/'claim_fact.csv').exists():
    with st.spinner('Preparing synthetic enterprise revenue cycle data'):
        write_outputs(build_dataset(25_000)); run_analytics()
t=load_tables(); fact=claim_fact(t); queue=build_exception_queue(t)
st.title('Laboratory Revenue Cycle Analytics')
st.markdown('<div class="synthetic"><b>Independent portfolio simulation.</b> All patient, claim, financial, payer performance, denial behavior, filing limits, and recovery outcomes are synthetic. Real payer names are categorical labels only and do not represent actual insurer performance.</div>',unsafe_allow_html=True)
PAGES=['Executive Overview','Regional & Provider Analytics','Franchise Performance','Diagnosis Code Analytics','Payer Performance & Denial Analytics','Billing Exceptions & Work Queues','Revenue Recovery Opportunities']; page=st.sidebar.radio('Analytics workspace',PAGES); st.sidebar.markdown('### Global Filters')
def choices(label,col): return st.sidebar.multiselect(label,sorted(fact[col].dropna().astype(str).unique().tolist()))
regions=choices('Region','region'); calls=choices('Provider Call Point','call_point'); franchises=choices('Clinical Franchise','franchise'); tests=choices('Lab Test','test_name'); payers=choices('Payer','payer_name'); lob=choices('Line of Business','line_of_business'); dx=choices('Diagnosis Code','diagnosis_code'); denial=choices('Denial Category','denial_category')
f=filter_fact(fact,{'region':regions,'call_point':calls,'franchise':franchises,'test_name':tests,'payer_name':payers,'line_of_business':lob,'diagnosis_code':dx,'denial_category':denial})
def money(x): return f'${x:,.0f}'
LABELS={'payer_name':'Payer','test_name':'Lab Test','franchise':'Clinical Franchise','call_point':'Provider Call Point','line_of_business':'Line of Business','diagnosis_code':'Diagnosis Code','diagnosis_description':'Diagnosis Description','denial_category':'Denial Category','denied_dollars':'Denied Dollars','billed_dollars':'Billed Dollars','recovered_dollars':'Recovered Dollars','denial_rate':'Denial Rate','recovery_rate':'Recovery Rate','total_claims':'Total Claims','denied_claims':'Denied Claims','financial_exposure':'Financial Exposure','estimated_recoverable':'Estimated Recoverable','denied_claim_count':'Denied Claim Count','priority_score':'Priority Score','exception_type':'Exception Type','queue_status':'Queue Status','exception_age_days':'Exception Age Days','days_to_filing':'Days to Filing','diagnosis_action':'Diagnosis Action','accession_id':'Accession ID','month':'Month','region':'Region','exceptions':'Exceptions'}
def label(col): return LABELS.get(col,col.replace('_',' ').title())
def metric_row(m):
    c=st.columns(4); c[0].metric('Total submitted claims',f"{m['total_claims']:,}"); c[1].metric('Denied claims',f"{m['denied_claims']:,}"); c[2].metric('Denial rate',f"{m['denial_rate']:.1%}"); c[3].metric('Denied dollars',money(m['denied_dollars'])); c=st.columns(4); c[0].metric('Billed dollars',money(m['billed_dollars'])); c[1].metric('Recovered dollars',money(m['recovered_dollars'])); c[2].metric('Recovery rate',f"{m['recovery_rate']:.1%}"); c[3].metric('Open billing exceptions',f"{len(queue[~queue.queue_status.eq('Resolved')]):,}")
def value_format(col):
    if col in {'denial_rate','recovery_rate'}: return '.1%'
    if col in {'denied_dollars','billed_dollars','recovered_dollars','financial_exposure','estimated_recoverable','outstanding','denied_amount','charge_amount','expected_reimbursement','payment_amount'}: return '$,.0f'
    if col in {'total_claims','denied_claims','claims','denials','exceptions','denied_claim_count'}: return ',d'
    return ',.0f'
def polish(fig,x,y):
    fig.update_xaxes(title=label(x))
    fig.update_yaxes(title=label(y),tickformat=value_format(y))
    if y in {'denial_rate','recovery_rate'}: fig.update_yaxes(tickformat='.1%')
    return fig
def bar(df,x,y,title):
    if df.empty: st.info('No records match the current filters.'); return
    fig=px.bar(df,x=x,y=y,title=title,color_discrete_sequence=['#00843D'],text_auto=value_format(y)); polish(fig,x,y); fig.update_traces(textposition='outside',cliponaxis=False); fig.update_layout(height=410,margin=dict(l=10,r=10,t=50,b=70)); st.plotly_chart(fig,use_container_width=True)
def line(df,x,y,title):
    if df.empty:return
    fig=px.line(df,x=x,y=y,markers=True,title=title,color_discrete_sequence=['#00843D']); polish(fig,x,y); fig.update_layout(height=360,margin=dict(l=10,r=10,t=50,b=40)); st.plotly_chart(fig,use_container_width=True)
def monthly(frame):
    g=frame.groupby('month').agg(total_claims=('claim_id','nunique'),denied_claims=('is_denied','sum'),denied_dollars=('denied_amount','sum')).reset_index(); g['denial_rate']=g.denied_claims/g.total_claims; return g
def format_table(df):
    formats={}
    for col in df.columns:
        if col in {'denial_rate','recovery_rate'}: formats[col]='{:.1%}'
        elif col in {'denied_dollars','billed_dollars','recovered_dollars','financial_exposure','estimated_recoverable','outstanding','denied_amount','charge_amount','expected_reimbursement','payment_amount'}: formats[col]='${:,.0f}'
        elif col in {'priority_score','resolution_probability'}: formats[col]='{:.1f}'
        elif pd.api.types.is_integer_dtype(df[col]): formats[col]='{:,.0f}'
    return df.rename(columns={c:label(c) for c in df.columns}).style.format({label(k):v for k,v in formats.items()},na_rep='')
m=kpis(f)
if page=='Executive Overview':
    st.header('Laboratory Revenue Cycle | Executive Overview'); metric_row(m); a,b=st.columns(2)
    with a: line(monthly(f),'month','denial_rate','Monthly Denial Rate')
    with b: line(monthly(f),'month','denied_dollars','Monthly Denied Dollars')
    a,b=st.columns(2)
    with a: bar(grouped_metrics(f,'franchise').sort_values('denied_dollars',ascending=False),'franchise','denied_dollars','Denied Dollars by Clinical Franchise')
    with b: bar(grouped_metrics(f,'region'),'region','denial_rate','Denial Rate by Region')
    a,b=st.columns(2)
    with a: bar(grouped_metrics(f,'payer_name').nlargest(10,'denied_dollars'),'payer_name','denied_dollars','Top Payers by Denied Dollars')
    with b: bar(grouped_metrics(f,'test_name').nlargest(10,'denied_dollars'),'test_name','denied_dollars','Top Lab Tests by Denied Dollars')
elif page=='Regional & Provider Analytics':
    st.header('Regional & Provider Analytics'); metric_row(m); a,b=st.columns(2)
    with a: bar(grouped_metrics(f,'region'),'region','denial_rate','Denial Rate by Region')
    with b: bar(grouped_metrics(f,'call_point').sort_values('denied_dollars',ascending=False),'call_point','denied_dollars','Denied Dollars by Provider Call Point')
    heat=f.groupby(['region','call_point']).agg(claims=('claim_id','nunique'),denials=('is_denied','sum')).reset_index(); heat['denial_rate']=heat.denials/heat.claims; fig=px.density_heatmap(heat,x='call_point',y='region',z='denial_rate',color_continuous_scale=[[0,'#E8F3EC'],[1,'#00843D']],title='Region and Provider Call Point Denial Heatmap'); fig.update_coloraxes(colorbar_tickformat='.1%',colorbar_title='Denial Rate'); fig.update_xaxes(title='Provider Call Point'); fig.update_yaxes(title='Region'); st.plotly_chart(fig,use_container_width=True); line(monthly(f),'month','denial_rate','Monthly Denial Trend')
elif page=='Franchise Performance':
    st.header('Franchise Performance'); metric_row(m); rank=st.selectbox('Rank Lab Tests by',['denied_dollars','denial_rate','denied_claims'],format_func=lambda x:label(x)); gm=grouped_metrics(f,'test_name').sort_values(rank,ascending=False).head(10); bar(gm,'test_name',rank,f"Top Lab Tests by {label(rank)}"); a,b=st.columns(2)
    with a: bar(grouped_metrics(f,'franchise'),'franchise','denial_rate','Denial Rate by Clinical Franchise')
    with b: bar(grouped_metrics(f,'payer_name').nlargest(12,'denied_dollars'),'payer_name','denied_dollars','Payer Exposure')
    detail=f.groupby(['franchise','test_name','payer_name','diagnosis_code'],dropna=False).agg(claims=('claim_id','nunique'),denied=('is_denied','sum'),denied_dollars=('denied_amount','sum')).reset_index(); st.dataframe(format_table(detail),use_container_width=True,hide_index=True)
elif page=='Diagnosis Code Analytics':
    st.header('Diagnosis Code Analytics'); metric_row(m); st.caption('Diagnosis codes on denied claims are not automatically treated as the cause. Diagnosis related metrics use the synthetic denial reason classification.'); dxm=diagnosis_analytics(f)
    if not dxm.empty:
        a,b=st.columns(2)
        with a: bar(dxm.nlargest(20,'denied_claims'),'diagnosis_code','denied_claims','Diagnosis Related Denials by Claim Count')
        with b: bar(dxm.nlargest(20,'denied_dollars'),'diagnosis_code','denied_dollars','Diagnosis Related Denied Dollars')
        view=dxm[['diagnosis_code','diagnosis_description','total_claims','denied_claims','denial_rate','denied_dollars']].sort_values('denied_dollars',ascending=False); st.dataframe(format_table(view),use_container_width=True,hide_index=True); st.download_button('Export Diagnosis Analysis CSV',dxm.to_csv(index=False),'diagnosis_analysis.csv','text/csv')
elif page=='Payer Performance & Denial Analytics':
    st.header('Payer Performance & Denial Analytics'); metric_row(m); pg=grouped_metrics(f,'payer_name'); pg['sample_warning']=pg.total_claims.lt(100); a,b=st.columns(2)
    with a: bar(pg.nlargest(15,'denied_dollars'),'payer_name','denied_dollars','Top Payers by Denied Dollars')
    with b: bar(pg.sort_values('denial_rate',ascending=False),'payer_name','denial_rate','Denial Rate by Payer')
    selected=st.multiselect('Compare Payers',sorted(f.payer_name.unique()),default=sorted(f.payer_name.unique())[:2],max_selections=4); st.dataframe(format_table(pg[pg.payer_name.isin(selected)]),use_container_width=True,hide_index=True); st.caption('Claim counts are displayed with rates to distinguish high denial volume from elevated denial rate. Comparisons with fewer than 100 claims are flagged as small samples.')
elif page=='Billing Exceptions & Work Queues':
    st.header('Billing Exceptions & Work Queues'); q=queue.copy()
    for col,vals in {'region':regions,'call_point':calls,'franchise':franchises,'payer_name':payers,'line_of_business':lob}.items():
        if vals:q=q[q[col].isin(vals)]
    openq=q[~q.queue_status.eq('Resolved')]; c=st.columns(4); c[0].metric('Open exceptions',f'{len(openq):,}'); c[1].metric('Financial exposure',money(openq.financial_exposure.sum())); c[2].metric('Average exception age',f'{openq.exception_age_days.mean():.1f} days' if len(openq) else '0 days'); c[3].metric('Awaiting provider response',f"{(openq.queue_status=='Awaiting provider response').sum():,}"); a,b=st.columns(2)
    with a: bar(openq.groupby('exception_type',as_index=False).size().rename(columns={'size':'exceptions'}),'exception_type','exceptions','Open Exceptions by Category')
    with b: bar(openq.groupby('payer_name',as_index=False).financial_exposure.sum().nlargest(12,'financial_exposure'),'payer_name','financial_exposure','Financial Exposure by Payer')
    view=openq[['accession_id','payer_name','region','call_point','franchise','test_name','exception_type','queue_status','exception_age_days','days_to_filing','financial_exposure','priority_score','diagnosis_action']].sort_values('priority_score',ascending=False); st.dataframe(format_table(view),use_container_width=True,hide_index=True,height=520)
else:
    st.header('Revenue Recovery Opportunities'); r=recovery_opportunities(f); c=st.columns(4); c[0].metric('Total denied dollars',money(r.denied_amount.sum())); c[1].metric('Estimated recoverable',money(r.estimated_recoverable.sum())); c[2].metric('Recovered dollars',money(r.recovered_amount.sum())); c[3].metric('Outstanding denied balance',money(r.outstanding.sum())); a,b=st.columns(2)
    with a: bar(r.groupby('payer_name',as_index=False).estimated_recoverable.sum().nlargest(12,'estimated_recoverable'),'payer_name','estimated_recoverable','Estimated Recoverable Dollars by Payer')
    with b: bar(r.groupby('franchise',as_index=False).estimated_recoverable.sum(),'franchise','estimated_recoverable','Estimated Recoverable Dollars by Clinical Franchise')
    ranked=r.groupby(['payer_name','franchise','test_name','denial_category'],as_index=False).agg(denied_claim_count=('claim_id','nunique'),denied_dollars=('denied_amount','sum'),estimated_recoverable=('estimated_recoverable','sum'),priority_score=('priority_score','mean')).sort_values('priority_score',ascending=False); st.dataframe(format_table(ranked),use_container_width=True,hide_index=True); st.caption('Projected recoveries are synthetic estimates based on simulated historical outcomes and are shown separately from realized synthetic recoveries.')
st.divider(); st.caption('Synthetic portfolio demonstration. No PHI, proprietary laboratory data, payer contracts, actual insurer denial statistics, or actual reimbursement policies are used.')