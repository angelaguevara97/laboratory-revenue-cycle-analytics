# Laboratory Revenue Cycle Analytics

An enterprise style healthcare revenue cycle portfolio platform built with Python, pandas, SQLite, Streamlit, Plotly, pytest, and GitHub Actions.

## Live Project

**[Open the Live Interactive Dashboard](https://angel-guevara-revenue-cycles.streamlit.app/)**

The application models 25,000 synthetic laboratory accessions and follows billing activity through validation, claim submission, denial analysis, operational follow up, and revenue recovery.

> **Independent portfolio simulation.** This project is not affiliated with Quest Diagnostics, any insurer, or any healthcare organization. All patient identifiers, claims, financial amounts, payer behavior, denial rates, filing limits, recovery outcomes, and operational results are synthetic. Real payer names are used only as recognizable categorical labels and do not represent actual payer performance or policy.

## Business Problem

Laboratory revenue cycle teams need to understand not only how many claims are denied, but where financial exposure is concentrated, which operational exceptions require attention, whether elevated denial volume is driven by claim volume or denial rate, and which recovery opportunities deserve priority.

This project demonstrates those workflows in a reproducible synthetic environment.

## Analytics Workspace

The Streamlit application contains seven principal pages.

1. **Executive Overview** with claim volume, denial rate, billed dollars, denied dollars, recovered dollars, recovery rate, monthly trends, franchise exposure, payer exposure, and test level exposure.
2. **Regional & Provider Analytics** with region and provider call point comparisons, heatmaps, and monthly trends.
3. **Franchise Performance** with clinical franchise and laboratory test ranking by denial frequency, denial rate, and denied dollars.
4. **Diagnosis Code Analytics** with ICD 10 CM analysis focused specifically on simulated diagnosis related denials. A diagnosis code appearing on a denied claim is not automatically treated as the cause.
5. **Payer Performance & Denial Analytics** with claim counts, normalized denial rates, denied dollars, payer comparisons, and small sample warnings.
6. **Billing Exceptions & Work Queues** with operational status, exception aging, filing urgency, financial exposure, and priority scoring.
7. **Revenue Recovery Opportunities** with denied balances, projected recoverability, realized synthetic recoveries, and transparent opportunity scoring.

## Analytical Drilldown

The model supports analysis across the following dimensions.

**Region → Provider Call Point → Clinical Franchise → Laboratory Test → Payer → Diagnosis Code**

Global filters keep KPI cards, charts, and tables synchronized across the selected population.

## Synthetic Data Model

The generator uses a fixed random seed for reproducibility and creates related tables for patients, client accounts, providers, payers, laboratory tests, diagnoses, accessions, eligibility, claims, denials, work queues, and claim history.

Client accounts retain consistent region and provider call point assignments. Claims are modeled separately from accessions to reduce double counting risk. Laboratory tests are mapped to clinical franchises and clinically plausible diagnosis examples. Payers include parent organization, operating plan, line of business, and synthetic filing parameters.

The modeled lines of business include Commercial, Medicare Advantage, Medicaid Managed Care, Traditional Medicare, and Traditional Medicaid.

## Revenue Cycle Controls

The analytics layer includes controls for missing or malformed diagnosis information, simulated documentation review, eligibility issues, subscriber mismatches, authorization exceptions, duplicate review, filing urgency, financial exposure, and recovery prioritization.

The project never recommends adding an unsupported diagnosis code to obtain reimbursement. Missing diagnosis information routes to provider clarification. Malformed values route to coding or data correction. Simulated medical necessity or documentation scenarios route to documentation review.

## Metric Definitions

**Denial rate** is denied claims divided by submitted claims in the selected population.

**Denied dollars** are the synthetic expected reimbursement associated with denied claims.

**Recovery rate** is recovered synthetic dollars divided by eligible denied dollars.

**Estimated recoverable dollars** are projected values based on synthetic historical recovery behavior. They are displayed separately from realized synthetic recoveries.

## Data Quality and Testing

Automated tests validate reproducibility, unique identifiers, sensible financial relationships, recovery amounts that do not exceed denied balances, consistent client geography, claim count reconciliation, and prevention of claim double counting.

GitHub Actions runs the pytest suite on repository changes.

## Technology Stack

- Python
- pandas
- NumPy
- SQLite
- Streamlit
- Plotly
- pytest
- GitHub Actions

## Project Structure

```text
dashboard/app.py              Streamlit and Plotly analytics application
src/generate_data.py          Reproducible synthetic data generator
src/analytics_engine.py       Validation, KPI, filtering, and opportunity logic
database/schema.sql           Relational SQLite schema
tests/                        Automated data and analytics tests
docs/                         Case study and methodology documentation
data/                         Synthetic sample and generated data outputs
```

## Run Locally

```bash
python -m pip install -r requirements.txt
python src/generate_data.py
python src/analytics_engine.py
streamlit run dashboard/app.py
```

The dashboard can also initialize the synthetic dataset automatically when generated analytics files are not present.

## Portfolio Skills Demonstrated

Healthcare revenue cycle analytics, laboratory billing, claim denial management, ICD 10 CM analysis, payer analytics, Python, pandas, SQL, SQLite, Streamlit, Plotly, data modeling, financial opportunity analysis, operational workflow analytics, data validation, automated testing, and dashboard development.

## Data and Privacy

No protected health information, real patient records, proprietary laboratory data, payer contracts, actual insurer denial statistics, or actual reimbursement policies are included. The project is designed strictly as an educational and portfolio demonstration.

## Author

Angel Guevara
