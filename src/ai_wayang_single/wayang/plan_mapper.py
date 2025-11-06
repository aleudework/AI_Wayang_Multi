from ai_wayang_single.llm.models import WayangOperation, WayangPlan
from ai_wayang_single.wayang.operator_mapper import OperatorMapper
from typing import List
import json
import re

class PlanMapper:
    """
    Maps a logical, abstract Wayang plan to executable JSON Wayang plan.
    Can also simplify a JSON Wayang plan to a more abstract version

    """

    def __init__(self, config):
        self.config = config

        self.operator_map = {

            # Input operators
            "jdbcRemoteInput": lambda op: OperatorMapper(op).jdbc_input(self.config["input_config"]),
            "textFileInput": lambda op: OperatorMapper(op).textfile_input(self.config["input_config"]),

            # Unary operators
            "map": lambda op: OperatorMapper(op).map(),
            "flatMap": lambda op: OperatorMapper(op).flatmap(),
            "filter": lambda op: OperatorMapper(op).filter(),
            "reduce": lambda op: OperatorMapper(op).reduce(),
            "reduceBy": lambda op: OperatorMapper(op).reduceby(),
            "groupBy": lambda op: OperatorMapper(op).groupby(),
            "sort": lambda op: OperatorMapper(op).sort(),

            # Binary operators
            "join": lambda op: OperatorMapper(op).join(),

            # Output operators
            "textFileOutput": lambda op: OperatorMapper(op).textfile_output(self.config["output_config"])
        }
        

    def plan_to_json(self, plan: WayangPlan):
        """
        Maps abstract Wayang plan to a executable JSON Wayang plan

        Args:
            plan (WayangPlan): Abstract WayangPlan
        
        Returns:
            json: Executable JSON plan

        """

        # Check if input plan is a WayangPlan model
        if not isinstance(plan, WayangPlan):
            raise ValueError("Abstract, raw plan must be in WayangPlan format")
        
        # Initialize a new JSON plan
        mapped_plan = self._new_plan()

        # Filter operators in abstract plan
        operations = plan.operations

        # Map operators
        mapped_operators = self._map_operators(operations)

        # Add operators to JSON plan
        mapped_plan["operators"] = mapped_operators

        # Return JSON plan
        return mapped_plan
    

    def plan_from_json(self, plan: str) -> WayangPlan:
        """
        Converts a JSON Wayang plan to a more simple, abstract WayangPlan easier for modification.
        
        Args:
            plan (str): Plan in JSON to be converted
        
        Returns:
            Plan in WayangPlan format

        """

        try:
            # Make sure plan is a dict (from json)
            if isinstance(plan, str):
                plan = json.loads(plan)

            # List to store operations
            operations = []

            # Maps each operation to WayangOperation model
            for op in plan["operators"]:
                # Flat nested structure (if called data)
                flat_op_data = {**op, **op.get("data", {})}
                # Filter to only relevant keys in WayangOperations
                op_data = {k: v for k, v in flat_op_data.items() if k in WayangOperation.model_fields}

                ## Handle specific operators 
                # Ensure correct inputFile
                if op_data.get("operatorName") == "textFileInput":
                    # Use flat_op_data because filename is removed
                    filename = flat_op_data["filename"]
                    # Remove path so only name of file is returned
                    filename = filename.split("/")[-1].split(".")[0]
                    op_data["inputFileName"] = filename

                # Ensure only table name in jdbc_input
                if op_data.get("operatorName") == "jdbcRemoteInput" and "table" in op_data:
                    table = op_data["table"]
                    match = re.search(r"FROM\s+([a-zA-Z0-9_]+)", table, re.IGNORECASE)
                    if match:
                        op_data["table"] = match.group(1)

                # Append to the operation list
                operations.append(WayangOperation(**op_data))
            
            # Add to Wayang plan and return
            return WayangPlan(operations=operations, thoughts="Plan converted from JSON")

        except Exception as e:
            raise ValueError("[Error] Not a correctly formatted JSON-plan")


    def _new_plan(self):
        """
        Initialize a new JSON Wayang plan
        
        Returns:
            str: JSON Wayang plan

        """

        return {
            "context": { "platforms": ["java"], "configuration": {} },
            "operators": []
        }


    def _map_operators(self, operations: List[WayangOperation]) -> List:
        """
        Maps operators from abstract form to executable form

        Args:
            operations (List[WayangOperation]): List of operations to be mapped
        
        Returns:
            List: List of operations mapped

        """

        # Intialize mapped operations list
        mapped_operations = []
        
        # Iterate over each operation
        for op in operations:
            try:
                # Get operation name
                name = op.operatorName

                # Skip operator not supported in the architecture
                if name not in self.operator_map:
                    print(f"[WARNING] Couldn't find or map operator")
                    continue
                
                # Map oeprator
                operation = self.operator_map[name](op)

                # Add mapped operator
                if operation:
                    mapped_operations.append(operation)
            
            except Exception as e:
                print(f"[ERROR] Couldn't add operator {op}: {e}")
        
        # Returned list of mapped operators
        return mapped_operations

    

