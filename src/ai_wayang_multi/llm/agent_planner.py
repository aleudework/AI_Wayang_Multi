from openai import OpenAI
from ai_wayang_multi.config.settings import PLANNER_AGENT_CONFIG
from ai_wayang_multi.llm.models import AbstractWayangPlan
from ai_wayang_multi.llm.prompt_loader import PromptLoader


class Planner:

    def __init__(self, model: str | None = None, system_prompt: str | None = None, version: int | None = None):
        self.client = OpenAI()
        self.model = model or PLANNER_AGENT_CONFIG.get("model")
        self.system_prompt = system_prompt or None

    
    def start(self) -> None:
        """
        Cleans Planner Agent for this section

        """

        self.system_prompt = PromptLoader().load_planner_system_prompt()
        self.chat = [{"role": "system", "content": self.system_prompt}]


    
    def generate(self, query: str, data_sources: dict):
        """
        
        """
        # Load standard prompt
        pl = PromptLoader()
        prompt = pl.load_planner_prompt(query, data_sources)

        # Defines params and structured format for the model
        params = {
            "model": self.model,
            "input": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "text_format": AbstractWayangPlan
        }        

        # Set effort if reasoning model
        effort = PLANNER_AGENT_CONFIG.get("reason_effort")
    
        if effort:
            params["reasoning"] = {"effort": effort}

        # Generate response
        response = self.client.responses.parse(**params)

        # Return response
        return {
            "raw": response,
            "abstract_plan": response.output_parsed
        }

