from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.llm.models import WayangOperation, WayangPlan
from ai_wayang_simple.config.settings import MCP_CONFIG, DEBUGGER_MODEL_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG
from pydantic import BaseModel, Field
from typing import List, Optional

import json


config = {"input_config": INPUT_CONFIG, "output_config": OUTPUT_CONFIG}

plan_mapper = PlanMapper(config)

draft = {
            "operations": [
                {
                    "cat": "input",
                    "id": 1,
                    "input": [],
                    "output": [
                        2
                    ],
                    "operationName": "jdbcRemoteInput",
                    "keyUdf": None,
                    "udf": None,
                    "table": "person_test",
                    "columnNames": [
                        "id",
                        "navn",
                        "alder",
                        "email",
                        "created_at"
                    ]
                },
                {
                    "cat": "unary",
                    "id": 2,
                    "input": [
                        1
                    ],
                    "output": [
                        3
                    ],
                    "operationName": "map",
                    "keyUdf": None,
                    "udf": "(r: org.apache.wayang.basic.data.Record) => r.getField(1).toString.substring(0,1)",
                    "table": None,
                    "columnNames": []
                },
                {
                    "cat": "unary",
                    "id": 3,
                    "input": [
                        2
                    ],
                    "output": [
                        4
                    ],
                    "operationName": "reduceBy",
                    "keyUdf": "(s: String) => s",
                    "udf": "(a: String, b: String) => a",
                    "table": None,
                    "columnNames": []
                },
                {
                    "cat": "output",
                    "id": 4,
                    "input": [
                        3
                    ],
                    "output": [],
                    "operationName": "textFileOutput",
                    "keyUdf": None,
                    "udf": None,
                    "table": None,
                    "columnNames": []
                }
            ],
            "description_of_plan": "Plan to output unique first characters of the navn column from person_test to a text file."
        }

plan = WayangPlan(**draft)

output = plan_mapper.map(plan)

print(json.dumps(output, indent=4))
