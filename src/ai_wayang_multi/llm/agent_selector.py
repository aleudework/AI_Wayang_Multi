from openai import OpenAI
from ai_wayang_multi.config.settings import SELECTOR_AGENT_CONFIG
from ai_wayang_multi.llm.prompt_loader import PromptLoader
from ai_wayang_multi.llm.models import DataSources


class Selector:
    """
    Agent to select relevant data sources and to reduce the number of sources for next agents

    """

    def __init__(
        self,
        model: str | None = None,
        reasoning: str | None = None,
        system_prompt: str | None = None,
    ):
        self.client = OpenAI()
        self.model = model or SELECTOR_AGENT_CONFIG.get("model")
        self.reasoning = reasoning or SELECTOR_AGENT_CONFIG.get("reason_effort")
        self.system_prompt = (
            system_prompt or PromptLoader().load_selector_system_prompt()
        )
        self.chat = []

    def set_model_and_reasoning(self, model: str, reasoning: str) -> None:
        """
        Sets objects model and reasoning if any.
        Mostly for testing

        Args:
            model (str): GPT-model
            reasoning (str): Reasoning level if any

        """
        self.model = model
        self.reasoning = reasoning

    def start(self) -> None:
        """
        Clears chat history without resetting agent

        """
        self.chat = [{"role": "system", "content": self.system_prompt}]

    def generate(self, prompt: str):
        """
        Refine user query and select relevant data sources to generate the plan

        Args:
            prompt (str): A query in natural language

        Returns:
            WayangPlanSpecification: Refined user query and selected data sources.

        """

        # Append user prompt to chat
        self.chat.append({"role": "user", "content": prompt})

        # Defines params and structured format for the model
        params = {"model": self.model, "input": self.chat, "text_format": DataSources}

        # Set effort if reasoning model
        effort = self.reasoning

        if effort:
            params["reasoning"] = {"effort": effort}

        # Generate response
        response = self.client.responses.parse(**params)

        # Return response
        return {"raw": response, "selected_data": response.output_parsed}
