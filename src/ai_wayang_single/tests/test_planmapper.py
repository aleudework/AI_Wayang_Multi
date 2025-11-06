from ai_wayang_simple.wayang.plan_mapper import PlanMapper
from ai_wayang_simple.config.settings import MCP_CONFIG, JDBC_CONFIG, DEBUGGER_MODEL_CONFIG

mapper = PlanMapper(JDBC_CONFIG)

plan = {
                "context": {
                    "platforms": [
                        "java"
                    ],
                    "configuration": {}
                },
                "operators": [
                    {
                        "id": 1,
                        "cat": "input",
                        "input": [],
                        "output": [
                            2
                        ],
                        "operatorName": "jdbcRemoteInput",
                        "data": {
                            "uri": "jdbc:postgresql://localhost:5432/master_thesis_db",
                            "username": "master_thesis",
                            "password": "master",
                            "table": "(SELECT id, navn, alder, email, created_at FROM person_test) as X",
                            "columnNames": [
                                "id",
                                "navn",
                                "alder",
                                "email",
                                "created_at"
                            ]
                        }
                    },
                    {
                        "id": 2,
                        "cat": "unary",
                        "input": [
                            1, 3
                        ],
                        "output": [
                            3
                        ],
                        "operatorName": "groupBy",
                        "data": {
                            "keyUdf": "(r: org.apache.wayang.basic.data.Record) => r.getField(1)"
                        }
                    },
                    {
                        "id": 3,
                        "cat": "unary",
                        "input": [
                            2
                        ],
                        "output": [
                            4
                        ],
                        "operatorName": "map",
                        "data": {
                            "udf": "(r: org.apache.wayang.basic.data.Record) => r.getField(0)"
                        }
                    },
                    {
                        "id": 4,
                        "cat": "output",
                        "input": [
                            3
                        ],
                        "output": [],
                        "operatorName": "textFileOutput",
                        "data": {
                            "filename": "file:///Users/alexander/Downloads/output_20251101_233233.txt"
                        }
                    }
                ]
            }


validate = mapper.validate_plan(plan)

print(validate)