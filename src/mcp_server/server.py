from src.mcp_server.tools import MCPTools
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LoanApplicationMCPServer:
    """MCP Server for Loan Application System"""

    def __init__(self):
        self.tools = MCPTools()
        self.tools_registry = self._register_tools()

    def _register_tools(self):
        """Register all available tools"""
        return {
            "query_applicant_data": {
                "description": "Query complete applicant information including credit and risk data",
                "params": {"applicant_id": "int"}
            },
            "get_regulatory_rules": {
                "description": "Get all active regulatory rules for compliance checking",
                "params": {}
            },
            "log_decision": {
                "description": "Log agent decision to audit trail",
                "params": {
                    "application_id": "int",
                    "agent_name": "str",
                    "action": "str",
                    "details": "dict"
                }
            },
            "get_loan_details": {
                "description": "Get loan application details",
                "params": {"application_id": "int"}
            },
            "verify_compliance_rule": {
                "description": "Verify if applicant meets a specific regulatory rule",
                "params": {
                    "applicant_id": "int",
                    "rule_id": "int"
                }
            }
        }

    def get_tools(self):
        """Get all registered tools"""
        return self.tools_registry

    def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool by name"""
        logger.info(f"Executing tool: {tool_name} with params: {kwargs}")

        if tool_name == "query_applicant_data":
            return self.tools.query_applicant_data(kwargs.get("applicant_id"))
        elif tool_name == "get_regulatory_rules":
            return self.tools.get_regulatory_rules()
        elif tool_name == "log_decision":
            return self.tools.log_decision(
                kwargs.get("application_id"),
                kwargs.get("agent_name"),
                kwargs.get("action"),
                kwargs.get("details", {})
            )
        elif tool_name == "get_loan_details":
            return self.tools.get_loan_details(kwargs.get("application_id"))
        elif tool_name == "verify_compliance_rule":
            return self.tools.verify_compliance_rule(
                kwargs.get("applicant_id"),
                kwargs.get("rule_id")
            )
        else:
            logger.warning(f"Unknown tool: {tool_name}")
            return {"error": f"Unknown tool: {tool_name}"}

def get_mcp_server():
    """Factory function to get MCP server instance"""
    return LoanApplicationMCPServer()
