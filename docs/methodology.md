# Methodology

## Objective

The first two phases create a safe and reproducible foundation for studying laboratory revenue cycle operations. The data is synthetic by design so the repository can be shared publicly without patient information or proprietary laboratory data.

## Reproducibility

The generator uses a fixed random seed of 42. Running the generator with the same code and accession count produces the same dataset. This is useful for testing because later billing rules can be evaluated against a stable baseline.

## Synthetic population

The default run creates 25,000 accessions. Patients, ordering providers, fictional payers, laboratory tests, diagnosis concepts, eligibility checks, claims, denials, and queue activity are generated around those accessions.

The generator intentionally creates imperfect records. Examples include missing diagnosis information, malformed diagnosis values, inactive coverage, subscriber mismatches, missing simulated authorization, possible duplicate service patterns, and claim denials.

These rates are modeling choices for the portfolio project. They are not benchmarks for Quest Diagnostics, Medicare, Medicaid, commercial insurance, or the laboratory industry.

## Financial model

Gross charge represents the synthetic billed amount.

Allowed amount represents a synthetic contracted or recognized amount and is generated below the gross charge.

Expected reimbursement represents the amount the simulation expects to collect from the payer after modeled adjustments.

Actual payment represents the generated adjudication outcome. Denied claims initially receive no payment.

Recovered amount represents money obtained after a synthetic denial resolution.

Keeping these values separate prevents a common analytical mistake: treating charges as if they were collectible revenue.

## Diagnosis concepts

The dataset includes a small set of recognizable ICD 10 CM diagnosis concepts and laboratory procedure code concepts for educational realism. Missing and malformed diagnosis values are intentionally generated so later validation rules have test cases.

A valid diagnosis format does not prove medical necessity. Medical necessity depends on the service, documented clinical circumstances, and applicable coverage policy. Later modules will keep format validation separate from simulated medical necessity review.

The project never creates a diagnosis solely to make a claim payable.

## Payer policies

Payer names and filing limits in the dataset are simulated. Future coverage rules will be explicitly labeled as simulated unless they are direct examples from a cited public source.

## Remittance concepts

Real electronic remittance workflows can use Claim Adjustment Group Codes, Claim Adjustment Reason Codes, and Remittance Advice Remark Codes to explain payment adjustments. The initial generator uses plain synthetic reason labels rather than pretending that invented codes are real standard codes. Later denial modules can map selected public code concepts with source documentation.

## Limitations

The project is an educational model rather than a production billing platform.

It does not contain protected health information.

It does not contain proprietary laboratory data.

It does not reproduce any real payer contract.

It does not determine clinical diagnoses.

It does not establish actual coverage or medical necessity.

It does not replace official coding guidance, payer policy, or human billing review.
