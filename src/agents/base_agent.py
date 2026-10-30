import anthropic
import json
from abc import ABC, abstractmethod
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_name: str, system_prompt: str):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.MODEL_ID
        self.messages = []

    def run_evaluation(self, applicant_data: dict, tools: list = None) -> dict:
        """Run agent evaluation with optional tool use"""
        logger.info(f"{self.agent_name} starting evaluation for applicant {applicant_data.get('id')}")

        user_message = self._prepare_prompt(applicant_data)

        try:
            if tools:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=self.system_prompt,
                    tools=tools,
                    messages=[{"role": "user", "content": user_message}]
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )

            result = self._process_response(response)
            logger.info(f"{self.agent_name} completed evaluation")
            return result

        except Exception as e:
            logger.error(f"Error in {self.agent_name}: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def _prepare_prompt(self, applicant_data: dict) -> str:
        """Prepare the user prompt with applicant data"""
        return json.dumps(applicant_data, indent=2, default=str)

    def _process_response(self, response) -> dict:
        """Process Claude's response"""
        result = {
            "agent": self.agent_name,
            "raw_response": None,
            "analysis": None
        }

        for block in response.content:
            if hasattr(block, 'text'):
                result["raw_response"] = block.text
                try:
                    result["analysis"] = json.loads(block.text)
                except json.JSONDecodeError:
                    result["analysis"] = {"text": block.text}
                break

        return result

    @abstractmethod
    def evaluate(self, applicant_data: dict) -> dict:
        """Evaluate applicant data. Must be implemented by subclasses."""
        pass
