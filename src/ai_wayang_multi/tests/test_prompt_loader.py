import pytest
from ai_wayang_simple.llm.prompt_loader import PromptLoader

def test_prompt_loader_returns_system_prompt():
    loader = PromptLoader() 
    prompt = loader.system_prompt

    print(prompt)

    assert isinstance(prompt, str)
    assert len(prompt) > 0