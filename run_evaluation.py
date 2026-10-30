#!/usr/bin/env python
"""
Test script to run evaluation on sample applications
"""

import sys
from src.database.connection import DatabaseConnection
from src.orchestrator import LoanApplicationOrchestrator
from src.utils import get_logger

logger = get_logger(__name__)

def main():
    # Initialize database
    DatabaseConnection.init_db()

    # Create orchestrator
    orchestrator = LoanApplicationOrchestrator()

    # Get application ID from command line or use default
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    logger.info(f"Starting evaluation for application {app_id}")

    # Run evaluation
    result = orchestrator.evaluate_application(app_id)

    if result.get("status") == "completed":
        logger.info("✅ Evaluation completed successfully")
        print("\n" + "="*80)
        print("FINAL DECISION")
        print("="*80)
        decision = result.get("final_decision", {})
        print(f"Classification: {decision.get('final_classification')}")
        print(f"Confidence: {decision.get('confidence'):.1%}")
        print(f"Summary: {decision.get('decision_summary')}")
        print("="*80 + "\n")

        print("Agent Results Summary:")
        print("-"*80)
        for agent, analysis in result.get("agent_results", {}).items():
            print(f"\n{agent.upper()}:")
            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    print(f"  {key}: {value}")
    else:
        logger.error(f"Evaluation failed: {result.get('error')}")
        print(f"❌ Error: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
