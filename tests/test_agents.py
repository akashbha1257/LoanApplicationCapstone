import pytest
from src.agents import (
    CreditAnalysisAgent,
    RiskAssessmentAgent,
    ComplianceAgent,
    FraudDetectionAgent,
    DecisionAgent
)

def test_credit_agent_initialization():
    """Test credit agent initialization"""
    agent = CreditAnalysisAgent()
    assert agent.agent_name == "Credit Analysis Agent"
    assert agent.system_prompt is not None

def test_risk_agent_initialization():
    """Test risk agent initialization"""
    agent = RiskAssessmentAgent()
    assert agent.agent_name == "Risk Assessment Agent"
    assert agent.system_prompt is not None

def test_compliance_agent_initialization():
    """Test compliance agent initialization"""
    agent = ComplianceAgent()
    assert agent.agent_name == "Compliance Agent"
    assert agent.system_prompt is not None

def test_fraud_agent_initialization():
    """Test fraud agent initialization"""
    agent = FraudDetectionAgent()
    assert agent.agent_name == "Fraud Detection Agent"
    assert agent.system_prompt is not None

def test_decision_agent_initialization():
    """Test decision agent initialization"""
    agent = DecisionAgent()
    assert agent.agent_name == "Decision Agent"
    assert agent.system_prompt is not None

def test_decision_agent_synthesize():
    """Test decision agent synthesis logic"""
    agent = DecisionAgent()

    # Mock agent results
    results = {
        "credit_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "credit_rating": "A"
            }
        },
        "risk_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "risk_level": "LOW"
            }
        },
        "compliance_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "compliance_status": "PASS"
            }
        },
        "fraud_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "fraud_risk_level": "LOW"
            }
        }
    }

    decision = agent.synthesize_decision(results)

    assert "final_classification" in decision
    assert decision["final_classification"] in ["APPROVED", "REJECTED", "MANUAL_REVIEW"]
    assert "confidence" in decision

def test_decision_agent_synthesize_with_rejection():
    """Test decision agent rejects when one agent rejects"""
    agent = DecisionAgent()

    results = {
        "credit_agent": {
            "analysis": {
                "recommendation": "REJECT",
                "credit_rating": "F"
            }
        },
        "risk_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "risk_level": "LOW"
            }
        },
        "compliance_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "compliance_status": "PASS"
            }
        },
        "fraud_agent": {
            "analysis": {
                "recommendation": "APPROVE",
                "fraud_risk_level": "LOW"
            }
        }
    }

    decision = agent.synthesize_decision(results)
    assert decision["final_classification"] == "REJECTED"
