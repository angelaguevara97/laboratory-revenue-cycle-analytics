# Interview Guide

## Thirty second explanation

I built a synthetic laboratory revenue cycle analytics project to understand how a laboratory service moves from accession through billing and reimbursement. I designed a relational SQLite model and a Python generator that creates 25,000 reproducible synthetic accessions plus eligibility, claim, denial, and work queue records. I intentionally included billing exceptions so I can build and test rules for prevention, prioritization, denial management, and revenue recovery. All records and payer policies are simulated.

## Why use synthetic data

Healthcare billing data can contain protected health information and proprietary operational details. Synthetic data lets me demonstrate the workflow publicly without exposing patient or employer data. It also lets me control known exception scenarios and test whether my logic finds them.

## Why use separate tables

Patients, accessions, claims, denials, and queue activity represent different business events. Keeping them separate reduces duplication and mirrors relational database design. Keys connect the events so I can follow one service through the revenue cycle.

## What is an accession

An accession is the laboratory service record created around the specimen and testing event. In this project it connects the patient, ordering provider, payer, service date, test code, diagnosis information, and charge before the claim is created.

## Charge versus allowed amount versus expected reimbursement versus payment

Charge is the gross billed amount.

Allowed amount is the amount recognized under the simulated payer arrangement.

Expected reimbursement is what the model expects to collect after simulated adjustments.

Payment is what was actually received in the generated adjudication outcome.

Separating these amounts prevents overstating revenue at risk.

## What does a denial mean in the project

A denial is a generated claim outcome that prevents initial payment. Denials are categorized for operational analysis. The current reason labels are intentionally synthetic rather than pretending that invented values are real CARCs or RARCs.

## Why use a fixed random seed

A fixed seed makes the synthetic dataset reproducible. If the same version of the generator is run twice with the same record count, the same records are produced. That gives later tests a stable baseline.

## What are the current limitations

The project does not reproduce a real laboratory billing platform or payer contract. It simplifies claim adjudication and does not determine actual coverage or medical necessity. The synthetic error and denial rates are modeling choices rather than industry benchmarks.

## Likely technical questions

### Why pandas

pandas is useful for generating, transforming, joining, validating, and summarizing tabular billing data. It also makes the logic readable during development.

### Why SQLite

SQLite provides a real relational database without requiring a database server. It lets the project demonstrate SQL relationships and persistence while remaining easy for a recruiter to run locally.

### Why Streamlit later

Streamlit will provide an interactive operations dashboard without hiding the underlying Python analysis. Recruiters will be able to filter queues, inspect denial trends, and review revenue metrics.

### How do you know the financial values are sensible

Automated tests verify relationships such as allowed amount not exceeding gross charge and expected reimbursement not exceeding allowed amount. Tests also verify identifier uniqueness, relational references, requested record counts, and reproducibility.

## Strong limitation statement

I built this as an educational revenue cycle simulation. I would not use the synthetic coverage rules to make a real billing decision. In a production environment I would validate logic against current official coding guidance, the applicable payer policy, organizational procedures, and qualified billing or coding review.
