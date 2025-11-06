from openai import OpenAI
from ai_wayang_single.config.settings import BUILDER_MODEL_CONFIG
from ai_wayang_single.llm.models import WayangPlan
from ai_wayang_single.llm.prompt_loader import PromptLoader

class Builder:
    """
    Builder Agent based on OpenAI's GPT-models.
    The agents build an logical, abstract plan from natural langauge query
    """

    def __init__(self, model: str | None = None, system_prompt: str | None = None):
        self.client = OpenAI()
        self.model = model or BUILDER_MODEL_CONFIG.get("model")
        self.system_prompt = system_prompt or PromptLoader().load_builder_system_prompt()

    def generate_plan(self, prompt: str):
        """
        Generates a logical, abstract Wayang plan from a natural language query.

        Args:
            prompt (str): A query in natural language

        Returns:
            WayangPlan: A logical Wayang plan 

        """

        # Defines params and structured format for the model
        params = {
            "model": self.model,
            "input": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "text_format": WayangPlan
        }

        # Set effort if reasoning model
        effort = BUILDER_MODEL_CONFIG.get("reason_effort")
    
        if effort:
            params["reasoning"] = {"effort": effort}

        # Generate response
        response = self.client.responses.parse(**params)

        # Return response
        return {
            "raw": response,
            "wayang_plan": response.output_parsed
        }

        

