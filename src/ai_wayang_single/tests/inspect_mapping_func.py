from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.llm.models import WayangPlan, WayangOperation
from ai_wayang_simple.config.settings import MCP_CONFIG, DEBUGGER_MODEL_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG
import json

config = {"input_config": INPUT_CONFIG, "output_config": OUTPUT_CONFIG}

plan_mapper = PlanMapper(config)

raw_plan = {
            "operations": [
                {
                    "cat": "input",
                    "id": 1,
                    "input": [],
                    "output": [
                        2
                    ],
                    "operatorName": "jdbcRemoteInput",
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
                    "operatorName": "filter",
                    "keyUdf": None,
                    "udf": "(r: org.apache.wayang.basic.data.Record) => { val name = r.getField(1).toString; val alder = r.getField(2).toString.toInt; (name.matches(\".*[aeiouAEIOU].*\")) && alder < 40 }",
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
                        0
                    ],
                    "operatorName": "map",
                    "keyUdf": None,
                    "udf": "(r: org.apache.wayang.basic.data.Record) => r.getField(1).toString",
                    "table": None,
                    "columnNames": []
                }
            ],
            "thoughts": "Load person_test, filter by name containing a vowel and alder < 40, then select navn."
        }

raw_plan2 = {
            "operations": [
                {
                    "cat": "input",
                    "id": 1,
                    "input": [],
                    "output": [
                        2
                    ],
                    "operatorName": "textFileInput",
                    "keyUdf": None,
                    "udf": None,
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "inputFileName": "my_textfile",
                    "columnNames": []
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
                    "operatorName": "flatMap",
                    "keyUdf": None,
                    "udf": "(line: String) => line.toCharArray.filter(_.isLetter).map(_.toUpper).map(_.toString)",
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "fileName": None,
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
                    "operatorName": "map",
                    "keyUdf": None,
                    "udf": "(ch: String) => (ch, 1)",
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "fileName": None,
                    "columnNames": []
                },
                {
                    "cat": "unary",
                    "id": 4,
                    "input": [
                        3
                    ],
                    "output": [
                        5
                    ],
                    "operatorName": "reduceBy",
                    "keyUdf": "(t: (String, Int)) => t._1",
                    "udf": "(a: (String, Int), b: (String, Int)) => (a._1, a._2 + b._2)",
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "fileName": None,
                    "columnNames": []
                },
                {
                    "cat": "unary",
                    "id": 5,
                    "input": [
                        4
                    ],
                    "output": [
                        6
                    ],
                    "operatorName": "sort",
                    "keyUdf": None,
                    "udf": "(t: (String, Int)) => -t._2",
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "fileName": None,
                    "columnNames": []
                },
                {
                    "cat": "unary",
                    "id": 6,
                    "input": [
                        5
                    ],
                    "output": [
                        7
                    ],
                    "operatorName": "map",
                    "keyUdf": None,
                    "udf": "(t: (String, Int)) => s\"${t._1},${t._2}\"",
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "fileName": None,
                    "columnNames": []
                },
                {
                    "cat": "output",
                    "id": 7,
                    "input": [
                        6
                    ],
                    "output": [],
                    "operatorName": "textFileOutput",
                    "keyUdf": None,
                    "udf": None,
                    "thisKeyUdf": None,
                    "thatKeyUdf": None,
                    "table": None,
                    "fileName": "hey",
                    "columnNames": []
                }
            ],
            "thoughts": "Read text file lines, extract uppercase letters, count via reduceBy, sort by descending count using negative key, format, and write to text file."
        }

raw_wayangplan = WayangPlan(**raw_plan)

print(json.dumps(raw_wayangplan.model_dump(), indent=4, ensure_ascii=False))

print("-----")

plan1 = plan_mapper.plan_to_json(raw_wayangplan)
# Pænt print af dict (output fra plan_to_json)
print(json.dumps(plan1, indent=4, ensure_ascii=False))

print("-----")

plan2 = plan_mapper.plan_from_json(plan1)

print(json.dumps(plan2.model_dump(), indent=4, ensure_ascii=False))