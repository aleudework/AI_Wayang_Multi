from typing import List
from ai_wayang_multi.llm.models import Step, WayangPlan

class StepHandler:
    """
    Different function to handle steps from Decomposer and WayangPlanStep from Builder

    """

    def __init__(self):
        pass

    def step_merger(self, queue: List[Step], subplans: dict) -> WayangPlan:
        """
            Merge WayangOperations or Steps into a final WayangPlan ordered by the same as the queue

            Args:
                queue (List[Step]): The queue list of steps with step-flow
                subplans (dict): The generated steps from builder agent
            
            Returns:
                WayangPlan: The final raw Wayang Plan to be mapped
            
        """

        # Initialize operation list
        operations = []

        # Add operations in same order as queue
        for step_id in queue:

            # Continue af step_id no longer in subplan
            if step_id not in subplans:
                continue

            # Add to operations list
            step_operations = subplans[step_id].operations
            operations.extend(step_operations)

        # Build Wayang Plan
        wayang_plan = WayangPlan(
            operations = operations,
            thoughts = ""
        )

        # Return Wayang plan
        return wayang_plan
    
    def update_subplan(self, step_id: int, subplan: WayangPlan, subplans: dict) -> dict:
        """
        Add a new subplan to the subplans. Remove any redudant or old operations.

        Args:
            step_id (int): Id of the current step
            subplan (WayangPlan): The subplan to be inserted
            subplans (dict): Current subplans to updated

        Returns:
            (dict): Updated subplans

        """

        # New dict for updated subplans
        updated_subplans = {}

        # New set for all new or improved operations
        new_ids = set()
        for op in subplan.operations:
            new_ids.add(op.id)
        
        # Add only not improved operations
        for old_step_id, old_subplan in subplans.items():
            kept_ops = []
            for op in old_subplan.operations:
                if op.id not in new_ids:
                    kept_ops.append(op)
            
            # Add operations if there are operations kept
            if len(kept_ops) > 0:
                old_subplan.operations = kept_ops
                updated_subplans[old_step_id] = old_subplan
        
        # Add all new operations
        updated_subplans[step_id] = subplan

        # Return updated operations
        return updated_subplans
        



    def get_steps(self, steps: List, subplans: dict,  queue: List[Step]):
        """
        Show previous steps built, but only relevant steps in queue order.
        Queue order is important to keep the logical flow / directed graph flow

        Args:
            steps (List): Steps to get
            subplans (dict): The list of already generated steps
            queue (List[Step]): The queue of steps to be generated

        Returns:
            List: A list of generated operations in steps-list

            
        """
        # Initalize list to store operations
        operations = []
        
        # Go over each step in queue
        for step_id in queue:
            # If step in queue found in steps
            if step_id in steps:
                # Continue af step_id not in subplans
                if step_id not in subplans:
                    continue
                # Add all generated operations
                operations.extend(subplans[step_id].operations)

        # Return full operation list
        return operations

    
    def build_step_queue(self, step_input_map: dict) -> List:
        """
        Generate a queue in a list of which steps to be built first.

        Args:
            step_input_map (dict): A map with steps and all their dependencies
        
        Returns:
            (List): Queue of steps to be performed in this order

        """
        try:
            total_steps = len(step_input_map) # Number of total steps in plan
            queued_steps = 0 # Number of steps queued
            queue = [] # Queue of all steps

            # Keep queueing steps until empty
            while queued_steps < total_steps:
                # Intialize variable for step_id to queue
                step_to_queue = None

                # Find the step ready for queue
                for step_id in list(step_input_map.keys()):
                    # Found step ready for queue
                    if len(step_input_map[step_id]) == 0:
                        step_to_queue = step_id
                        del step_input_map[step_id] # Delete from the step_map used for iteration
                        break
                
                # Go to exeception if no step is ready for queue 
                if step_to_queue is None:
                    raise ValueError("Logical input flow in WayangPlanHighLight doesn't match")

                # Remove the step added to queue from all other steps
                for step_id, inputs in step_input_map.items():
                    for input in inputs[:]:
                        if input == step_to_queue:
                            inputs.remove(input)
                
                # Add step to queue and increase number of queued steps
                queue.append(step_to_queue)
                queued_steps += 1

            return queue
            
        except Exception as e:
            print(f"[Error Step Queue] {e}")

            # If an error occured, just return the queue in arbitrary step order
            queue = []
            for step_id, _ in step_input_map.items():
                queue.append(step_id)
            
            return queue


    def build_step_dependency_map(self, steps: List[Step]) -> dict:
        """
        Generate a dict for all steps and which dependencies they have.
        Used to find which input they should have when builded

        Args:
            steps (List[Step]): A list of all steps from HighLevelWayangPlan.
        
        Returns:
            dict: A dict of all steps and their dependencies

        """

        # Create a map of all steps and their inputs
        step_input_map = {}
        for step in steps:
            step_input_map[step.step_id] = step.depends_on
        
        # Intialize map with all dependencies
        step_dependencies = {}

        # Add all dependencies to step
        for step in steps:
            dependencies = self._get_dependencies(step_input_map, step.step_id, None)
            step_dependencies[step.step_id] = list(dependencies)

        # Return final step input map with all dependencies
        return step_dependencies
        

    
    def _get_dependencies(self, step_input_map: dict, step_id: int, seen=set) -> set:
        """
        Helper function. A recursive function to explore dependencis

        Args:
            step_input_map (dict): Map of steps and their input steps
            step_ind (int): The int of the current step to explore depedencies
            seen (set): A set of all dependencies from a given step

        Return:
            (set): The set of dependencies

        """

        # Generate a new set for seen if None
        if seen is None:
            seen = set()

        # Go over each step and their input
        for current_step in step_input_map.get(step_id, []):
            # Add the current step if not already explored
            if current_step not in seen:
                seen.add(current_step)
                # Explore current steps dependencies
                self._get_dependencies(step_input_map, current_step, seen)
        
        return seen

