"""
ReWOO (Reasoning WithOut Observation) strategy

Plan all actions upfront, then execute:
1. Create complete plan of actions
2. Execute all actions (parallel when possible)
3. Synthesize final answer from results

More efficient than ReAct for multi-step tasks
"""

from datetime import datetime
from typing import Callable, Dict, List
from react_agent_framework.core.reasoning.base import BaseReasoning, ReasoningResult
from react_agent_framework.providers.base import Message


class ReWOOReasoning(BaseReasoning):
    """
    ReWOO reasoning strategy

    Plan-then-execute approach for efficiency
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
        Execute ReWOO reasoning

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
        self._log("ReWOO Reasoning Started")
        self._log(f"{'='*60}")
        self._log(f"Query: {query}\n")

        # Step 1: Create plan
        plan = self._create_plan(query, tool_descriptions, llm_generate, system_prompt)

        self._log(f"\n{'='*60}")
        self._log("📋 PLAN CREATED")
        self._log(f"{'='*60}")
        for i, step in enumerate(plan, 1):
            self._log(f"{i}. {step['action']}({step['input']})")
        self._log("")

        trace.append(
            {
                "phase": "planning",
                "plan": plan,
            }
        )

        # Step 2: Execute plan
        results = self._execute_plan(plan, tools)

        self._log(f"\n{'='*60}")
        self._log("⚙️ EXECUTION RESULTS")
        self._log(f"{'='*60}")
        for i, result in enumerate(results, 1):
            self._log(f"{i}. {result['action']}: {result['result'][:100]}...")
        self._log("")

        trace.append(
            {
                "phase": "execution",
                "results": results,
            }
        )

        # Step 3: Synthesize answer
        answer = self._synthesize_answer(query, plan, results, llm_generate, system_prompt)

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
            metadata={"strategy": "rewoo", "plan_steps": len(plan)},
        )

    def _create_plan(
        self,
        query: str,
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
    ) -> List[Dict[str, str]]:
        """
        Create execution plan

        Args:
            query: User query
            tool_descriptions: Available tools
            llm_generate: LLM function
            system_prompt: System instructions

        Returns:
            List of plan steps
        """
        tools_desc = "\n".join([f"- {name}: {desc}" for name, desc in tool_descriptions.items()])

        planning_prompt = f"""{system_prompt}

Available tools:
{tools_desc}

Create a complete plan to answer this question. List ALL actions needed upfront.

Format each step as:
Step N: Action: [tool name], Input: [input for tool]

Do NOT execute anything yet, just plan.

Question: {query}

Your plan:"""

        messages = [
            Message(role="system", content=planning_prompt),
        ]

        response = llm_generate(messages)

        # Parse plan from response
        plan = []
        lines = response.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line or not line.startswith("Step"):
                continue

            # Parse: "Step N: Action: tool_name, Input: input_text"
            if "Action:" in line and "Input:" in line:
                action_part = line.split("Action:")[1].split("Input:")[0].strip().rstrip(",")
                input_part = line.split("Input:")[1].strip()

                plan.append(
                    {
                        "action": action_part,
                        "input": input_part,
                    }
                )

        return plan

    def _execute_plan(
        self,
        plan: List[Dict[str, str]],
        tools: Dict[str, Callable],
    ) -> List[Dict[str, str]]:
        """
        Execute all steps in plan

        Args:
            plan: List of planned actions
            tools: Available tools

        Returns:
            List of results
        """
        results = []

        for step in plan:
            action = step["action"]
            action_input = step["input"]

            if action in tools:
                try:
                    result = tools[action](action_input)
                except Exception as e:
                    result = f"Error executing {action}: {str(e)}"
            else:
                result = f"Tool '{action}' not found"

            results.append(
                {
                    "action": action,
                    "input": action_input,
                    "result": result,
                }
            )

        return results

    def _synthesize_answer(
        self,
        query: str,
        plan: List[Dict[str, str]],
        results: List[Dict[str, str]],
        llm_generate: Callable,
        system_prompt: str,
    ) -> str:
        """
        Synthesize final answer from results

        Args:
            query: Original query
            plan: Execution plan
            results: Execution results
            llm_generate: LLM function
            system_prompt: System instructions

        Returns:
            Final answer
        """
        # Format results for context
        results_text = "\n\n".join(
            [
                f"Step {i+1}: {r['action']}({r['input']})\nResult: {r['result']}"
                for i, r in enumerate(results)
            ]
        )

        synthesis_prompt = f"""{system_prompt}

You executed a plan to answer this question:

Question: {query}

Here are the results from each step:

{results_text}

Based on these results, provide a complete and accurate answer to the original question.

Answer:"""

        messages = [
            Message(role="system", content=synthesis_prompt),
        ]

        answer = llm_generate(messages)

        return answer.strip()
