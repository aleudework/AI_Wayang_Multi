"""
Models to ensure structured format in agents
"""

from pydantic import BaseModel, Field
from typing import List, Optional

### For Selector Agent

class DataSources(BaseModel):
    tables: Optional[List[str]] = Field(default = [], description = "Table names required to generate the Wayang Plan")
    textfiles: Optional[List[str]] = Field(default = [], description = "Textfiles names required to generate the Wayang Plan")
    thoughts: str = Field(default=None, description="Describe your thoughts on why you selected these data sources")


### For Decomposer Agent

class Step(BaseModel):
    step_id: int = Field(default=None, descrption="A number to represent this step in the plan")
    input: List[int] = Field(default=None, description="The previous step_id needed for this step. If a binary operation step, write both step_ids")
    output: List[int] = Field(default=None, description="The step_id of the following step. Which uses this output as an input")
    step_description: str = Field(default=None, description="A detailed description of the logic on what this step must do to fullfil input and output")
    expected_input: str = Field(default=None, description="A description of what input is expected for this step of the plan")
    expected_output: str = Field(default=None, description="A description of what output is expected to be generated for this step of the plan")

class WayangPlanHighLevel(BaseModel):
    steps: List[Step] = Field(default=None, description="The steps needed to generate the plan")
    thoughts: str = Field(default=None, description="Describe your thoughts on how you ended up with this plan. Keep it short")


### For Builder Agent

class WayangOperation(BaseModel):
    cat: str
    id: int
    input: List[int] = Field(default_factory=list)
    output: List[int] = Field(default_factory=list)
    operatorName: str
    keyUdf: Optional[str] = None
    udf: Optional[str] = None
    thisKeyUdf: Optional[str] = None
    thatKeyUdf: Optional[str] = None
    table: Optional[str] = None
    inputFileName: Optional[str] = None
    columnNames: List[str] = Field(default_factory=list)

class WayangPlan(BaseModel):
    operations: List[WayangOperation]
    thoughts: str = Field(default=None, description="Describe your thoughts on how you ended up with this plan. Keep it short")