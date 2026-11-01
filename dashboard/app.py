from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "generated"
ANALYTICS = ROOT / "data" / "analytics"

st.set_page_config(page_title="Laboratory Revenue Cycle Analytics", page_icon="🧪", layout="wide")
st.title("Laboratory Revenue Cycle Analytics")
st.caption("Synthetic educational simulation. No patient data, payer contract data, or proprietary laboratory data is used.")

required = [ANALYTICS / "exception_queue.csv", ANALYTICS / "revenue_metrics.csv", DATA / "claims.csv", DATA / "denials.csv"]
if not all(path.exists() for path in required):
    st.error("Project data has not been generated. Run: python src/run_project.py")
    st.stop()

queue = pd.read_csv(ANALYTICS / "exception_queue.csv")
metrics = pd.read_csv(ANALYTICS / "revenue_metrics.csv").iloc[0]
claims = pd.read_csv(DATA / "claims.csv")
denials = pd.read_csv(DATA / "denials.csv")
diagnosis = pd.read_csv(ANALYTICS / "diagnosis_validation.csv")
eligibility = pd.read_csv(ANALYTICS / "eligibility_validation.csv")
duplicates = pd.read_csv(ANALYTICS / "duplicate_review.csv")

page = st.sidebar.radio("View", ["Executive Overview", "Billing Exception Queue", "Denial Management", "Validation Quality"])

if page == "Executive Overview":
    st.subheader("Revenue Cycle Performance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Claims submitted", f"{int(metrics['claims_submitted']):,}")
    c2.metric("Denial rate", f"{metrics['denial_rate']:.1%}")
    c3.metric("Revenue recovered", f"${metrics['recovered_dollars']:,.0f}")
    c4.metric("Recovery rate", f"{metrics['recovery_rate']:.1%}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Gross charges", f"${metrics['gross_charges']:,.0f}")
    c6.metric("Expected reimbursement", f"${metrics['expected_reimbursement']:,.0f}")
    c7.metric("Actual payments", f"${metrics['actual_payments']:,.0f}")
    c8.metric("Average resolution days", f"{metrics['average_resolution_days']:.1f}")

    st.subheader("Open Revenue Risk")
    active = queue[queue["queue_status"].isin(["Open", "Escalated"])]
    st.metric("Exception revenue at risk", f"${active['revenue_at_risk'].sum():,.0f}")
    st.bar_chart(queue["priority"].value_counts())

elif page == "Billing Exception Queue":
    st.subheader("Prioritized Billing Exceptions")
    priorities = st.multiselect("Priority", sorted(queue["priority"].dropna().unique()), default=sorted(queue["priority"].dropna().unique()))
    statuses = st.multiselect("Status", sorted(queue["queue_status"].unique()), default=sorted(queue["queue_status"].unique()))
    filtered = queue[queue["priority"].isin(priorities) & queue["queue_status"].isin(statuses)]
    st.metric("Filtered revenue at risk", f"${filtered['revenue_at_risk'].sum():,.0f}")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

elif page == "Denial Management":
    st.subheader("Denial and Recovery Analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Denied claims", f"{int(metrics['denied_claims']):,}")
    c2.metric("Denied dollars", f"${metrics['denied_dollars']:,.0f}")
    c3.metric("Recovered dollars", f"${metrics['recovered_dollars']:,.0f}")
    st.bar_chart(denials.groupby("denial_category")["denied_amount"].sum().sort_values(ascending=False))
    status = denials.groupby("resolution_status").agg(claims=("claim_id", "count"), denied_amount=("denied_amount", "sum"), recovered_amount=("recovered_amount", "sum")).reset_index()
    st.dataframe(status, use_container_width=True, hide_index=True)

else:
    st.subheader("Prebill Validation Quality")
    c1, c2, c3 = st.columns(3)
    c1.metric("Diagnosis exceptions", f"{(diagnosis['diagnosis_result'] != 'Pass').sum():,}")
    c2.metric("Eligibility exceptions", f"{(eligibility['eligibility_result'] != 'Pass').sum():,}")
    c3.metric("Duplicate review signals", f"{(duplicates['duplicate_review_status'] == 'Manual review').sum():,}")
    st.write("Diagnosis validation")
    st.bar_chart(diagnosis["diagnosis_result"].value_counts())
    st.write("Eligibility validation")
    st.bar_chart(eligibility["eligibility_result"].value_counts())
    st.write("Duplicate review")
    st.bar_chart(duplicates["duplicate_result"].value_counts())

st.divider()
st.caption("All policies, payer names, financial arrangements, authorization logic, filing limits, and outcomes are simulated for portfolio education.")
