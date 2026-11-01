PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    birth_year INTEGER NOT NULL,
    sex TEXT NOT NULL,
    state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS providers (
    provider_id TEXT PRIMARY KEY,
    specialty TEXT NOT NULL,
    state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payers (
    payer_id TEXT PRIMARY KEY,
    payer_name TEXT NOT NULL,
    payer_type TEXT NOT NULL,
    filing_limit_days INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS accessions (
    accession_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    payer_id TEXT NOT NULL,
    service_date TEXT NOT NULL,
    collection_date TEXT NOT NULL,
    test_code TEXT NOT NULL,
    diagnosis_code TEXT,
    charge_amount REAL NOT NULL,
    accession_status TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    FOREIGN KEY (payer_id) REFERENCES payers(payer_id)
);

CREATE TABLE IF NOT EXISTS eligibility (
    eligibility_id TEXT PRIMARY KEY,
    accession_id TEXT NOT NULL,
    coverage_status TEXT NOT NULL,
    subscriber_match TEXT NOT NULL,
    authorization_status TEXT NOT NULL,
    checked_date TEXT NOT NULL,
    FOREIGN KEY (accession_id) REFERENCES accessions(accession_id)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    accession_id TEXT NOT NULL,
    submission_date TEXT,
    claim_type TEXT NOT NULL,
    charge_amount REAL NOT NULL,
    allowed_amount REAL NOT NULL,
    expected_reimbursement REAL NOT NULL,
    payment_amount REAL NOT NULL,
    claim_status TEXT NOT NULL,
    original_claim_id TEXT,
    FOREIGN KEY (accession_id) REFERENCES accessions(accession_id),
    FOREIGN KEY (original_claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS denials (
    denial_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    denial_category TEXT NOT NULL,
    simulated_reason_code TEXT NOT NULL,
    denial_date TEXT NOT NULL,
    denied_amount REAL NOT NULL,
    resolution_status TEXT NOT NULL,
    resolution_date TEXT,
    recovered_amount REAL NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS work_queue (
    work_item_id TEXT PRIMARY KEY,
    accession_id TEXT NOT NULL,
    exception_type TEXT NOT NULL,
    priority_score REAL NOT NULL,
    queue_status TEXT NOT NULL,
    created_date TEXT NOT NULL,
    follow_up_date TEXT,
    resolution_probability REAL NOT NULL,
    FOREIGN KEY (accession_id) REFERENCES accessions(accession_id)
);

CREATE TABLE IF NOT EXISTS claim_history (
    event_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    notes TEXT NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX IF NOT EXISTS idx_accessions_patient_service ON accessions(patient_id, service_date, test_code);
CREATE INDEX IF NOT EXISTS idx_claims_accession ON claims(accession_id);
CREATE INDEX IF NOT EXISTS idx_denials_claim ON denials(claim_id);
CREATE INDEX IF NOT EXISTS idx_queue_status ON work_queue(queue_status, priority_score);
