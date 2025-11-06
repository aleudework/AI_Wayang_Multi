import pytest
from ai_wayang_simple.llm.prompt_loader import PromptLoader

pl = PromptLoader()

print(pl.load_few_shot_prompt())

print(pl.load_builder_system_prompt())