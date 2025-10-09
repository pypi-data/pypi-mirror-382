"""
Calculator tool for mathematical operations
"""

import ast
import operator
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class Calculator(BaseTool):
    """
    Safe mathematical calculator

    Evaluates mathematical expressions safely without exec()
    """

    name = "calculator"
    description = (
        "Evaluate mathematical expressions. Input: expression (e.g., '2 + 2', '10 * (5 + 3)')"
    )
    category = "computation"

    # Supported operators
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, **kwargs):
        """Initialize calculator tool"""
        super().__init__(**kwargs)

    def _evaluate_node(self, node: ast.AST) -> float:
        """
        Safely evaluate AST node

        Args:
            node: AST node to evaluate

        Returns:
            Numeric result

        Raises:
            ValueError: If expression is invalid or unsafe
        """
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            op_type = type(node.op)

            if op_type not in self.OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")

            return self.OPERATORS[op_type](left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_node(node.operand)
            op_type = type(node.op)

            if op_type not in self.OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

            return self.OPERATORS[op_type](operand)

        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    def execute(self, input_text: str) -> str:
        """
        Execute calculator

        Args:
            input_text: Mathematical expression

        Returns:
            Calculation result or error message
        """
        expression = input_text.strip()

        try:
            # Parse expression into AST
            tree = ast.parse(expression, mode="eval")

            # Evaluate safely
            result = self._evaluate_node(tree.body)

            # Format result
            if result == int(result):
                return str(int(result))
            else:
                return f"{result:.10g}"  # Remove trailing zeros

        except SyntaxError:
            return f"Error: Invalid mathematical expression: {expression}"
        except ValueError as e:
            return f"Error: {str(e)}"
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Error calculating expression: {str(e)}"
