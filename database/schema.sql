-- Create Applicants table
CREATE TABLE IF NOT EXISTS applicants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    ssn VARCHAR(20) UNIQUE,
    date_of_birth DATE,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    employment_status ENUM('Employed', 'Self-Employed', 'Unemployed', 'Retired') DEFAULT 'Employed',
    annual_income DECIMAL(15, 2),
    employer_name VARCHAR(200),
    years_employed INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Loan Applications table
CREATE TABLE IF NOT EXISTS loan_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id INT NOT NULL,
    loan_amount DECIMAL(15, 2) NOT NULL,
    loan_purpose VARCHAR(200),
    loan_type ENUM('Personal', 'Mortgage', 'Auto', 'Business') DEFAULT 'Personal',
    loan_term_months INT,
    interest_rate_requested DECIMAL(5, 2),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Under Review', 'Approved', 'Rejected', 'Manual Review') DEFAULT 'Pending',
    FOREIGN KEY (applicant_id) REFERENCES applicants(id),
    UNIQUE KEY unique_pending_app (applicant_id, application_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Credit History table
CREATE TABLE IF NOT EXISTS credit_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id INT NOT NULL,
    credit_score INT,
    credit_score_range ENUM('Poor', 'Fair', 'Good', 'Very Good', 'Excellent'),
    total_credit_limit DECIMAL(15, 2),
    total_credit_used DECIMAL(15, 2),
    credit_utilization_percent DECIMAL(5, 2),
    accounts_open INT,
    accounts_closed INT,
    late_payments_30_days INT DEFAULT 0,
    late_payments_60_days INT DEFAULT 0,
    late_payments_90_days INT DEFAULT 0,
    defaults INT DEFAULT 0,
    delinquencies INT DEFAULT 0,
    collections INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES applicants(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Risk Indicators table
CREATE TABLE IF NOT EXISTS risk_indicators (
    id INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id INT NOT NULL,
    monthly_income DECIMAL(15, 2),
    monthly_debt_payments DECIMAL(15, 2),
    debt_to_income_ratio DECIMAL(5, 2),
    housing_cost_ratio DECIMAL(5, 2),
    liquid_assets DECIMAL(15, 2),
    savings_account_balance DECIMAL(15, 2),
    has_collateral BOOLEAN DEFAULT FALSE,
    collateral_value DECIMAL(15, 2),
    job_stability_score INT,
    industry VARCHAR(100),
    frequent_address_changes INT DEFAULT 0,
    fraud_flag BOOLEAN DEFAULT FALSE,
    fraud_reason TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES applicants(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Regulatory Rules table
CREATE TABLE IF NOT EXISTS regulatory_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rule_name VARCHAR(200) NOT NULL UNIQUE,
    rule_type ENUM('AML', 'KYC', 'Age', 'Income', 'Debt', 'Credit', 'Other') DEFAULT 'Other',
    minimum_age INT,
    minimum_credit_score INT,
    maximum_debt_to_income DECIMAL(5, 2),
    minimum_income DECIMAL(15, 2),
    sanctioned_countries TEXT,
    pep_check_required BOOLEAN DEFAULT TRUE,
    id_verification_required BOOLEAN DEFAULT TRUE,
    description TEXT,
    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Application Evaluations table
CREATE TABLE IF NOT EXISTS application_evaluations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    credit_agent_result JSON,
    credit_agent_score DECIMAL(3, 2),
    risk_agent_result JSON,
    risk_agent_score DECIMAL(3, 2),
    compliance_agent_result JSON,
    compliance_agent_passed BOOLEAN,
    fraud_agent_result JSON,
    fraud_agent_risk_level VARCHAR(50),
    final_decision_agent_result JSON,
    final_classification ENUM('Approved', 'Rejected', 'Manual Review'),
    confidence_score DECIMAL(3, 2),
    decision_justification TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Audit Log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT,
    agent_name VARCHAR(100),
    action VARCHAR(200),
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create indexes for better query performance
CREATE INDEX idx_applicant_email ON applicants(email);
CREATE INDEX idx_applicant_ssn ON applicants(ssn);
CREATE INDEX idx_loan_applicant ON loan_applications(applicant_id);
CREATE INDEX idx_loan_status ON loan_applications(status);
CREATE INDEX idx_credit_applicant ON credit_history(applicant_id);
CREATE INDEX idx_risk_applicant ON risk_indicators(applicant_id);
CREATE INDEX idx_eval_application ON application_evaluations(application_id);
CREATE INDEX idx_audit_application ON audit_log(application_id);

-- Insert Sample Regulatory Rules
INSERT INTO regulatory_rules (rule_name, rule_type, minimum_age, minimum_credit_score, maximum_debt_to_income, minimum_income, description, is_active) VALUES
('Minimum Age Requirement', 'Age', 21, NULL, NULL, NULL, 'Applicants must be at least 21 years old', TRUE),
('Minimum Credit Score', 'Credit', NULL, 600, NULL, NULL, 'Minimum credit score for approval', TRUE),
('Maximum Debt-to-Income', 'Debt', NULL, NULL, 43.00, NULL, 'Maximum debt-to-income ratio allowed', TRUE),
('Minimum Annual Income', 'Income', NULL, NULL, NULL, 25000.00, 'Minimum annual income requirement', TRUE),
('KYC Verification', 'KYC', NULL, NULL, NULL, NULL, 'Know Your Customer verification required', TRUE),
('AML Compliance', 'AML', NULL, NULL, NULL, NULL, 'Anti-Money Laundering compliance check', TRUE),
('PEP Check', 'Other', NULL, NULL, NULL, NULL, 'Politically Exposed Person screening', TRUE);

-- Insert Sample Applicants
INSERT INTO applicants (first_name, last_name, email, phone, ssn, date_of_birth, address, city, state, zip_code, employment_status, annual_income, employer_name, years_employed) VALUES
('John', 'Doe', 'john.doe@email.com', '555-0101', '123-45-6789', '1985-06-15', '123 Main St', 'New York', 'NY', '10001', 'Employed', 75000.00, 'Tech Corp', 5),
('Jane', 'Smith', 'jane.smith@email.com', '555-0102', '123-45-6790', '1990-03-22', '456 Oak Ave', 'Los Angeles', 'CA', '90001', 'Employed', 95000.00, 'Finance Inc', 8),
('Bob', 'Johnson', 'bob.johnson@email.com', '555-0103', '123-45-6791', '1982-11-30', '789 Pine Rd', 'Chicago', 'IL', '60601', 'Self-Employed', 120000.00, 'Own Business', 10),
('Alice', 'Williams', 'alice.williams@email.com', '555-0104', '123-45-6792', '1995-07-08', '321 Elm St', 'Houston', 'TX', '77001', 'Employed', 55000.00, 'Retail Co', 2),
('Charlie', 'Brown', 'charlie.brown@email.com', '555-0105', '123-45-6793', '1988-02-14', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 'Unemployed', 0.00, NULL, 0),
('Diana', 'Martinez', 'diana.martinez@email.com', '555-0106', '123-45-6794', '1992-09-20', '987 Cedar Ln', 'Philadelphia', 'PA', '19101', 'Employed', 85000.00, 'Healthcare Org', 6),
('Edward', 'Garcia', 'edward.garcia@email.com', '555-0107', '123-45-6795', '1980-04-11', '159 Birch Ave', 'San Antonio', 'TX', '78201', 'Employed', 125000.00, 'Law Firm', 15),
('Fiona', 'Rodriguez', 'fiona.rodriguez@email.com', '555-0108', '123-45-6796', '1993-12-03', '357 Spruce St', 'San Diego', 'CA', '92101', 'Employed', 78000.00, 'Education', 4),
('George', 'Lee', 'george.lee@email.com', '555-0109', '123-45-6797', '1987-05-25', '852 Ash Rd', 'Dallas', 'TX', '75201', 'Self-Employed', 95000.00, 'Consulting', 7),
('Helen', 'Taylor', 'helen.taylor@email.com', '555-0110', '123-45-6798', '1991-10-12', '753 Willow Dr', 'Austin', 'TX', '78701', 'Employed', 110000.00, 'Tech Startup', 3);

-- Insert Sample Credit History
INSERT INTO credit_history (applicant_id, credit_score, credit_score_range, total_credit_limit, total_credit_used, credit_utilization_percent, accounts_open, accounts_closed, late_payments_30_days, defaults, delinquencies) VALUES
(1, 720, 'Good', 50000, 12000, 24, 8, 2, 0, 0, 0),
(2, 780, 'Very Good', 75000, 15000, 20, 10, 1, 0, 0, 0),
(3, 650, 'Fair', 40000, 20000, 50, 5, 3, 2, 0, 1),
(4, 550, 'Poor', 15000, 12000, 80, 3, 2, 5, 1, 2),
(5, 580, 'Poor', 10000, 8000, 80, 2, 1, 3, 0, 1),
(6, 750, 'Very Good', 60000, 18000, 30, 9, 0, 0, 0, 0),
(7, 800, 'Excellent', 100000, 20000, 20, 12, 0, 0, 0, 0),
(8, 710, 'Good', 55000, 22000, 40, 7, 2, 0, 0, 0),
(9, 690, 'Good', 48000, 14400, 30, 6, 2, 0, 0, 0),
(10, 770, 'Very Good', 80000, 16000, 20, 11, 1, 0, 0, 0);

-- Insert Sample Risk Indicators
INSERT INTO risk_indicators (applicant_id, monthly_income, monthly_debt_payments, debt_to_income_ratio, housing_cost_ratio, liquid_assets, savings_account_balance, has_collateral, collateral_value, job_stability_score, industry, fraud_flag) VALUES
(1, 6250, 1500, 24, 15, 50000, 25000, TRUE, 80000, 85, 'Technology', FALSE),
(2, 7917, 1800, 23, 18, 75000, 40000, TRUE, 150000, 90, 'Finance', FALSE),
(3, 10000, 3000, 30, 20, 100000, 50000, TRUE, 200000, 75, 'Consulting', FALSE),
(4, 4583, 1200, 26, 20, 15000, 8000, FALSE, 0, 60, 'Retail', FALSE),
(5, 0, 500, 0, 0, 5000, 2000, FALSE, 0, 20, 'Unemployed', TRUE),
(6, 7083, 1600, 23, 17, 60000, 35000, TRUE, 120000, 80, 'Healthcare', FALSE),
(7, 10417, 2000, 19, 14, 200000, 100000, TRUE, 500000, 95, 'Law', FALSE),
(8, 6500, 1800, 28, 22, 45000, 20000, TRUE, 100000, 72, 'Education', FALSE),
(9, 7917, 2200, 28, 20, 60000, 30000, TRUE, 180000, 78, 'Consulting', FALSE),
(10, 9167, 1700, 19, 16, 120000, 60000, TRUE, 300000, 88, 'Technology', FALSE);
