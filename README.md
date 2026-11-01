# Laboratory Revenue Cycle Analytics

A portfolio project that simulates laboratory revenue cycle operations using synthetic data, Python, pandas, SQLite, and Streamlit.

## Purpose

This project models how a clinical laboratory can identify billing exceptions before claim submission, organize follow up work, detect possible duplicate billing, monitor timely filing risk, analyze denials, and measure revenue recovery.

The project is designed as an educational simulation of revenue cycle concepts. It does not reproduce the systems, data, policies, workflows, performance, or payer contracts of Quest Diagnostics or any other laboratory.

## Current build status

Phase 1 establishes the project foundation, relational data model, documentation, and local environment.

Phase 2 creates a reproducible synthetic data generator for 25,000 laboratory accessions plus related patients, providers, payers, eligibility checks, claims, denials, and work queue activity.

Later phases will add the billing exception engine, duplicate review logic, queue prioritization, denial analytics, revenue recovery metrics, and Streamlit dashboard.

## Revenue cycle flow represented

1. A provider orders laboratory testing for a patient.
2. The specimen is collected and an accession is created.
3. Patient, insurance, diagnosis, test, and authorization information is checked.
4. Records with missing or questionable information can be held for review.
5. Valid claims are submitted to a payer.
6. The payer adjudicates the claim and returns payment or adjustment information.
7. Denied or underpaid claims can enter a follow up workflow.
8. Resolved claims can produce recovered revenue.

## Data model

The SQLite design separates patients, providers, payers, accessions, eligibility checks, claims, denials, work queue items, and claim history. This makes it possible to follow one laboratory service from accession through claim resolution while preserving the relationships among operational and financial records.

See `docs/data_dictionary.md` for field definitions and `database/schema.sql` for the relational schema.

## Synthetic data

All patient, provider, payer, accession, claim, eligibility, denial, and queue records are synthetic. Names of simulated payers are fictional. Financial amounts and operational rates are generated for demonstration and do not represent industry benchmarks or the performance of any real organization.

The generator intentionally creates a controlled number of incomplete or problematic records. Those records give later modules something realistic to identify and work.

Run:

```bash
python src/generate_data.py
```

The default run creates 25,000 accessions and writes CSV files to `data/generated` plus a SQLite database at `database/lab_revenue_cycle.db`.

A fixed random seed makes the dataset reproducible.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/generate_data.py
```

## Compliance and coding note

Diagnosis information in this project is used for education and data validation only. The application will never recommend inventing a diagnosis or changing a diagnosis solely to obtain payment. Diagnosis assignment depends on accurate provider documentation and applicable coding guidance.

Future medical necessity examples will use clearly labeled simulated coverage policies unless a public policy is explicitly cited. A simulated policy should never be interpreted as a coverage rule for a real payer.

## Technology

Python

pandas

NumPy

SQLite

Streamlit

pytest

## Repository map

`src` contains application and data generation code.

`database` contains the SQLite schema.

`data` contains documentation and small sample outputs. Generated bulk data is excluded from source control.

`tests` contains automated validation tests.

`docs` contains the data dictionary, methodology, case study material, and interview notes.

`dashboard` will contain the Streamlit application in a later phase.

## Public reference concepts

The project uses ICD 10 CM as a diagnosis coding concept and will model electronic remittance concepts such as claim adjustment reason codes and remittance advice remark codes. Any real code set references will be tied to public authoritative guidance. Simulated business rules will always be labeled as simulated.

## Author

Angel Guevara
