import pytest
from ai_wayang_simple.llm.agent_builder import Builder

def test_llm_output():
    llm = Builder()
    prompt = "Fill the plan simple and fast"
    output = llm.generate_plan(prompt)

    print(output)
    print(output["wayang_plan"])

    assert isinstance(output, dict)
    assert "wayang_plan" in output
    assert output["wayang_plan"] is not None