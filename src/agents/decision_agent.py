from src.agents.base_agent import BaseAgent
import json

class DecisionAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the Final Decision Agent responsible for synthesizing loan application evaluations.
Your task is to aggregate findings from all specialist agents and make a final classification decision.

Agent Findings to Consider:
1. Credit Analysis Agent - creditworthiness assessment
2. Risk Assessment Agent - financial stability evaluation
3. Compliance Agent - regulatory compliance verification
4. Fraud Detection Agent - fraud risk assessment

Decision Logic:
- APPROVED: All agents recommend APPROVE with no critical flags
- REJECTED: Any REJECT recommendation or critical compliance violations
- MANUAL REVIEW: Mixed signals, edge cases, or conflicting recommendations

Provide your analysis in JSON format with:
- final_classification: APPROVED, REJECTED, or MANUAL_REVIEW
- decision_summary: Overview of key factors
- credit_assessment_summary: Key points from credit agent
- risk_assessment_summary: Key points from risk agent
- compliance_assessment_summary: Key points from compliance agent
- fraud_assessment_summary: Key points from fraud agent
- critical_factors: Most important decision drivers
- confidence: 0-1 overall confidence in decision
- justification: Detailed explanation of final decision
- next_steps: Recommended actions
"""
        super().__init__("Decision Agent", system_prompt)

    def evaluate(self, agent_results: dict) -> dict:
        """Synthesize all agent evaluations into final decision"""
        prompt_data = {
            "credit_analysis": agent_results.get("credit_agent", {}),
            "risk_assessment": agent_results.get("risk_agent", {}),
            "compliance_check": agent_results.get("compliance_agent", {}),
            "fraud_detection": agent_results.get("fraud_agent", {}),
            "applicant_id": agent_results.get("applicant_id"),
            "loan_amount": agent_results.get("loan_amount"),
            "loan_type": agent_results.get("loan_type")
        }

        result = self.run_evaluation(prompt_data)
        return result

    def synthesize_decision(self, all_agent_results: dict) -> dict:
        """High-level synthesis without Claude for quick decisions"""
        try:
            credit = all_agent_results.get("credit_agent", {}).get("analysis", {})
            risk = all_agent_results.get("risk_agent", {}).get("analysis", {})
            compliance = all_agent_results.get("compliance_agent", {}).get("analysis", {})
            fraud = all_agent_results.get("fraud_agent", {}).get("analysis", {})

            # Count recommendations
            rejects = sum([
                credit.get("recommendation") == "REJECT",
                risk.get("recommendation") == "REJECT",
                compliance.get("recommendation") == "REJECT",
                fraud.get("recommendation") == "REJECT"
            ])

            approves = sum([
                credit.get("recommendation") == "APPROVE",
                risk.get("recommendation") == "APPROVE",
                compliance.get("recommendation") == "APPROVE",
                fraud.get("recommendation") == "APPROVE"
            ])

            # Decision logic
            if rejects > 0 or compliance.get("compliance_status") == "FAIL":
                classification = "Rejected"
            elif approves == 4:
                classification = "Approved"
            else:
                classification = "Manual Review"

            return {
                "final_classification": classification,
                "credit_assessment": credit.get("credit_rating", "Unknown"),
                "risk_level": risk.get("risk_level", "Unknown"),
                "compliance_status": compliance.get("compliance_status", "Unknown"),
                "fraud_risk": fraud.get("fraud_risk_level", "Unknown"),
                "confidence": min(0.95, max(0.7, (approves * 0.2) + 0.3)),
                "decision_summary": f"Application classified as {classification}"
            }
        except Exception as e:
            return {"error": str(e), "final_classification": "Manual Review"}
