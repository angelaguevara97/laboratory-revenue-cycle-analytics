# Laboratory Revenue Cycle Analytics Case Study

## Business problem

Laboratory billing depends on accurate information moving from the clinical order into the billing process. Missing diagnosis information, inactive coverage, subscriber errors, documentation gaps, duplicate submissions, and unresolved denials can delay reimbursement or create avoidable revenue loss.

The operational challenge is not simply finding errors. A revenue cycle team also needs to decide which exceptions should be worked first, what information is needed to resolve them, whether a claim is truly duplicative, how much money is at risk, and whether corrective work produced payment.

## Project objective

Build a public and reproducible simulation that demonstrates the data relationships behind laboratory billing and creates a foundation for exception detection, queue management, denial analysis, and revenue recovery.

## Phase 1

The project foundation defines separate relational tables for patients, providers, fictional payers, accessions, eligibility checks, claims, denials, work queue items, and claim history.

This design allows analysis at both the laboratory service level and the claim level. It also creates an audit trail for later workflow modules.

## Phase 2

A Python and pandas generator creates 25,000 synthetic laboratory accessions. It also creates related patient, provider, payer, eligibility, claim, denial, queue, and history records.

The generator deliberately introduces controlled data quality and billing issues so later modules can detect them. Examples include missing diagnosis information, malformed diagnosis values, inactive eligibility, subscriber mismatches, missing simulated authorization, possible duplicate service patterns, and synthetic denials.

A fixed random seed makes the output reproducible.

## Financial design

The simulation separates gross charges, allowed amounts, expected reimbursement, actual payment, denied amount, and recovered amount. This makes it possible to analyze revenue at risk without treating the original charge as guaranteed revenue.

## Compliance design

All people, payers, accessions, and claims are synthetic. The project does not use protected health information or proprietary laboratory data.

Diagnosis validation is separated from medical necessity. A missing or malformed diagnosis can be identified as a data quality problem, but the system does not invent a diagnosis or recommend changing documentation to obtain payment.

Simulated filing limits and future simulated coverage rules are labeled as modeling assumptions rather than real payer requirements.

## Current result

The project now has a reproducible data foundation that can support billing exception rules, duplicate review, timely filing calculations, provider follow up queues, denial analytics, and a Streamlit dashboard in later phases.

## Limitations

This is not a production claim adjudication system.

Synthetic rates are not industry benchmarks.

The model does not establish real payer coverage.

The model does not determine clinical diagnoses.

The model simplifies many details of eligibility, claim formatting, coordination of benefits, remittance processing, appeals, patient responsibility, and payer contracts.

Those limitations are intentional. The goal is to demonstrate revenue cycle reasoning and analytics while keeping the portfolio safe, explainable, and publicly shareable.
