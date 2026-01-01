# Import libraries
from mcp.server.fastmcp import FastMCP
from ai_wayang_multi.config.settings import MCP_CONFIG, INPUT_CONFIG, OUTPUT_CONFIG, DEBUGGER_AGENT_CONFIG
from ai_wayang_multi.llm.agent_specifier import Specifier
from ai_wayang_multi.llm.agent_selector import Selector
from ai_wayang_multi.llm.agent_decomposer import Decomposer
from ai_wayang_multi.llm.agent_builder import Builder
from ai_wayang_multi.llm.agent_refiner import Refiner
from ai_wayang_multi.llm.agent_debugger import Debugger
from ai_wayang_multi.wayang.step_handler import StepHandler
from ai_wayang_multi.wayang.plan_mapper import PlanMapper
from ai_wayang_multi.wayang.plan_validator import PlanValidator
from ai_wayang_multi.wayang.wayang_executor import WayangExecutor
from ai_wayang_multi.utils.logger import Logger
from ai_wayang_multi.utils.schema_loader import SchemaLoader
from typing import Optional
import os

# Initialize MCP-server
mcp = FastMCP(name="AI-Wayang-Simple", 
              port=MCP_CONFIG.get("port"))

# Initialize configs
config = {
    "input_config": INPUT_CONFIG,
    "output_config": OUTPUT_CONFIG
}

# Initialize agents and objects
# Agents are initialized outside the tools to cache system prompts (and save token cost)
specifier_agent = Specifier() # Initialize specifier agent
selector_agent = Selector() # Initialize selector agent
decomposer_agent = Decomposer() # Initialize planner agent
builder_agent = Builder() # Initialize builder agent
refiner_agent = Refiner() # Initialize refiner agent
debugger_agent = Debugger() # Initialize debugger agent
step_handler = StepHandler() # Initialize step handler
plan_mapper = PlanMapper(config=config) # Initialize mapper
plan_validator = PlanValidator() # Initialize validator
wayang_executor = WayangExecutor() # Wayang executor

# To store the last sessions output
last_session_result = "Nothing to output"

@mcp.tool()
def query_wayang(describe_wayang_plan: str, model: Optional[str] = "gpt-5-nano", reasoning: Optional[str] = "low", use_debugger: Optional[str] = "True") -> str:
    """
    Generates and execute a Wayang plan based on given query in national language.
    The query provided must be in Englis

    Args:
        describe_wayang_plan (str):
            A detailed description in English of what query or task should be executed
    
    Returns:
        Execution output from Wayang server
    
    Notes:
    - This tool builds and execute a query based on a description 
    - Runetime is typically a few minutes
    - Be as detailed in the description as possible
    """

    # Declaring variable as global
    global last_session_result

    # Sets parametre (mainly for evaluation)
    specifier_agent.set_model_and_reasoning(model, reasoning)
    selector_agent.set_model_and_reasoning(model, reasoning)
    decomposer_agent.set_model_and_reasoning(model, reasoning)
    builder_agent.set_model_and_reasoning(model, reasoning)
    refiner_agent.set_model_and_reasoning(model, reasoning)
    debugger_agent.set_model_and_reasoning(model, reasoning)

    try:
        # Set up logger 
        logger = Logger()
        logger.add_message("User query: Plan description from client LLM", describe_wayang_plan)
        logger.add_message("Architecture", {"model": model, "architecture": "Multi", "debugger": use_debugger})
        print("[INFO] Starting generating Wayang plans")
        
        # Initialize important variables
        status_code = None # Status code from validator or Wayang server
        result = None # Variable to store output
        version = 1 # Keeping track of plan version for this session



        ### --- Specifier Agent, to specify clearly write the user's request --- ###

        specifier_agent.start() # New specifier session
        response = specifier_agent.generate(describe_wayang_plan)
        refined_query = response.get("refined_query") # Get only the relevant resonse

        # Logging
        print("[INFO] SpecifierAgent: User query refined and clearified")
        logger.add_message("Agent Usage: SpecifierAgent Information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
        logger.add_message("Agent: SpecifierAgent Output", refined_query)        



        ### --- Selector Agent, to select relevant data sources --- ###

        selector_agent.start() # New selector session
        response = selector_agent.generate(describe_wayang_plan)
        data_selected = response.get("selected_data") # The selected data from agent

        # Logging
        print("[INFO] SelectorAgent: Relevant data sources selected")
        logger.add_message("Agent Usage: SelectorAgent Information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
        logger.add_message("Agent: SelectorAgent Output", data_selected.model_dump())


        
        ### --- Decomposer Agent, to decompose the user's query into subtasks / steps for Builders --- ###

        decomposer_agent.start() # New decomposer session
        response = decomposer_agent.generate(refined_query, data_selected)
        highlevel_plan = response.get("response")

        # Logging
        print("[INFO] DecomposerAgent: High level Wayang Plan built")
        logger.add_message("Agent Usage: DecomposerAgent Information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
        logger.add_message("Agent: DecomposerAgent Output", highlevel_plan.model_dump())



        ### --- Builder Agents, builds the Wayang Plan from the high level plan --- ###

        builder_agent.start(refined_query, data_selected) # New builder session
        steps = highlevel_plan.steps # Get the step list from plan

        # Build step dependencies map
        step_dependencies = step_handler.build_step_dependency_map(steps)

        # Build step queue
        step_queue = step_handler.build_step_queue(step_dependencies)

        # Logging
        print("[INFO] StepHandler created step dependencies and queue")
        logger.add_message("Class: StepHandler created step dependencies and queue", f"Step queue {step_queue}")

        # Map for generated subplans
        subplans = {}

        # Go over queue for each steps and generate subplans
        for step_id in step_queue:
            # Current step variable
            current_step = None

            # Get current step from Decomposer
            for step in steps:
                if step.step_id == step_id:
                    current_step = step
                    break
            
            # Get previously generated operations in a list to add context for this subplan 
            previous_steps = step_handler.get_steps(step_dependencies.get(step_id, []), subplans, step_queue)

            # Generate plan
            response = builder_agent.generate(current_step, previous_steps)
            subplan = response.get("wayang_subplan")

            # Add subplan to subplans
            subplans = step_handler.update_subplan(step_id, subplan, subplans)

            # Logging
            print(f"[INFO] BuilderAgent: Step or subplan generated for step {step_id}")
            logger.add_message(f"Agent Usage: BuilderAgent Information step {step_id}", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
            logger.add_message(f"Agent: BuilderAgent Subplan for step {step_id}", subplan.model_dump())

        
        # Merge subplans into a final Wayang Plan based on queue order
        full_plan = step_handler.step_merger(step_queue, subplans)

        # Logging
        print("[INFO] StepHandler merged subplans to full plan")
        logger.add_message("Class: StepHandler merged subplans to full plan", full_plan.model_dump())



        ### --- Refiner Agent: Refine the full plan to be executable in Wayang Server --- ###

        refiner_agent.start(data_selected) # New refiner session

        # Refine Wayang Plan
        response = refiner_agent.generate(refined_query, full_plan)
        refined_plan = response.get("wayang_plan")

        # Logging
        print("[INFO] RefinerAgent: Refiner Agent refined main wayang plan")
        logger.add_message("Agent Usage: RefinerAgent Information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
        logger.add_message("Agent: RefinerAgent Output", refined_plan.model_dump())



        ### --- Map Raw Plan to Executable Plan --- ###

        # Map plan
        print("[INFO] Refined Plan Mapping")
        wayang_plan = plan_mapper.plan_to_json(refined_plan)

        # Logging
        print("[INFO] Plan mapped")
        logger.add_message("Class: PlanMapper Mapped the refined plan finalized for execution", {"version": 1, "plan": wayang_plan})



        ### --- Validate Plan --- ###

        # Logging
        print("[INFO] Validating plan")
        logger.add_message(f"Class: PlanValidator Validates Plan", "")


        # Validate plan before execution
        val_success, val_errors = plan_validator.validate_plan(wayang_plan)

        # Tell and log validation result
        if val_success:
            print("[INFO] Plan validated sucessfully")

        else:
            # Logging if validation fails
            print(f"[INFO] Plan {version} failed validation: {val_errors}")
            logger.add_message(f"Err: PlanValidator Val error. Failed validation", {"version": version, "errors": val_errors})
            status_code = 400



        ### --- Execute Plan If Validated Successfully --- ###

        if val_success:
            # Execute plan in Wayang
            print("[INFO] Plan sent to Wayang for execution")
            status_code, result = wayang_executor.execute_plan(wayang_plan)
            logger.add_message("Wayang: Wayang plan sent to Wayang", "")
            
            # Log if plan couldn't execute
            if status_code != 200:
                print(f"[INFO] Couldn't execute plan succesfully, status {status_code}")
                logger.add_message("Err: Wayang error. Plan executed unsucessful", {"status_code": status_code, "output": result})
        


        ### --- Debug Plan --- ###
        
        # Check if debugger should be used
        #use_debugger = DEBUGGER_AGENT_CONFIG.get("use_debugger")

        # Use debugger if true
        if use_debugger == "True" and status_code != 200:

            # Start logging
            print("[INFO] Using Debugger Agent to fix plan")

            # Set debugging parameters
            max_itr = int(DEBUGGER_AGENT_CONFIG.get("max_itr")) # Get max iterations for debugging
            debugger_agent.start() # Initialize debugger session 
            debugger_agent.set_vesion(version) # Set version to number of plans already created this session

            # Debug and execute plan up to max iterations
            for _ in range(max_itr):

                # Map and anonymize plan from executable json to raw format
                failed_plan = plan_mapper.plan_from_json(wayang_plan)
                logger.add_message("Class: PlanMapper Simplifies to JSON", "")
                print(f"[INFO] PlanMapper Simplifies to JSON")

                # Debug plan
                response = debugger_agent.debug_plan(refined_query, failed_plan, wayang_errors=result, val_errors=val_errors) # Debug plan
                version = debugger_agent.get_version() # Current plan version
                raw_plan = response.get("wayang_plan") # Get only the debugged plan
                print("[INFO] Plan debugged by Debugger")

                # Get current plan version
                version = debugger_agent.get_version()

                # Logging
                logger.add_message(f"Agent Usage: DebuggerAgent. Debug version {version} information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
                logger.add_message(f"Agent: DebuggerAgent's thoughts, plan {version}", {"version": version, "thoughts": raw_plan.thoughts})
                logger.add_message(f"Agent: DebuggerAgent's plan: {version}", {"version": version, "plan": raw_plan.model_dump()})

                # Refines the debugged plan by Refiner Agent
                response = refiner_agent.generate(refined_query, raw_plan)
                refined_plan = response.get("wayang_plan")
                print("[INFO] Plan refined by Refiner")

                # Logging
                
                logger.add_message(f"Agent Usage: RefinerAgent. Refines version {version} information", {"model": str(response["raw"].model), "usage": response["raw"].usage.model_dump()})
                logger.add_message(f"Agent: RefinerAgent's plan: {version}", {"version": version, "plan": refined_plan.model_dump()})

                # Map the debugged plan to JSON-format
                wayang_plan = plan_mapper.plan_to_json(refined_plan)

                print("[INFO] Plan re-mapped by PlanMapper")
                logger.add_message("Class: PlanMapper Mapped Debug and Refined Plan", {"version": version, "plan": wayang_plan})
                
                # Validate debugged plan
                val_success, val_errors = plan_validator.validate_plan(wayang_plan)

                print(f"[INFO] PlanValidator validates debugger's plan")
                logger.add_message("Class: PlanValidator Validated Debugger Plan", "")

                # If plan failed validation, continue debugging
                if not val_success:
                    # Logging failure
                    print(f"[INFO] Plan {version} failed validation: {val_errors}")
                    logger.add_message(f"Err: PlanValidator Val error. Failed validation", {"version": version, "errors": val_errors})
                    status_code = 400
                    result = None
                    continue

                print(f"[INFO] Succesfully validated and debugged plan, version {version}") # If plan validation succesfully
                
                # Execute Wayang plan
                print(f"[INFO] Plan {version} sent to Wayang for execution")
                status_code, result = wayang_executor.execute_plan(wayang_plan)
                logger.add_message("Wayang: Wayang plan sent to Wayang", "")

                # Break debugging loop if sucessfully executed
                if status_code == 200:
                    break

                # Continue debugging if execution failed
                if status_code != 200:
                    print(f"[ERROR] Couldn't execute plan version {version}, status {status_code}")
                    logger.add_message(f"Err: Wayang error. Plan version {version} executed unsucessful", {"status_code": status_code, "output": result})
                    continue
            
        # Return output when success
        if status_code == 200:
            print("[INFO] Plan succesfully executed")
            logger.add_message("Final: Sucessful. Plan executed", "Success")

            # Return result to client
            return result

        # If failed to execute plan after debugging
        if status_code != 200:
            print(f"[ERROR] Couldn't execute plan succesfully, status {status_code}")
            logger.add_message("Final: Unsucessful. Plan executed unsucessful", {"status_code": status_code, "output": result})
            
            # Return failure to client
            return "Couldn't execute wayang plan succesfully"

    except Exception as e:
        # Prints if an exception happened
        print(f"[ERROR] {e}")

        # Return error to client LLM to explain to user
        msg = f"An error occured, explain for the user: {e}"
        temp_out = msg # temp
        # Return error message to client
        return msg


@mcp.tool()
def get_wayang_result() -> str:
    """
    Get the current result from query_wayang or from the Wayang execution.

    Returns:
        The output result or output error from Wayang
    
    """

    return last_session_result

@mcp.tool()
def load_schemas() -> str:
    """
    Loads schemas with examples from database and textfiles for agents.

    Returns
        str: Informationen on number of added schemas
    """
    try:

        # Create output folder path
        base_dir = os.path.dirname(os.path.abspath(__file__)) # Path to server file
        relative_path = os.path.join(base_dir, "..", "..", "..", "data", "schemas") # Relative path to output folder
        output_folder = os.path.abspath(relative_path) # Absolute path to folder
        
        # Initialize schema loader
        schema_loader = SchemaLoader(config, output_folder)
        
        # For output messages
        msg = []

        # Load jdbc tables
        msg.append(schema_loader.get_and_save_table_schemas())

        # Load textfiles
        msg.append(schema_loader.get_and_save_textfile_schemas())

        # Returns msg as str to client
        return "\n".join(msg)

    except Exception as e:
        # Print and returns error
        print(f"[ERROR] {e}")
        return f"An error occured, error: {e}"