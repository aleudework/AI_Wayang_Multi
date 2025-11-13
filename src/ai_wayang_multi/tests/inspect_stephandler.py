hlplan = {
    "steps": [
        {"step_id": 1, "input": []},           # uafhængig
        {"step_id": 2, "input": []},           # uafhængig
        {"step_id": 3, "input": [1]},          # afhænger af 1
        {"step_id": 4, "input": [2]},          # afhænger af 2
        {"step_id": 5, "input": [3, 4]},       # afhænger af både 3 og 4
        {"step_id": 6, "input": [2, 5]},       # afhænger af 2 og 5
        {"step_id": 7, "input": [1, 6]},       # afhænger af 1 og 6
        {"step_id": 8, "input": [3, 7]},       # afhænger af 3 og 7
        {"step_id": 9, "input": [5, 8]},       # afhænger af 5 og 8
        {"step_id": 10, "input": [9]},         # afhænger af 9
        {"step_id": 11, "input": [4, 7]},      # afhænger af 4 og 7
        {"step_id": 12, "input": [6, 11]},     # afhænger af 6 og 11
        {"step_id": 13, "input": [12, 9]},     # afhænger af 12 og 9
        {"step_id": 14, "input": [10, 13]},    # afhænger af 10 og 13
        {"step_id": 15, "input": [8, 11]},     # afhænger af 8 og 11
        {"step_id": 16, "input": [14, 15]},    # afhænger af 14 og 15
        {"step_id": 17, "input": [16]},        # afhænger af 16
        {"step_id": 18, "input": [17, 7]},     # afhænger af 17 og 7
        {"step_id": 19, "input": [18, 10]},    # afhænger af 18 og 10
        {"step_id": 20, "input": [19, 21, 5, 3, 2]},
        {"step_id": 21, "input": [2]}
    ],
    "thoughts": "Complex plan with interleaved dependencies for topological sort testing."
}

from ai_wayang_multi.wayang.step_handler import StepHandler
from ai_wayang_multi.llm.models import WayangPlanHighLevel

plan = WayangPlanHighLevel.model_validate(hlplan)

sh = StepHandler()

dep_map = sh.build_step_dependency_map(plan.steps)

print(dep_map)

print('---')

queue = sh.build_step_queue(dep_map)

print(queue)