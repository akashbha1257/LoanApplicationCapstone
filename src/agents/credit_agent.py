from src.agents.base_agent import BaseAgent
import json

class CreditAnalysisAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an expert Credit Analysis Agent specializing in loan applications.
Your task is to evaluate an applicant's creditworthiness based on their credit history.

Analyze the following factors:
1. Credit Score (scale: 300-850)
2. Credit Utilization Ratio
3. Payment History (late payments, defaults, delinquencies)
4. Credit Account Mix
5. Length of Credit History

Provide your analysis in JSON format with:
- credit_rating: Letter grade (A, B, C, D, F)
- credit_score_assessment: Description of credit score quality
- risk_score: 0-100 (0 = no risk, 100 = maximum risk)
- key_concerns: List of any concerning factors
- recommendation: APPROVE, REJECT, or REVIEW
- confidence: 0-1 confidence in the recommendation
- justification: Brief explanation of the assessment
"""
        super().__init__("Credit Analysis Agent", system_prompt)

    def evaluate(self, applicant_data: dict) -> dict:
        """Evaluate applicant's credit profile"""
        prompt_data = {
            "applicant_id": applicant_data.get("id"),
            "credit_score": applicant_data.get("credit_score"),
            "credit_score_range": applicant_data.get("credit_score_range"),
            "total_credit_limit": applicant_data.get("total_credit_limit"),
            "total_credit_used": applicant_data.get("total_credit_used"),
            "credit_utilization_percent": applicant_data.get("credit_utilization_percent"),
            "late_payments_30_days": applicant_data.get("late_payments_30_days", 0),
            "late_payments_60_days": applicant_data.get("late_payments_60_days", 0),
            "late_payments_90_days": applicant_data.get("late_payments_90_days", 0),
            "defaults": applicant_data.get("defaults", 0),
            "delinquencies": applicant_data.get("delinquencies", 0),
            "accounts_open": applicant_data.get("accounts_open"),
            "accounts_closed": applicant_data.get("accounts_closed")
        }

        result = self.run_evaluation(prompt_data)
        return result
