from openai import OpenAI
from ai_wayang_multi.config.settings import SPECIFIER_AGENT_CONFIG
from ai_wayang_multi.llm.prompt_loader import PromptLoader
from ai_wayang_multi.llm.models import WayangPlanSpecification

class Specifier:

        def __init__(self, model: str | None = None, system_prompt: str | None = None):
            self.client = OpenAI()
            self.model = model or SPECIFIER_AGENT_CONFIG.get("model")
            self.system_prompt = system_prompt or PromptLoader().load_specifier_system_prompt()


        def generate(self, prompt: str):
            """
            Refine user query and select relevant data sources to generate the plan

            Args:
                prompt (str): A query in natural language

            Returns:
                WayangPlanSpecification: Refined user query and selected data sources.

            """

            # Defines params and structured format for the model
            params = {
                "model": self.model,
                "input": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "text_format": WayangPlanSpecification
            }

            # Set effort if reasoning model
            effort = SPECIFIER_AGENT_CONFIG.get("reason_effort")
        
            if effort:
                params["reasoning"] = {"effort": effort}

            # Generate response
            response = self.client.responses.parse(**params)

            # Return response
            return {
                "raw": response,
                "response": response.output_parsed
            }