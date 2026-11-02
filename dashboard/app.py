from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA = ROOT / "data" / "generated"
ANALYTICS = ROOT / "data" / "analytics"

st.set_page_config(
    page_title="Laboratory Revenue Cycle Analytics",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2.5rem; max-width: 1450px;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(49, 51, 63, 0.12);}
    [data-testid="stMetric"] {
        background: rgba(248, 249, 251, 0.85);
        border: 1px solid rgba(49, 51, 63, 0.10);
        padding: 14px 16px;
        border-radius: 12px;
    }
    [data-testid="stMetricLabel"] {font-weight: 600;}
    div[data-testid="stDataFrame"] {border: 1px solid rgba(49, 51, 63, 0.10); border-radius: 10px; overflow: hidden;}
    .portfolio-note {
        padding: 12px 14px;
        border-radius: 10px;
        background: rgba(248, 249, 251, 0.8);
        border: 1px solid rgba(49, 51, 63, 0.10);
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Laboratory Revenue Cycle Analytics")
st.markdown(
    '<div class="portfolio-note">Synthetic educational simulation • 25,000 laboratory accessions • No patient data, payer contract data, or proprietary laboratory data is used.</div>',
    unsafe_allow_html=True,
)

required = [
    ANALYTICS / "exception_queue.csv",
    ANALYTICS / "revenue_metrics.csv",
    DATA / "claims.csv",
    DATA / "denials.csv",
]
if not all(path.exists() for path in required):
    with st.spinner("Preparing synthetic laboratory revenue cycle data..."):
        try:
            from src.generate_data import build_dataset, write_outputs
            from src.analytics_engine import run_analytics

            tables = build_dataset(25_000)
            write_outputs(tables)
            run_analytics()
        except Exception as exc:
            st.error("The synthetic project data could not be initialized.")
            st.exception(exc)
            st.stop()

if not all(path.exists() for path in required):
    st.error("The synthetic project data was not created successfully.")
    st.stop()

queue = pd.read_csv(ANALYTICS / "exception_queue.csv")
metrics = pd.read_csv(ANALYTICS / "revenue_metrics.csv").iloc[0]
claims = pd.read_csv(DATA / "claims.csv")
denials = pd.read_csv(DATA / "denials.csv")
diagnosis = pd.read_csv(ANALYTICS / "diagnosis_validation.csv")
eligibility = pd.read_csv(ANALYTICS / "eligibility_validation.csv")
duplicates = pd.read_csv(ANALYTICS / "duplicate_review.csv")


def readable_bar_chart(data, category, value, *, height=330, value_format=",.0f"):
    order = data[category].tolist()
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                f"{category}:N",
                sort=order,
                axis=alt.Axis(title=None, labelAngle=0, labelLimit=260, labelPadding=10),
            ),
            y=alt.Y(f"{value}:Q", axis=alt.Axis(title=value, format=value_format)),
            tooltip=[
                alt.Tooltip(f"{category}:N", title=category),
                alt.Tooltip(f"{value}:Q", title=value, format=value_format),
            ],
        )
        .properties(height=height)
    )


st.sidebar.markdown("### Revenue Cycle Dashboard")
st.sidebar.caption("Explore operational performance, billing exceptions, denials, and prebill validation.")
page = st.sidebar.radio(
    "View",
    ["Executive Overview", "Billing Exception Queue", "Denial Management", "Validation Quality"],
)
st.sidebar.divider()
st.sidebar.caption("Portfolio simulation • Synthetic data only")

if page == "Executive Overview":
    st.subheader("Executive Overview")
    st.caption("High-level revenue cycle performance and current exception exposure.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Claims submitted", f"{int(metrics['claims_submitted']):,}")
    c2.metric("Denial rate", f"{metrics['denial_rate']:.1%}")
    c3.metric("Revenue recovered", f"${metrics['recovered_dollars']:,.0f}")
    c4.metric("Recovery rate", f"{metrics['recovery_rate']:.1%}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Gross charges", f"${metrics['gross_charges']:,.0f}")
    c6.metric("Expected reimbursement", f"${metrics['expected_reimbursement']:,.0f}")
    c7.metric("Actual payments", f"${metrics['actual_payments']:,.0f}")
    c8.metric("Avg. resolution days", f"{metrics['average_resolution_days']:.1f}")

    st.markdown("#### Open Revenue Risk")
    active = queue[queue["queue_status"].isin(["Open", "Escalated"])]
    r1, r2, r3 = st.columns(3)
    r1.metric("Exception revenue at risk", f"${active['revenue_at_risk'].sum():,.0f}")
    r2.metric("Open / escalated exceptions", f"{len(active):,}")
    r3.metric("Urgent exceptions", f"{(active['priority'] == 'Urgent').sum():,}")

    priority_counts = queue["priority"].value_counts().rename_axis("Priority").reset_index(name="Exceptions")
    st.markdown("#### Exception Volume by Priority")
    st.altair_chart(readable_bar_chart(priority_counts, "Priority", "Exceptions", height=330), use_container_width=True)

elif page == "Billing Exception Queue":
    st.subheader("Billing Exception Queue")
    st.caption("Prioritized operational work queue for simulated billing follow-up.")

    f1, f2 = st.columns(2)
    with f1:
        priorities = st.multiselect(
            "Priority",
            sorted(queue["priority"].dropna().unique()),
            default=sorted(queue["priority"].dropna().unique()),
        )
    with f2:
        statuses = st.multiselect(
            "Status",
            sorted(queue["queue_status"].dropna().unique()),
            default=sorted(queue["queue_status"].dropna().unique()),
        )

    filtered = queue[queue["priority"].isin(priorities) & queue["queue_status"].isin(statuses)].copy()
    q1, q2, q3 = st.columns(3)
    q1.metric("Filtered exceptions", f"{len(filtered):,}")
    q2.metric("Revenue at risk", f"${filtered['revenue_at_risk'].sum():,.0f}")
    q3.metric("Urgent cases", f"{(filtered['priority'] == 'Urgent').sum():,}")

    preferred = [
        "accession_id", "payer_name", "service_date", "diagnosis_code", "exception_reason",
        "diagnosis_action", "days_to_filing", "filing_deadline", "charge_amount",
        "revenue_at_risk", "priority", "queue_status",
    ]
    display_cols = [col for col in preferred if col in filtered.columns]
    st.dataframe(
        filtered[display_cols],
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config={
            "accession_id": "Accession",
            "payer_name": "Payer",
            "service_date": "Service date",
            "diagnosis_code": "Diagnosis",
            "exception_reason": "Exception",
            "diagnosis_action": "Recommended action",
            "days_to_filing": st.column_config.NumberColumn("Days to filing", format="%d"),
            "filing_deadline": "Filing deadline",
            "charge_amount": st.column_config.NumberColumn("Charge", format="$%.2f"),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue at risk", format="$%.2f"),
            "priority": "Priority",
            "queue_status": "Status",
        },
    )

elif page == "Denial Management":
    st.subheader("Denial Management")
    st.caption("Denial exposure, recovery performance, and resolution outcomes.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Denied claims", f"{int(metrics['denied_claims']):,}")
    c2.metric("Denied dollars", f"${metrics['denied_dollars']:,.0f}")
    c3.metric("Recovered dollars", f"${metrics['recovered_dollars']:,.0f}")
    c4.metric("Recovery rate", f"{metrics['recovery_rate']:.1%}")

    denial_by_category = (
        denials.groupby("denial_category", as_index=False)["denied_amount"]
        .sum()
        .sort_values("denied_amount", ascending=False)
        .rename(columns={"denial_category": "Denial category", "denied_amount": "Denied dollars"})
    )
    st.markdown("#### Denied Dollars by Category")
    denial_chart = (
        alt.Chart(denial_by_category)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            y=alt.Y("Denial category:N", sort="-x", axis=alt.Axis(title=None, labelLimit=300)),
            x=alt.X("Denied dollars:Q", axis=alt.Axis(title="Denied dollars", format="$,.0f")),
            tooltip=[
                alt.Tooltip("Denial category:N", title="Denial category"),
                alt.Tooltip("Denied dollars:Q", title="Denied dollars", format="$,.2f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(denial_chart, use_container_width=True)

    status = (
        denials.groupby("resolution_status")
        .agg(
            Claims=("claim_id", "count"),
            Denied_dollars=("denied_amount", "sum"),
            Recovered_dollars=("recovered_amount", "sum"),
        )
        .reset_index()
        .rename(columns={"resolution_status": "Resolution status"})
    )
    st.markdown("#### Resolution Outcomes")
    st.dataframe(
        status,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Denied_dollars": st.column_config.NumberColumn("Denied dollars", format="$%.2f"),
            "Recovered_dollars": st.column_config.NumberColumn("Recovered dollars", format="$%.2f"),
        },
    )

else:
    st.subheader("Validation Quality")
    st.caption("Prebill validation signals across diagnosis, eligibility, and duplicate review workflows.")

    diagnosis_exceptions = int((diagnosis["diagnosis_result"] != "Pass").sum())
    eligibility_exceptions = int((eligibility["eligibility_result"] != "Pass").sum())
    duplicate_signals = int((duplicates["duplicate_review_status"] == "Manual review").sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Diagnosis exceptions", f"{diagnosis_exceptions:,}")
    c2.metric("Eligibility exceptions", f"{eligibility_exceptions:,}")
    c3.metric("Duplicate review signals", f"{duplicate_signals:,}")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Diagnosis Validation")
        diagnosis_chart = diagnosis["diagnosis_result"].value_counts().rename_axis("Result").reset_index(name="Records")
        st.altair_chart(readable_bar_chart(diagnosis_chart, "Result", "Records", height=330), use_container_width=True)
    with right:
        st.markdown("#### Eligibility Validation")
        eligibility_chart = eligibility["eligibility_result"].value_counts().rename_axis("Result").reset_index(name="Records")
        st.altair_chart(readable_bar_chart(eligibility_chart, "Result", "Records", height=330), use_container_width=True)

    st.markdown("#### Duplicate Review")
    duplicate_chart = duplicates["duplicate_result"].value_counts().rename_axis("Result").reset_index(name="Records")
    st.altair_chart(readable_bar_chart(duplicate_chart, "Result", "Records", height=330), use_container_width=True)

st.divider()
st.caption(
    "Portfolio simulation: all policies, payer names, financial arrangements, authorization logic, filing limits, and outcomes are synthetic and intended for educational demonstration only."
)
