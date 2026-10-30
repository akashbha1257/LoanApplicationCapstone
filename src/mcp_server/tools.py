import json
from src.database.connection import DatabaseConnection
from src.database.models import (
    Applicant, CreditHistory, RiskIndicators, LoanApplication, AuditLog, RegulatoryRule
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MCPTools:
    @staticmethod
    def query_applicant_data(applicant_id: int) -> dict:
        """Query complete applicant information"""
        try:
            db = DatabaseConnection.get_session()
            applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
            if not applicant:
                return {"error": "Applicant not found"}

            credit = db.query(CreditHistory).filter(CreditHistory.applicant_id == applicant_id).first()
            risk = db.query(RiskIndicators).filter(RiskIndicators.applicant_id == applicant_id).first()

            data = {
                "applicant": {
                    "id": applicant.id,
                    "name": f"{applicant.first_name} {applicant.last_name}",
                    "email": applicant.email,
                    "phone": applicant.phone,
                    "date_of_birth": str(applicant.date_of_birth) if applicant.date_of_birth else None,
                    "address": applicant.address,
                    "city": applicant.city,
                    "state": applicant.state,
                    "zip_code": applicant.zip_code,
                    "employment_status": applicant.employment_status.value if applicant.employment_status else None,
                    "annual_income": float(applicant.annual_income) if applicant.annual_income else 0,
                    "employer_name": applicant.employer_name,
                    "years_employed": applicant.years_employed
                },
                "credit_history": {
                    "credit_score": credit.credit_score if credit else None,
                    "credit_score_range": credit.credit_score_range.value if credit and credit.credit_score_range else None,
                    "total_credit_limit": float(credit.total_credit_limit) if credit and credit.total_credit_limit else 0,
                    "total_credit_used": float(credit.total_credit_used) if credit and credit.total_credit_used else 0,
                    "credit_utilization_percent": float(credit.credit_utilization_percent) if credit and credit.credit_utilization_percent else 0,
                    "accounts_open": credit.accounts_open if credit else 0,
                    "accounts_closed": credit.accounts_closed if credit else 0,
                    "late_payments_30_days": credit.late_payments_30_days if credit else 0,
                    "late_payments_60_days": credit.late_payments_60_days if credit else 0,
                    "late_payments_90_days": credit.late_payments_90_days if credit else 0,
                    "defaults": credit.defaults if credit else 0,
                    "delinquencies": credit.delinquencies if credit else 0
                } if credit else {},
                "risk_indicators": {
                    "monthly_income": float(risk.monthly_income) if risk and risk.monthly_income else 0,
                    "monthly_debt_payments": float(risk.monthly_debt_payments) if risk and risk.monthly_debt_payments else 0,
                    "debt_to_income_ratio": float(risk.debt_to_income_ratio) if risk and risk.debt_to_income_ratio else 0,
                    "housing_cost_ratio": float(risk.housing_cost_ratio) if risk and risk.housing_cost_ratio else 0,
                    "liquid_assets": float(risk.liquid_assets) if risk and risk.liquid_assets else 0,
                    "savings_account_balance": float(risk.savings_account_balance) if risk and risk.savings_account_balance else 0,
                    "has_collateral": risk.has_collateral if risk else False,
                    "collateral_value": float(risk.collateral_value) if risk and risk.collateral_value else 0,
                    "job_stability_score": risk.job_stability_score if risk else 0,
                    "industry": risk.industry if risk else None,
                    "fraud_flag": risk.fraud_flag if risk else False
                } if risk else {}
            }
            db.close()
            return data
        except Exception as e:
            logger.error(f"Error querying applicant data: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_regulatory_rules() -> list:
        """Get all active regulatory rules"""
        try:
            db = DatabaseConnection.get_session()
            rules = db.query(RegulatoryRule).filter(RegulatoryRule.is_active == True).all()

            rules_data = []
            for rule in rules:
                rules_data.append({
                    "id": rule.id,
                    "rule_name": rule.rule_name,
                    "rule_type": rule.rule_type.value if rule.rule_type else None,
                    "minimum_age": rule.minimum_age,
                    "minimum_credit_score": rule.minimum_credit_score,
                    "maximum_debt_to_income": float(rule.maximum_debt_to_income) if rule.maximum_debt_to_income else None,
                    "minimum_income": float(rule.minimum_income) if rule.minimum_income else None,
                    "pep_check_required": rule.pep_check_required,
                    "id_verification_required": rule.id_verification_required,
                    "description": rule.description
                })
            db.close()
            return rules_data
        except Exception as e:
            logger.error(f"Error retrieving regulatory rules: {str(e)}")
            return []

    @staticmethod
    def log_decision(application_id: int, agent_name: str, action: str, details: dict) -> dict:
        """Log agent decision to audit trail"""
        try:
            db = DatabaseConnection.get_session()
            audit = AuditLog(
                application_id=application_id,
                agent_name=agent_name,
                action=action,
                details=json.dumps(details)
            )
            db.add(audit)
            db.commit()
            db.close()
            return {"status": "logged", "application_id": application_id}
        except Exception as e:
            logger.error(f"Error logging decision: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_loan_details(application_id: int) -> dict:
        """Get loan application details"""
        try:
            db = DatabaseConnection.get_session()
            application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
            if not application:
                return {"error": "Application not found"}

            data = {
                "id": application.id,
                "applicant_id": application.applicant_id,
                "loan_amount": float(application.loan_amount) if application.loan_amount else 0,
                "loan_purpose": application.loan_purpose,
                "loan_type": application.loan_type.value if application.loan_type else None,
                "loan_term_months": application.loan_term_months,
                "interest_rate_requested": float(application.interest_rate_requested) if application.interest_rate_requested else None,
                "status": application.status.value if application.status else None
            }
            db.close()
            return data
        except Exception as e:
            logger.error(f"Error retrieving loan details: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def verify_compliance_rule(applicant_id: int, rule_id: int) -> dict:
        """Verify if applicant meets a specific regulatory rule"""
        try:
            from datetime import date, datetime
            db = DatabaseConnection.get_session()

            applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
            rule = db.query(RegulatoryRule).filter(RegulatoryRule.id == rule_id).first()

            if not applicant or not rule:
                return {"compliant": False, "reason": "Applicant or rule not found"}

            credit = db.query(CreditHistory).filter(CreditHistory.applicant_id == applicant_id).first()
            risk = db.query(RiskIndicators).filter(RiskIndicators.applicant_id == applicant_id).first()

            result = {"compliant": True, "details": []}

            # Age check
            if rule.minimum_age:
                if applicant.date_of_birth:
                    age = (date.today() - applicant.date_of_birth).days // 365
                    if age < rule.minimum_age:
                        result["compliant"] = False
                        result["details"].append(f"Age {age} below minimum {rule.minimum_age}")

            # Credit score check
            if rule.minimum_credit_score and credit and credit.credit_score:
                if credit.credit_score < rule.minimum_credit_score:
                    result["compliant"] = False
                    result["details"].append(f"Credit score {credit.credit_score} below minimum {rule.minimum_credit_score}")

            # DTI check
            if rule.maximum_debt_to_income and risk and risk.debt_to_income_ratio:
                if risk.debt_to_income_ratio > rule.maximum_debt_to_income:
                    result["compliant"] = False
                    result["details"].append(f"DTI {risk.debt_to_income_ratio} exceeds maximum {rule.maximum_debt_to_income}")

            # Income check
            if rule.minimum_income and applicant.annual_income:
                if float(applicant.annual_income) < float(rule.minimum_income):
                    result["compliant"] = False
                    result["details"].append(f"Income {applicant.annual_income} below minimum {rule.minimum_income}")

            db.close()
            return result
        except Exception as e:
            logger.error(f"Error verifying compliance: {str(e)}")
            return {"error": str(e), "compliant": False}
