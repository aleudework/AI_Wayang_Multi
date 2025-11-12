from ai_wayang_multi.llm.models import Step

schema_json = Step.model_json_schema()

print(schema_json)