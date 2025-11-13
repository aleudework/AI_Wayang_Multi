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
    step_id: int = Field(default=None, descrption="The step_id number for this step. Make sure that the number aligns with previous steps and no duplicates.")
    transformation: str = Field(default=None, description="Describe what kind of transformation is happening in this step [input-transformation, unary-transformations, binary-transformations, output-transformation]")
    depends_on: List[int] = Field(default=None, description="The previous step_id required to perform this step. If a binary operation step, write both step_ids")
    detailed_description: str = Field(default=None, description="A detailed description of the logic or transformation that should happen in this step. Mention the expected input and output also for this transformation.")

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