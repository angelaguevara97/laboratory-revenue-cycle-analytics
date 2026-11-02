# Laboratory Revenue Cycle Analytics

A portfolio simulation of laboratory revenue cycle operations using synthetic data, Python, pandas, SQLite, and Streamlit.

## Live Project

**[Open the Live Interactive Dashboard](https://angel-guevara-revenue-cycles.streamlit.app/)**

The live dashboard lets reviewers explore the finished project without downloading code or running Python locally.

## Project Summary

This project models how a clinical laboratory can identify billing exceptions before claim submission, organize provider follow up, detect possible duplicate billing, prioritize timely filing risk, analyze denials, and measure revenue recovery.

The application generates 25,000 synthetic laboratory accessions and follows related activity through eligibility validation, claim submission, adjudication, denial review, and recovery analytics.

This is an educational simulation. It does not reproduce the systems, data, policies, workflows, performance, payer contracts, or internal practices of Quest Diagnostics or any other laboratory.

## What the System Does

1. Generates a reproducible synthetic laboratory billing population.
2. Validates missing and malformed diagnosis information.
3. Applies clearly labeled simulated medical necessity review rules.
4. Identifies eligibility, subscriber, and authorization exceptions.
5. Detects exact and near duplicate signals for manual review.
6. Calculates simulated timely filing deadlines.
7. Prioritizes billing exceptions using urgency, financial exposure, and resolvability.
8. Produces compliant provider clarification messages that request accurate documentation.
9. Tracks claim denials, resolution outcomes, and recovered revenue.
10. Separates gross charges, allowed amounts, expected reimbursement, actual payments, denied dollars, and recovered dollars.
11. Presents operational and financial metrics in an interactive Streamlit dashboard.

## Dashboard Views

- **Executive Overview:** claim volume, denial rate, recovery, reimbursement, payments, and open revenue risk.
- **Billing Exception Queue:** filters for priority and status with operational follow up details.
- **Denial Management:** denied dollars, recovery, denial categories, and resolution outcomes.
- **Validation Quality:** diagnosis exceptions, eligibility exceptions, and duplicate review signals.

## Revenue Cycle Flow

Provider order → specimen collection → accession → prebill validation → claim submission → payer adjudication → payment or denial → follow up → correction or appeal → recovery

## Project Structure

- `src/generate_data.py` creates the synthetic population and SQLite database.
- `src/analytics_engine.py` performs validation, duplicate detection, timely filing calculations, queue prioritization, and revenue recovery metrics.
- `src/run_project.py` runs the complete workflow.
- `dashboard/app.py` provides the Streamlit application.
- `database/schema.sql` defines the relational SQLite structure.
- `tests` contains automated tests for data generation and analytics logic.
- `docs` contains methodology, the data dictionary, case study, interview guide, and presentation.
- `data/sample_accessions.csv`, `data/sample_claims.csv`, and `data/sample_denials.csv` provide small reviewable examples.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_project.py
streamlit run dashboard/app.py
```

## Analytical Controls

Missing diagnosis information is routed for provider clarification rather than invented. Malformed diagnosis information is routed for coding or data correction. Simulated policy-review cases are routed for documentation review. Duplicate matches create manual review signals rather than automatic rejection because legitimate repeat testing and corrected claims can occur.

Fictional payers use clearly labeled simulated filing limits. Priority scoring combines filing urgency, financial exposure, and estimated resolvability.

## Metrics

The project calculates claim denial rate, denied dollars, revenue recovered, recovery rate, average resolution time, gross charges, allowed amounts, expected reimbursement, and actual payments.

## Data and Privacy

All records are synthetic. The project contains no protected health information. Patient identifiers, providers, payers, financial arrangements, filing limits, authorization logic, and outcomes are generated for educational purposes.

## Limitations

This application is not production billing software. Real deployment would require validated code sets, payer-specific policies, contractual reimbursement logic, security controls, audit logging, privacy safeguards, regulatory review, and integration with laboratory and billing systems.

## Author

Angel Guevara
