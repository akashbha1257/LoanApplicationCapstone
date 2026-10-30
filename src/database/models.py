from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum, ForeignKey, Numeric, Date
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class EmploymentStatus(str, enum.Enum):
    EMPLOYED = "Employed"
    SELF_EMPLOYED = "Self-Employed"
    UNEMPLOYED = "Unemployed"
    RETIRED = "Retired"

class LoanType(str, enum.Enum):
    PERSONAL = "Personal"
    MORTGAGE = "Mortgage"
    AUTO = "Auto"
    BUSINESS = "Business"

class ApplicationStatus(str, enum.Enum):
    PENDING = "Pending"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    MANUAL_REVIEW = "Manual Review"

class CreditScoreRange(str, enum.Enum):
    POOR = "Poor"
    FAIR = "Fair"
    GOOD = "Good"
    VERY_GOOD = "Very Good"
    EXCELLENT = "Excellent"

class RuleType(str, enum.Enum):
    AML = "AML"
    KYC = "KYC"
    AGE = "Age"
    INCOME = "Income"
    DEBT = "Debt"
    CREDIT = "Credit"
    OTHER = "Other"

class Classification(str, enum.Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    MANUAL_REVIEW = "Manual Review"

class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    ssn = Column(String(20), unique=True)
    date_of_birth = Column(Date)
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.EMPLOYED)
    annual_income = Column(Numeric(15, 2))
    employer_name = Column(String(200))
    years_employed = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    loan_applications = relationship("LoanApplication", back_populates="applicant")
    credit_history = relationship("CreditHistory", back_populates="applicant", uselist=False)
    risk_indicators = relationship("RiskIndicators", back_populates="applicant", uselist=False)

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    loan_amount = Column(Numeric(15, 2), nullable=False)
    loan_purpose = Column(String(200))
    loan_type = Column(Enum(LoanType), default=LoanType.PERSONAL)
    loan_term_months = Column(Integer)
    interest_rate_requested = Column(Numeric(5, 2))
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)

    applicant = relationship("Applicant", back_populates="loan_applications")
    evaluation = relationship("ApplicationEvaluation", back_populates="application", uselist=False)

class CreditHistory(Base):
    __tablename__ = "credit_history"

    id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    credit_score = Column(Integer)
    credit_score_range = Column(Enum(CreditScoreRange))
    total_credit_limit = Column(Numeric(15, 2))
    total_credit_used = Column(Numeric(15, 2))
    credit_utilization_percent = Column(Numeric(5, 2))
    accounts_open = Column(Integer)
    accounts_closed = Column(Integer)
    late_payments_30_days = Column(Integer, default=0)
    late_payments_60_days = Column(Integer, default=0)
    late_payments_90_days = Column(Integer, default=0)
    defaults = Column(Integer, default=0)
    delinquencies = Column(Integer, default=0)
    collections = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = relationship("Applicant", back_populates="credit_history")

class RiskIndicators(Base):
    __tablename__ = "risk_indicators"

    id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    monthly_income = Column(Numeric(15, 2))
    monthly_debt_payments = Column(Numeric(15, 2))
    debt_to_income_ratio = Column(Numeric(5, 2))
    housing_cost_ratio = Column(Numeric(5, 2))
    liquid_assets = Column(Numeric(15, 2))
    savings_account_balance = Column(Numeric(15, 2))
    has_collateral = Column(Boolean, default=False)
    collateral_value = Column(Numeric(15, 2))
    job_stability_score = Column(Integer)
    industry = Column(String(100))
    frequent_address_changes = Column(Integer, default=0)
    fraud_flag = Column(Boolean, default=False)
    fraud_reason = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = relationship("Applicant", back_populates="risk_indicators")

class RegulatoryRule(Base):
    __tablename__ = "regulatory_rules"

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(200), unique=True, nullable=False)
    rule_type = Column(Enum(RuleType), default=RuleType.OTHER)
    minimum_age = Column(Integer)
    minimum_credit_score = Column(Integer)
    maximum_debt_to_income = Column(Numeric(5, 2))
    minimum_income = Column(Numeric(15, 2))
    sanctioned_countries = Column(Text)
    pep_check_required = Column(Boolean, default=True)
    id_verification_required = Column(Boolean, default=True)
    description = Column(Text)
    effective_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ApplicationEvaluation(Base):
    __tablename__ = "application_evaluations"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    credit_agent_result = Column(Text)
    credit_agent_score = Column(Numeric(3, 2))
    risk_agent_result = Column(Text)
    risk_agent_score = Column(Numeric(3, 2))
    compliance_agent_result = Column(Text)
    compliance_agent_passed = Column(Boolean)
    fraud_agent_result = Column(Text)
    fraud_agent_risk_level = Column(String(50))
    final_decision_agent_result = Column(Text)
    final_classification = Column(Enum(Classification))
    confidence_score = Column(Numeric(3, 2))
    decision_justification = Column(Text)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplication", back_populates="evaluation")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"))
    agent_name = Column(String(100))
    action = Column(String(200))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
