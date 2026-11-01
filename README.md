# Laboratory Revenue Cycle Analytics

A complete portfolio simulation of laboratory revenue cycle operations using synthetic data, Python, pandas, SQLite, and Streamlit.

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

## Revenue Cycle Flow

Provider order → specimen collection → accession → prebill validation → claim submission → payer adjudication → payment or denial → follow up → correction or appeal → recovery

An accession represents the laboratory testing event. A claim represents the billing transaction associated with that service. Keeping these concepts separate makes it possible to analyze both laboratory operations and reimbursement activity.

## Project Structure

`src/generate_data.py` creates the synthetic population and SQLite database.

`src/analytics_engine.py` performs diagnosis validation, eligibility review, duplicate detection, timely filing calculations, queue prioritization, and revenue recovery metrics.

`src/run_project.py` runs the complete data and analytics workflow.

`dashboard/app.py` provides the interactive Streamlit application.

`database/schema.sql` defines the relational SQLite structure.

`tests` contains automated tests for data generation and analytics logic.

`docs` contains methodology, the data dictionary, case study, interview guide, and interview presentation.

`data/sample_accessions.csv`, `data/sample_claims.csv`, and `data/sample_denials.csv` provide small examples that can be reviewed directly on GitHub.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_project.py
streamlit run dashboard/app.py
```

The project runner creates 25,000 accessions, related revenue cycle tables, the SQLite database, and analytics outputs.

## Diagnosis and Medical Necessity Controls

Diagnosis validation separates three different problems.

**Missing diagnosis:** The record is routed for provider clarification.

**Malformed diagnosis:** The record is routed for coding or data correction.

**Simulated policy review:** A valid diagnosis and test combination does not satisfy an educational simulation rule, so the record is routed for documentation review.

The program never invents a diagnosis and never recommends changing a diagnosis solely to obtain payment. The simulated coverage combinations are not real payer policies.

## Duplicate Review

Exact matching uses patient, service date, test code, and provider. Near matching identifies the same patient and test within a short period. A match creates a manual review signal rather than an automatic rejection because repeat testing, corrected claims, and separate services can be legitimate.

## Timely Filing and Prioritization

Fictional payers have clearly labeled simulated filing limits. The engine calculates remaining days and combines filing urgency, financial exposure, and estimated resolvability into a priority score. This demonstrates how an operations team can focus limited follow up capacity on work with greater revenue risk.

## Denial and Recovery Analytics

The project calculates:

* Claim denial rate
* Denied dollars
* Revenue recovered
* Recovery rate
* Average days to resolution
* Gross charges
* Allowed amounts
* Expected reimbursement
* Actual payments

The distinction between gross charges and expected reimbursement prevents the project from treating every billed dollar as collectible revenue.

## Dashboard

The Streamlit dashboard includes four views.

**Executive Overview** summarizes claim volume, denial rate, recovery, reimbursement, payments, and open revenue risk.

**Billing Exception Queue** provides filters for priority and status and displays operational follow up details.

**Denial Management** summarizes denied dollars, recovery, denial categories, and resolution outcomes.

**Validation Quality** shows diagnosis exceptions, eligibility exceptions, and duplicate review signals.

## Data and Privacy

All records are synthetic. The project contains no protected health information. Patient identifiers, providers, payers, financial arrangements, filing limits, authorization logic, and outcomes are generated for educational purposes.

A fixed random seed makes the dataset reproducible so changes to analytical rules can be tested against a stable population.

## Public Healthcare Context

Clinical laboratory reimbursement involves procedure coding, diagnosis information, payer adjudication, remittance information, and follow up workflows. CMS publishes the Clinical Laboratory Fee Schedule and laboratory billing resources. CMS also explains that electronic remittance advice communicates claim adjudication and payment adjustments using standardized adjustment and remark code concepts.

This portfolio project uses those concepts as background while keeping its operational rules and financial assumptions explicitly simulated.

## Limitations

This application is not production billing software. Real deployment would require current validated code sets, payer specific coverage and authorization policies, contractual reimbursement logic, security controls, audit logging, privacy safeguards, regulatory review, and integration with laboratory and billing systems.

## Author

Angel Guevara
