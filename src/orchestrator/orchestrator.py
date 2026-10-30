import asyncio
from typing import Dict, Any
from datetime import datetime
from src.agents import (
    CreditAnalysisAgent,
    RiskAssessmentAgent,
    ComplianceAgent,
    FraudDetectionAgent,
    DecisionAgent
)
from src.database.connection import DatabaseConnection
from src.database.models import (
    LoanApplication,
    ApplicationEvaluation,
    Applicant,
    CreditHistory,
    RiskIndicators,
    Classification,
    ApplicationStatus,
    AuditLog
)
from src.mcp_server import get_mcp_server
from src.utils.logger import get_logger
import json

logger = get_logger(__name__)

class LoanApplicationOrchestrator:
    def __init__(self):
        self.credit_agent = CreditAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.compliance_agent = ComplianceAgent()
        self.fraud_agent = FraudDetectionAgent()
        self.decision_agent = DecisionAgent()
        self.mcp_server = get_mcp_server()

    def evaluate_application(self, application_id: int) -> Dict[str, Any]:
        """Orchestrate evaluation of a loan application"""
        logger.info(f"Starting evaluation for application {application_id}")

        try:
            db = DatabaseConnection.get_session()

            # Get application and applicant data
            application = db.query(LoanApplication).filter(
                LoanApplication.id == application_id
            ).first()

            if not application:
                logger.error(f"Application {application_id} not found")
                return {"error": "Application not found", "status": "failed"}

            applicant = db.query(Applicant).filter(
                Applicant.id == application.applicant_id
            ).first()

            credit_history = db.query(CreditHistory).filter(
                CreditHistory.applicant_id == application.applicant_id
            ).first()

            risk_indicators = db.query(RiskIndicators).filter(
                RiskIndicators.applicant_id == application.applicant_id
            ).first()

            # Prepare applicant data for agents
            applicant_data = self._prepare_applicant_data(
                applicant, credit_history, risk_indicators, application
            )

            # Run agents in parallel
            logger.info("Running agents in parallel...")
            results = asyncio.run(self._run_agents_parallel(applicant_data, application_id))

            # Log each agent result
            self._log_agent_results(db, application_id, results)

            # Make final decision
            final_decision = self.decision_agent.synthesize_decision(results)

            # Save evaluation to database
            evaluation = ApplicationEvaluation(
                application_id=application_id,
                credit_agent_result=results.get("credit_agent", {}).get("raw_response", ""),
                credit_agent_score=self._extract_score(results.get("credit_agent", {})),
                risk_agent_result=results.get("risk_agent", {}).get("raw_response", ""),
                risk_agent_score=self._extract_score(results.get("risk_agent", {})),
                compliance_agent_result=results.get("compliance_agent", {}).get("raw_response", ""),
                compliance_agent_passed=results.get("compliance_agent", {}).get("analysis", {}).get("compliance_status") == "PASS",
                fraud_agent_result=results.get("fraud_agent", {}).get("raw_response", ""),
                fraud_agent_risk_level=results.get("fraud_agent", {}).get("analysis", {}).get("fraud_risk_level", "UNKNOWN"),
                final_decision_agent_result=json.dumps(final_decision),
                final_classification=Classification(final_decision.get("final_classification", "MANUAL_REVIEW")),
                confidence_score=final_decision.get("confidence", 0.5),
                decision_justification=final_decision.get("decision_summary", "")
            )

            db.add(evaluation)
            application.status = ApplicationStatus(final_decision.get("final_classification", "MANUAL_REVIEW"))
            db.commit()

            result = {
                "application_id": application_id,
                "status": "completed",
                "final_decision": final_decision,
                "agent_results": {
                    "credit": results.get("credit_agent", {}).get("analysis", {}),
                    "risk": results.get("risk_agent", {}).get("analysis", {}),
                    "compliance": results.get("compliance_agent", {}).get("analysis", {}),
                    "fraud": results.get("fraud_agent", {}).get("analysis", {})
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Evaluation complete for application {application_id}: {final_decision.get('final_classification')}")
            db.close()
            return result

        except Exception as e:
            logger.error(f"Error evaluating application {application_id}: {str(e)}")
            return {"error": str(e), "status": "failed", "application_id": application_id}

    async def _run_agents_parallel(self, applicant_data: dict, application_id: int) -> Dict[str, Any]:
        """Run all agents in parallel"""
        tasks = [
            self._run_agent_async(self.credit_agent, applicant_data, "credit_agent"),
            self._run_agent_async(self.risk_agent, applicant_data, "risk_agent"),
            self._run_agent_async(self.compliance_agent, applicant_data, "compliance_agent"),
            self._run_agent_async(self.fraud_agent, applicant_data, "fraud_agent")
        ]

        results_list = await asyncio.gather(*tasks)

        results = {
            "credit_agent": results_list[0],
            "risk_agent": results_list[1],
            "compliance_agent": results_list[2],
            "fraud_agent": results_list[3],
            "applicant_id": applicant_data.get("id"),
            "loan_amount": applicant_data.get("loan_amount"),
            "loan_type": applicant_data.get("loan_type")
        }

        return results

    async def _run_agent_async(self, agent, applicant_data: dict, agent_name: str) -> Dict[str, Any]:
        """Run agent asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, agent.evaluate, applicant_data)

    def _prepare_applicant_data(self, applicant, credit_history, risk_indicators, application) -> dict:
        """Prepare applicant data for agent evaluation"""
        return {
            "id": applicant.id,
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "date_of_birth": str(applicant.date_of_birth) if applicant.date_of_birth else None,
            "ssn": applicant.ssn,
            "state": applicant.state,
            "country": "USA",
            "employment_status": applicant.employment_status.value if applicant.employment_status else None,
            "annual_income": float(applicant.annual_income) if applicant.annual_income else 0,
            "employer_name": applicant.employer_name,
            "years_employed": applicant.years_employed,
            "kyc_verified": True,
            "pep_status": "Not Exposed",
            "credit_score": credit_history.credit_score if credit_history else None,
            "credit_score_range": credit_history.credit_score_range.value if credit_history and credit_history.credit_score_range else None,
            "total_credit_limit": float(credit_history.total_credit_limit) if credit_history and credit_history.total_credit_limit else 0,
            "total_credit_used": float(credit_history.total_credit_used) if credit_history and credit_history.total_credit_used else 0,
            "credit_utilization_percent": float(credit_history.credit_utilization_percent) if credit_history and credit_history.credit_utilization_percent else 0,
            "accounts_open": credit_history.accounts_open if credit_history else 0,
            "accounts_closed": credit_history.accounts_closed if credit_history else 0,
            "late_payments_30_days": credit_history.late_payments_30_days if credit_history else 0,
            "late_payments_60_days": credit_history.late_payments_60_days if credit_history else 0,
            "late_payments_90_days": credit_history.late_payments_90_days if credit_history else 0,
            "defaults": credit_history.defaults if credit_history else 0,
            "delinquencies": credit_history.delinquencies if credit_history else 0,
            "collections": credit_history.collections if credit_history else 0,
            "monthly_income": float(risk_indicators.monthly_income) if risk_indicators and risk_indicators.monthly_income else 0,
            "monthly_debt_payments": float(risk_indicators.monthly_debt_payments) if risk_indicators and risk_indicators.monthly_debt_payments else 0,
            "debt_to_income_ratio": float(risk_indicators.debt_to_income_ratio) if risk_indicators and risk_indicators.debt_to_income_ratio else 0,
            "housing_cost_ratio": float(risk_indicators.housing_cost_ratio) if risk_indicators and risk_indicators.housing_cost_ratio else 0,
            "liquid_assets": float(risk_indicators.liquid_assets) if risk_indicators and risk_indicators.liquid_assets else 0,
            "savings_account_balance": float(risk_indicators.savings_account_balance) if risk_indicators and risk_indicators.savings_account_balance else 0,
            "has_collateral": risk_indicators.has_collateral if risk_indicators else False,
            "collateral_value": float(risk_indicators.collateral_value) if risk_indicators and risk_indicators.collateral_value else 0,
            "job_stability_score": risk_indicators.job_stability_score if risk_indicators else 0,
            "industry": risk_indicators.industry if risk_indicators else None,
            "frequent_address_changes": risk_indicators.frequent_address_changes if risk_indicators else 0,
            "fraud_flag": risk_indicators.fraud_flag if risk_indicators else False,
            "fraud_reason": risk_indicators.fraud_reason if risk_indicators else None,
            "loan_amount": float(application.loan_amount) if application.loan_amount else 0,
            "loan_type": application.loan_type.value if application.loan_type else "Personal",
            "loan_purpose": application.loan_purpose
        }

    def _log_agent_results(self, db, application_id: int, results: dict):
        """Log agent results to audit trail"""
        for agent_name, result in results.items():
            if agent_name not in ["applicant_id", "loan_amount", "loan_type"]:
                audit = AuditLog(
                    application_id=application_id,
                    agent_name=agent_name.replace("_", " ").title(),
                    action="Evaluation",
                    details=json.dumps(result.get("analysis", {}))
                )
                db.add(audit)
        db.commit()

    def _extract_score(self, agent_result: dict) -> float:
        """Extract numeric score from agent result"""
        try:
            analysis = agent_result.get("analysis", {})
            if isinstance(analysis, dict):
                for key in ["risk_score", "score", "confidence"]:
                    if key in analysis:
                        score = float(analysis[key])
                        return min(1.0, max(0.0, score / 100.0 if score > 1 else score))
            return 0.5
        except:
            return 0.5
