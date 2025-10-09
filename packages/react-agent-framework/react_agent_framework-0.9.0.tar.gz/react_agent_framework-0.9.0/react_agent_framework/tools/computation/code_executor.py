"""
Safe Python code executor tool
"""

import sys
import io
from typing import Dict, Any
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class CodeExecutor(BaseTool):
    """
    Execute Python code safely in isolated environment

    Captures stdout and returns execution result
    """

    name = "code_executor"
    description = "Execute Python code safely. Input: Python code to execute"
    category = "computation"

    def __init__(self, timeout: int = 5, **kwargs):
        """
        Initialize code executor

        Args:
            timeout: Execution timeout in seconds
        """
        super().__init__(**kwargs)
        self.timeout = timeout

        # Blocked imports for security
        self.blocked_imports = [
            "os",
            "sys",
            "subprocess",
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "file",
            "input",
        ]

    def validate_input(self, input_text: str) -> bool:
        """
        Validate code for security issues

        Args:
            input_text: Code to validate

        Returns:
            True if safe, False otherwise
        """
        if not input_text or not input_text.strip():
            return False

        code_lower = input_text.lower()

        # Check for blocked imports
        for blocked in self.blocked_imports:
            if f"import {blocked}" in code_lower or f"from {blocked}" in code_lower:
                return False

        # Check for dangerous built-ins
        dangerous_patterns = ["__", "eval(", "exec(", "compile(", "open("]
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return False

        return True

    def execute(self, input_text: str) -> str:
        """
        Execute Python code

        Args:
            input_text: Python code to execute

        Returns:
            Execution output or error message
        """
        code = input_text.strip()

        try:
            # Capture stdout
            stdout_capture = io.StringIO()
            sys.stdout = stdout_capture

            # Create restricted namespace
            namespace: Dict[str, Any] = {
                "__builtins__": {
                    "abs": abs,
                    "all": all,
                    "any": any,
                    "bool": bool,
                    "dict": dict,
                    "enumerate": enumerate,
                    "filter": filter,
                    "float": float,
                    "int": int,
                    "len": len,
                    "list": list,
                    "map": map,
                    "max": max,
                    "min": min,
                    "print": print,
                    "range": range,
                    "reversed": reversed,
                    "round": round,
                    "set": set,
                    "sorted": sorted,
                    "str": str,
                    "sum": sum,
                    "tuple": tuple,
                    "type": type,
                    "zip": zip,
                }
            }

            # Execute code
            exec(code, namespace)

            # Get output
            output = stdout_capture.getvalue()

            # Restore stdout
            sys.stdout = sys.__stdout__

            if output:
                return output.strip()
            else:
                return "Code executed successfully (no output)"

        except SyntaxError as e:
            sys.stdout = sys.__stdout__
            return f"Syntax Error: {str(e)}"
        except Exception as e:
            sys.stdout = sys.__stdout__
            return f"Execution Error: {str(e)}"
