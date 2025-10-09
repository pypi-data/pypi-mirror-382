"""
Plan-and-Execute strategy

Detailed planning with adaptive execution:
1. Create detailed plan with steps
2. Execute steps one by one
3. Update plan based on results
4. Continue until complete

Similar to ReWOO but with plan refinement
"""

from datetime import datetime
from typing import Callable, Dict, List, Optional
from react_agent_framework.core.reasoning.base import BaseReasoning, ReasoningResult
from react_agent_framework.providers.base import Message


class PlanExecuteReasoning(BaseReasoning):
    """
    Plan-and-Execute reasoning strategy

    Adaptive planning with step-by-step execution
    """

    def reason(
        self,
        query: str,
        tools: Dict[str, Callable],
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
        **kwargs,
    ) -> ReasoningResult:
        """
        Execute Plan-and-Execute reasoning

        Args:
            query: The question/task
            tools: Dictionary of available tools
            tool_descriptions: Tool descriptions
            llm_generate: Function to call LLM
            system_prompt: System instructions

        Returns:
            ReasoningResult with answer
        """
        start_time = datetime.now()
        trace = []

        self._log(f"\n{'='*60}")
        self._log("Plan-and-Execute Reasoning Started")
        self._log(f"{'='*60}")
        self._log(f"Query: {query}\n")

        # Step 1: Create initial plan
        plan = self._create_plan(query, tool_descriptions, llm_generate, system_prompt)

        self._log(f"\n{'='*60}")
        self._log("📋 INITIAL PLAN")
        self._log(f"{'='*60}")
        for i, step in enumerate(plan, 1):
            status = "✓" if step.get("completed") else "○"
            self._log(f"{status} Step {i}: {step['description']}")
        self._log("")

        trace.append(
            {
                "phase": "initial_planning",
                "plan": plan,
            }
        )

        # Step 2: Execute plan step by step
        execution_results = []

        for i, step in enumerate(plan):
            self._log(f"\n{'='*60}")
            self._log(f"▶️ Executing Step {i+1}: {step['description']}")
            self._log(f"{'='*60}")

            # Execute step
            result = self._execute_step(step, tools, tool_descriptions, llm_generate, system_prompt)

            self._log(f"Result: {result[:200]}...")

            execution_results.append(
                {
                    "step": i + 1,
                    "description": step["description"],
                    "result": result,
                }
            )

            step["completed"] = True
            step["result"] = result

            # Check if we should update plan
            if i < len(plan) - 1:  # Not the last step
                plan_update = self._should_update_plan(
                    query, plan, execution_results, llm_generate, system_prompt
                )

                if plan_update:
                    self._log("\n🔄 Plan updated based on results")
                    plan = plan_update

                    trace.append(
                        {
                            "phase": "plan_update",
                            "updated_plan": plan,
                            "after_step": i + 1,
                        }
                    )

        trace.append(
            {
                "phase": "execution",
                "results": execution_results,
            }
        )

        # Step 3: Synthesize final answer
        answer = self._synthesize_answer(
            query, plan, execution_results, llm_generate, system_prompt
        )

        self._log(f"\n{'='*60}")
        self._log("✅ FINAL ANSWER")
        self._log(f"{'='*60}")
        self._log(f"{answer}\n")

        trace.append(
            {
                "phase": "synthesis",
                "answer": answer,
            }
        )

        return ReasoningResult(
            answer=answer,
            iterations=len(plan),
            success=True,
            trace=trace,
            start_time=start_time,
            end_time=datetime.now(),
            metadata={"strategy": "plan_execute", "plan_steps": len(plan)},
        )

    def _create_plan(
        self,
        query: str,
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
    ) -> List[Dict]:
        """Create detailed execution plan"""
        tools_desc = "\n".join([f"- {name}: {desc}" for name, desc in tool_descriptions.items()])

        planning_prompt = f"""{system_prompt}

Available tools:
{tools_desc}

Create a detailed plan to answer this question. Break it down into clear steps.

Format:
Step 1: [Description of what to do]
Step 2: [Description of what to do]
...

Question: {query}

Your plan:"""

        messages = [Message(role="system", content=planning_prompt)]

        response = llm_generate(messages)

        # Parse plan
        plan = []
        lines = response.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("Step"):
                # Extract step description
                if ":" in line:
                    description = line.split(":", 1)[1].strip()
                    plan.append(
                        {
                            "description": description,
                            "completed": False,
                            "result": None,
                        }
                    )

        return plan

    def _execute_step(
        self,
        step: Dict,
        tools: Dict[str, Callable],
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
    ) -> str:
        """Execute a single plan step"""
        tools_desc = "\n".join([f"- {name}: {desc}" for name, desc in tool_descriptions.items()])

        execution_prompt = f"""{system_prompt}

Available tools:
{tools_desc}

Execute this step using the appropriate tool:

Step: {step['description']}

Provide the tool name and input in this format:
Tool: [tool name]
Input: [input for tool]"""

        messages = [Message(role="system", content=execution_prompt)]

        response = llm_generate(messages)

        # Parse tool and input
        tool_name = None
        tool_input = ""

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("Tool:"):
                tool_name = line.split(":", 1)[1].strip()
            elif line.startswith("Input:"):
                tool_input = line.split(":", 1)[1].strip()

        # Execute tool
        if tool_name and tool_name in tools:
            try:
                result = tools[tool_name](tool_input)
                return result
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return f"Could not execute step: {response}"

    def _should_update_plan(
        self,
        query: str,
        current_plan: List[Dict],
        execution_results: List[Dict],
        llm_generate: Callable,
        system_prompt: str,
    ) -> Optional[List[Dict]]:
        """
        Check if plan should be updated based on results

        Returns updated plan or None if no update needed
        """
        # Format current state
        results_text = "\n".join(
            [
                f"Step {r['step']}: {r['description']}\nResult: {r['result'][:100]}"
                for r in execution_results
            ]
        )

        remaining_steps = "\n".join(
            [
                f"Step {i+len(execution_results)+1}: {s['description']}"
                for i, s in enumerate(current_plan[len(execution_results) :])
            ]
        )

        update_prompt = f"""{system_prompt}

Question: {query}

Completed steps:
{results_text}

Remaining planned steps:
{remaining_steps}

Based on the results so far, should we update the remaining plan?

Respond with either:
1. "NO UPDATE" if the plan is still good
2. An updated list of remaining steps if changes are needed

Your response:"""

        messages = [Message(role="system", content=update_prompt)]

        response = llm_generate(messages)

        # Check if update is needed
        if "NO UPDATE" in response.upper():
            return None

        # Parse updated plan
        updated_steps = []
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("Step"):
                if ":" in line:
                    description = line.split(":", 1)[1].strip()
                    updated_steps.append(
                        {
                            "description": description,
                            "completed": False,
                            "result": None,
                        }
                    )

        if updated_steps:
            # Combine completed steps with updated remaining steps
            completed_steps = current_plan[: len(execution_results)]
            return completed_steps + updated_steps

        return None

    def _synthesize_answer(
        self,
        query: str,
        plan: List[Dict],
        execution_results: List[Dict],
        llm_generate: Callable,
        system_prompt: str,
    ) -> str:
        """Synthesize final answer from execution results"""
        results_text = "\n\n".join(
            [
                f"Step {r['step']}: {r['description']}\nResult: {r['result']}"
                for r in execution_results
            ]
        )

        synthesis_prompt = f"""{system_prompt}

Question: {query}

Executed plan and results:
{results_text}

Based on these results, provide a complete answer to the original question.

Answer:"""

        messages = [Message(role="system", content=synthesis_prompt)]

        answer = llm_generate(messages)

        return answer.strip()
