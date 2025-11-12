import pytest
from ai_wayang_multi.llm.prompt_loader import PromptLoader

pl = PromptLoader()

d = {"tables": ["adresse_test"], "text_files": ["names", "postal_codes"]}

j = pl.load_selected_data_prompt(d)

print(j)
