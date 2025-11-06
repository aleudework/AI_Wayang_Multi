from ai_wayang_single.wayang.plan_mapper import PlanMapper
from ai_wayang_single.config.settings import MCP_CONFIG, DEBUGGER_MODEL_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG

config = {"input_config": INPUT_CONFIG, "output_config": OUTPUT_CONFIG}

plan_mapper = PlanMapper(config)

plan = {
    "context": {
        "platforms": ["java"],
        "configuration": {}
    },
    "operators": [
        {
            "id": 1,
            "cat": "input",
            "input": [],
            "output": [2],
            "operatorName": "jdbcRemoteInput",
            "data": {
                "uri": "jdbc:postgresql://localhost:5432/master_thesis_db",
                "username": "master_thesis",
                "password": "master",
                "table": "(select id, email from person_test) as p",
                "columnNames": ["id", "email"]
            }
        },
        {
            "id": 2,
            "cat": "unary",
            "input": [1],
            "output": [3],
            "operatorName": "map",
            "data": {
                "udf": "(r: org.apache.wayang.basic.data.Record) => { val name = r.getField(0).asInstanceOf[String]; val short = if (name != null) name.substring(0, Math.min(2, name.length)) else null; r.setField(0, short); r }",
                "inputType": None,
                "outputType": None
            }
        },
        {
            "id": 3,
            "cat": "output",
            "input": [2],
            "output": [],
            "operatorName": "textFileOutput",
            "data": {
                "filename": "file:///Users/alexander/Downloads/output_20251021_today.txt"
            }
        }
    ]
}


print ("----")

anon_plan = plan_mapper.anonymize_plan(plan)

print(anon_plan)

un_anon_plan = plan_mapper.unanonymize_plan(anon_plan)

print ("----")

print(un_anon_plan)