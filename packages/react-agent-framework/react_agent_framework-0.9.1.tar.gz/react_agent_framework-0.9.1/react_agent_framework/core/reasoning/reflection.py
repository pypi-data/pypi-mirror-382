"""
Reflection strategy

Self-critique and improvement:
1. Generate initial answer
2. Reflect on answer quality
3. Identify improvements
4. Regenerate if needed
5. Repeat until satisfactory

Based on Reflexion paper
"""

from datetime import datetime
from typing import Callable, Dict
from react_agent_framework.core.reasoning.base import BaseReasoning, ReasoningResult
from react_agent_framework.providers.base import Message


class ReflectionReasoning(BaseReasoning):
    """
    Reflection reasoning strategy

    Self-critique loop for answer improvement
    """

    def __init__(
        self,
        max_iterations: int = 3,
        verbose: bool = False,
        reflection_threshold: float = 0.8,
    ):
        """
        Initialize reflection strategy

        Args:
            max_iterations: Maximum reflection cycles
            verbose: Enable verbose output
            reflection_threshold: Quality threshold to stop (0.0-1.0)
        """
        super().__init__(max_iterations=max_iterations, verbose=verbose)
        self.reflection_threshold = reflection_threshold

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
        Execute Reflection reasoning

        Args:
            query: The question/task
            tools: Dictionary of available tools
            tool_descriptions: Tool descriptions
            llm_generate: Function to call LLM
            system_prompt: System instructions

        Returns:
            ReasoningResult with refined answer
        """
        start_time = datetime.now()
        trace = []

        self._log(f"\n{'='*60}")
        self._log("Reflection Reasoning Started")
        self._log(f"{'='*60}")
        self._log(f"Query: {query}\n")

        current_answer = None
        reflections = []

        for iteration in range(self.max_iterations):
            self._log(f"\n{'='*60}")
            self._log(f"CYCLE {iteration + 1}")
            self._log(f"{'='*60}\n")

            # Step 1: Generate or regenerate answer
            if current_answer is None:
                # Initial generation
                current_answer = self._generate_answer(
                    query, tools, tool_descriptions, llm_generate, system_prompt
                )
                self._log(f"📝 Initial Answer:\n{current_answer}\n")
            else:
                # Regenerate with reflection feedback
                current_answer = self._regenerate_answer(
                    query,
                    current_answer,
                    reflections[-1],
                    tools,
                    tool_descriptions,
                    llm_generate,
                    system_prompt,
                )
                self._log(f"🔄 Improved Answer:\n{current_answer}\n")

            # Step 2: Reflect on answer
            reflection = self._reflect(query, current_answer, llm_generate, system_prompt)

            self._log(f"🤔 Reflection:\n{reflection['critique']}\n")
            self._log(f"📊 Quality Score: {reflection['quality']:.2f}\n")

            reflections.append(reflection)

            trace.append(
                {
                    "cycle": iteration + 1,
                    "answer": current_answer,
                    "reflection": reflection,
                }
            )

            # Step 3: Check if satisfactory
            if reflection["quality"] >= self.reflection_threshold:
                self._log("✅ Quality threshold reached!")
                break

        self._log(f"\n{'='*60}")
        self._log(f"✅ FINAL ANSWER (after {len(reflections)} cycles)")
        self._log(f"{'='*60}")
        self._log(f"{current_answer}\n")

        return ReasoningResult(
            answer=current_answer or "No answer generated",
            iterations=len(reflections),
            success=True,
            trace=trace,
            start_time=start_time,
            end_time=datetime.now(),
            metadata={
                "strategy": "reflection",
                "reflection_cycles": len(reflections),
                "final_quality": reflections[-1]["quality"] if reflections else 0.0,
            },
        )

    def _generate_answer(
        self,
        query: str,
        tools: Dict[str, Callable],
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
    ) -> str:
        """Generate initial answer"""
        tools_desc = "\n".join([f"- {name}: {desc}" for name, desc in tool_descriptions.items()])

        prompt = f"""{system_prompt}

Available tools:
{tools_desc}

Answer this question to the best of your ability. You can describe what tools you would use.

Question: {query}

Your answer:"""

        messages = [Message(role="system", content=prompt)]

        answer = llm_generate(messages)
        return answer.strip()

    def _reflect(
        self,
        query: str,
        answer: str,
        llm_generate: Callable,
        system_prompt: str,
    ) -> Dict:
        """
        Reflect on answer quality

        Returns dict with:
        - critique: What could be improved
        - quality: Score 0.0-1.0
        - suggestions: List of improvements
        """
        reflection_prompt = f"""{system_prompt}

You are a critical evaluator. Analyze this answer and provide:

1. A quality score from 0.0 to 1.0 (where 1.0 is perfect)
2. Critical feedback on what's missing or wrong
3. Specific suggestions for improvement

Question: {query}

Answer to evaluate:
{answer}

Provide your reflection in this format:
Quality Score: [0.0-1.0]
Critique: [your critical analysis]
Suggestions: [specific improvements]"""

        messages = [Message(role="system", content=reflection_prompt)]

        reflection_text = llm_generate(messages)

        # Parse reflection
        quality = 0.5  # default
        critique = ""
        suggestions = ""

        for line in reflection_text.split("\n"):
            line = line.strip()
            if line.startswith("Quality Score:"):
                try:
                    quality = float(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    quality = 0.5
            elif line.startswith("Critique:"):
                critique = line.split(":", 1)[1].strip()
            elif line.startswith("Suggestions:"):
                suggestions = line.split(":", 1)[1].strip()

        return {
            "quality": quality,
            "critique": critique or reflection_text,
            "suggestions": suggestions,
            "full_text": reflection_text,
        }

    def _regenerate_answer(
        self,
        query: str,
        previous_answer: str,
        reflection: Dict,
        tools: Dict[str, Callable],
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
    ) -> str:
        """Regenerate answer based on reflection"""
        tools_desc = "\n".join([f"- {name}: {desc}" for name, desc in tool_descriptions.items()])

        prompt = f"""{system_prompt}

Available tools:
{tools_desc}

You previously answered this question, but it needs improvement.

Question: {query}

Your previous answer:
{previous_answer}

Critical feedback:
{reflection['critique']}

Suggestions for improvement:
{reflection['suggestions']}

Provide an improved answer that addresses the feedback:"""

        messages = [Message(role="system", content=prompt)]

        improved_answer = llm_generate(messages)
        return improved_answer.strip()
