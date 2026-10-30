from src.agents.base_agent import BaseAgent
import json

class RiskAssessmentAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an expert Risk Assessment Agent specializing in loan applications.
Your task is to evaluate the financial stability and risk factors of loan applicants.

Analyze the following factors:
1. Debt-to-Income Ratio (target: <43%)
2. Housing Cost Ratio (target: <28%)
3. Monthly Income vs Monthly Debt
4. Employment Stability
5. Liquid Assets and Emergency Savings
6. Collateral Availability

Provide your analysis in JSON format with:
- risk_level: LOW, MEDIUM, or HIGH
- debt_to_income_assessment: Analysis of debt burden
- income_stability: Assessment of income reliability
- savings_and_assets: Assessment of financial cushion
- employment_risk: Assessment based on employment history
- risk_factors: List of identified risk factors
- recommendation: APPROVE, REJECT, or REVIEW
- confidence: 0-1 confidence in the recommendation
- justification: Brief explanation of the assessment
"""
        super().__init__("Risk Assessment Agent", system_prompt)

    def evaluate(self, applicant_data: dict) -> dict:
        """Evaluate applicant's financial risk profile"""
        prompt_data = {
            "applicant_id": applicant_data.get("id"),
            "monthly_income": applicant_data.get("monthly_income"),
            "monthly_debt_payments": applicant_data.get("monthly_debt_payments"),
            "debt_to_income_ratio": applicant_data.get("debt_to_income_ratio"),
            "housing_cost_ratio": applicant_data.get("housing_cost_ratio"),
            "liquid_assets": applicant_data.get("liquid_assets"),
            "savings_account_balance": applicant_data.get("savings_account_balance"),
            "has_collateral": applicant_data.get("has_collateral", False),
            "collateral_value": applicant_data.get("collateral_value"),
            "job_stability_score": applicant_data.get("job_stability_score"),
            "employment_status": applicant_data.get("employment_status"),
            "years_employed": applicant_data.get("years_employed")
        }

        result = self.run_evaluation(prompt_data)
        return result
