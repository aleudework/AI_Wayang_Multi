"""
    Input:
        Operators
        Data
        Few-shot
        User Query
        Step from planner with input (if there is an input)

    Output:
        The output structured in a plan (same as normal builder)

"""


from openai import OpenAI
from ai_wayang_multi.config.settings import BUILDER_AGENT_CONFIG
from ai_wayang_multi.llm.models import WayangPlan, Step
from ai_wayang_multi.llm.prompt_loader import PromptLoader

class Builder:
    """
    Builder Agent based on OpenAI's GPT-models.
    The agents build an logical, abstract plan from natural langauge query
    """

    def __init__(self, model: str | None = None, system_prompt: str | None = None):
        self.client = OpenAI()
        self.model = model or BUILDER_AGENT_CONFIG.get("model")
        self.system_prompt = system_prompt or None
        self.chat = []


    def start(self, query: str, selected_data: dict) -> None:
        """
        Cleans Builder Agent so it only includes system prompt

        Args:
            query (str): The query (refined) of the plan to be built
            selected_data (dict): The data sources to be used selected by Specifier Agent

        """

        self.system_prompt = PromptLoader().load_builder_system_prompt(query, selected_data)
        self.chat = [{"role": "system", "content": self.system_prompt}]

    
    def generate(self, wayang_step: Step) -> WayangPlan:
        """
        
        """


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
        effort = BUILDER_AGENT_CONFIG.get("reason_effort")
    
        if effort:
            params["reasoning"] = {"effort": effort}

        # Generate response
        response = self.client.responses.parse(**params)

        # Return response
        return {
            "raw": response,
            "wayang_plan": response.output_parsed
        }

        

