# Interview Presentation

## Slide 1: Laboratory Revenue Cycle Analytics

I built a synthetic laboratory billing intelligence project that models the path from accession through reimbursement. The project uses Python, pandas, SQLite, and Streamlit.

## Slide 2: Business Problem

Laboratory revenue can be delayed when billing information is incomplete, insurance cannot be verified, documentation needs clarification, duplicate services require review, or claims are denied. The goal was to identify those exceptions early and route work according to financial risk and filing urgency.

## Slide 3: Data Design

The project generates 25,000 synthetic laboratory accessions. Related tables represent patients, providers, payers, eligibility checks, claims, denials, work queue activity, and claim history. No real patient or proprietary payer data is used.

## Slide 4: Prebill Validation

The validation engine checks diagnosis format, missing diagnosis information, simulated policy combinations, eligibility status, subscriber information, authorization status, and duplicate signals. A simulated policy mismatch creates a documentation review. It never changes a diagnosis to obtain payment.

## Slide 5: Work Queue Prioritization

Exceptions are ranked using filing urgency, financial exposure, and estimated resolvability. Claims close to a simulated filing deadline receive greater priority. Provider clarification messages request accurate documentation rather than suggesting diagnoses.

## Slide 6: Duplicate Review

Exact matching uses patient, service date, test code, and provider. Near matching looks for the same patient and test within a short period. Matches are sent to manual review because repeat testing and corrected claims can be legitimate.

## Slide 7: Denial and Recovery Analytics

The project separates gross charges, allowed amounts, expected reimbursement, actual payments, denied dollars, and recovered dollars. It calculates denial rate, recovery rate, dollars recovered, and average resolution time.

## Slide 8: Dashboard

The Streamlit dashboard provides an executive overview, a filterable billing exception queue, denial analysis, and prebill validation quality metrics.

## Slide 9: Controls and Limitations

Every patient, provider, payer, policy, financial amount, filing limit, and outcome is synthetic. Simulated coverage rules are not presented as actual payer policy. Real operational use would require validated payer rules, current code sets, security controls, audit processes, and compliance review.

## Slide 10: What I Learned

The project taught me that revenue cycle analytics is not simply about finding denied claims. Strong operations try to prevent avoidable denials before submission, prioritize work by both urgency and value, preserve documentation integrity, and measure recovery using realistic reimbursement expectations rather than gross charges alone.
