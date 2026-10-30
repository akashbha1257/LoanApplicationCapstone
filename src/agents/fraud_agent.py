from src.agents.base_agent import BaseAgent
import json

class FraudDetectionAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an expert Fraud Detection Agent specializing in loan applications.
Your task is to identify suspicious patterns and potential fraud in loan applications.

Analyze the following red flags:
1. Income Inconsistencies (applicant's reported income vs credit pattern)
2. Credit Score Inconsistencies (high income but low credit score)
3. Identity Verification Issues
4. Unusual Application Patterns (multiple applications, rapid address changes)
5. Employment Verification Gaps
6. Collateral Inconsistencies
7. Documentation Red Flags

Provide your analysis in JSON format with:
- fraud_risk_level: LOW, MEDIUM, or HIGH
- fraud_indicators: List of identified fraud red flags
- income_consistency: Assessment of income report credibility
- credit_consistency: Assessment of credit patterns alignment
- identity_confidence: Assessment of identity verification
- employment_verification: Assessment of employment claims
- suspicious_patterns: Any unusual patterns detected
- recommendation: APPROVE, REJECT, or REVIEW
- confidence: 0-1 confidence in the assessment
- justification: Brief explanation of fraud risk assessment
"""
        super().__init__("Fraud Detection Agent", system_prompt)

    def evaluate(self, applicant_data: dict) -> dict:
        """Evaluate applicant for fraud indicators"""
        prompt_data = {
            "applicant_id": applicant_data.get("id"),
            "reported_annual_income": applicant_data.get("annual_income"),
            "credit_score": applicant_data.get("credit_score"),
            "credit_utilization_percent": applicant_data.get("credit_utilization_percent"),
            "total_credit_used": applicant_data.get("total_credit_used"),
            "employment_status": applicant_data.get("employment_status"),
            "years_employed": applicant_data.get("years_employed", 0),
            "address_changes": applicant_data.get("frequent_address_changes", 0),
            "has_ssn": bool(applicant_data.get("ssn")),
            "accounts_open": applicant_data.get("accounts_open"),
            "recent_credit_inquiries": applicant_data.get("recent_credit_inquiries", 0),
            "has_collateral": applicant_data.get("has_collateral", False),
            "collateral_value": applicant_data.get("collateral_value"),
            "fraud_flag": applicant_data.get("fraud_flag", False),
            "fraud_reason": applicant_data.get("fraud_reason")
        }

        result = self.run_evaluation(prompt_data)
        return result
