from src.agents.base_agent import BaseAgent
import json

class ComplianceAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an expert Compliance Agent specializing in loan applications.
Your task is to verify regulatory requirements and compliance rules for loan applications.

Verify compliance with:
1. Minimum Age Requirement (must be 21+)
2. Minimum Credit Score Requirement (typically 600+)
3. Maximum Debt-to-Income Ratio (typically 43%)
4. Minimum Annual Income Requirement
5. AML/KYC Compliance (Know Your Customer)
6. PEP Status Check (Politically Exposed Person)
7. Geographic and Sanctions Compliance

Provide your analysis in JSON format with:
- compliance_status: PASS or FAIL
- age_compliant: true/false with details
- credit_score_compliant: true/false with details
- dti_compliant: true/false with details
- income_compliant: true/false with details
- kyc_compliant: true/false with details
- pep_compliant: true/false with details
- violations: List of regulatory violations if any
- recommendation: APPROVE, REJECT, or REVIEW
- confidence: 0-1 confidence in the recommendation
- justification: Brief explanation of compliance assessment
"""
        super().__init__("Compliance Agent", system_prompt)

    def evaluate(self, applicant_data: dict) -> dict:
        """Evaluate applicant's regulatory compliance"""
        from datetime import datetime, date

        dob = applicant_data.get("date_of_birth")
        age = None
        if isinstance(dob, str):
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            age = (date.today() - dob_date).days // 365
        elif isinstance(dob, date):
            age = (date.today() - dob).days // 365

        prompt_data = {
            "applicant_id": applicant_data.get("id"),
            "age": age,
            "state": applicant_data.get("state"),
            "country": applicant_data.get("country", "USA"),
            "credit_score": applicant_data.get("credit_score"),
            "annual_income": applicant_data.get("annual_income"),
            "debt_to_income_ratio": applicant_data.get("debt_to_income_ratio"),
            "employment_status": applicant_data.get("employment_status"),
            "has_ssn": bool(applicant_data.get("ssn")),
            "kyc_verified": applicant_data.get("kyc_verified", True),
            "pep_status": applicant_data.get("pep_status", "Not Exposed")
        }

        result = self.run_evaluation(prompt_data)
        return result
