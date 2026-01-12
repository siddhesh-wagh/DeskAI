"""
Calculator Skill - Safe mathematical expression evaluation
"""
from skills.base import BaseSkill, SkillResult
from core.dispatcher import command
from core.context import AssistantContext
from typing import Dict, Any
import ast
import operator as op
import re
from word2number import w2n


# Operator mapping for safe eval
OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.UAdd: op.pos,
    ast.USub: op.neg
}

# Spoken word to operator mapping
OPERATOR_MAP = {
    "plus": "+", "add": "+", "sum": "+",
    "minus": "-", "subtract": "-", "difference": "-",
    "times": "*", "multiply": "*", "multiplied by": "*", "into": "*", "x": "*",
    "divided by": "/", "divide by": "/",
    "mod": "%", "modulo": "%",
    "power": "**", "to the power of": "**",
    "open parenthesis": "(", "close parenthesis": ")",
    "point": ".", "dot": ".",
}


class CalculatorSkill(BaseSkill):
    """Perform mathematical calculations from spoken input"""
    
    def safe_eval(self, expr: str) -> float:
        """
        Safely evaluate mathematical expression using AST.
        
        Args:
            expr: Mathematical expression string
        
        Returns:
            Calculated result
        
        Raises:
            ValueError: On invalid expression or unsupported operations
        """
        def _eval(node):
            if isinstance(node, ast.Constant):  # Number
                return node.value
            elif isinstance(node, ast.BinOp):  # Binary operation
                left = _eval(node.left)
                right = _eval(node.right)
                return OPERATORS[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):  # Unary operation
                operand = _eval(node.operand)
                return OPERATORS[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported expression: {node!r}")
        
        try:
            tree = ast.parse(expr, mode='eval')
            return _eval(tree.body)
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero")
        except KeyError as e:
            raise ValueError(f"Unsupported operation: {e}")
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    def parse_spoken_math(self, spoken: str) -> str:
        """
        Convert spoken math to expression.
        
        Example: "five plus three times two" -> "5 + 3 * 2"
        """
        words = spoken.lower().split()
        tokens = []
        i = 0
        
        while i < len(words):
            matched = False
            
            # Try multi-word operators first
            for size in (3, 2, 1):
                if i + size <= len(words):
                    phrase = " ".join(words[i:i+size])
                    if phrase in OPERATOR_MAP:
                        tokens.append(OPERATOR_MAP[phrase])
                        i += size
                        matched = True
                        break
            
            if matched:
                continue
            
            # Try word-to-number conversion
            for j in range(len(words), i, -1):
                seq = " ".join(words[i:j])
                try:
                    num = w2n.word_to_num(seq)
                    tokens.append(str(num))
                    i = j
                    matched = True
                    break
                except ValueError:
                    pass
            
            if matched:
                continue
            
            # Check if already a number
            w = words[i]
            if re.fullmatch(r"-?\d+(\.\d+)?", w):
                tokens.append(w)
                i += 1
            else:
                raise ValueError(f"Unrecognized term: '{w}'")
        
        # Join tokens and add spacing around operators
        expr = "".join(tokens)
        spaced = re.sub(r"([+\-*/%()^])", r" \1 ", expr)
        return re.sub(r"\s+", " ", spaced).strip()
    
    def handle_percentage(self, query: str) -> tuple:
        """
        Handle percentage calculations separately.
        
        Returns:
            (handled, result_message)
        """
        # Match "X% of Y" or "X percent of Y"
        match = re.search(r"(\d+\.?\d*)\s*(%|percent)\s*of\s*(\d+\.?\d*)", query)
        
        if match:
            try:
                percent = float(match.group(1))
                base = float(match.group(3))
                result = (percent / 100) * base
                return (True, f"{percent}% of {base} is {result}")
            except ValueError:
                return (True, "Invalid percentage calculation")
        
        return (False, "")
    
    def execute(self, context: AssistantContext, query: str, **params) -> Dict[str, Any]:
        # Handle percentage calculations
        is_percentage, percentage_result = self.handle_percentage(query)
        if is_percentage:
            return self.success_response(percentage_result)
        
        # Extract expression from query
        expr = query.lower()
        for keyword in ("calculate", "what is", "what's", "compute"):
            expr = expr.replace(keyword, "")
        
        expr = expr.replace("tell me", "").strip().rstrip("?")
        
        if not expr:
            return self.error_response("No calculation expression provided")
        
        try:
            # Parse spoken math to expression
            parsed_expr = self.parse_spoken_math(expr)
            
            # Replace ^ with ** for power
            parsed_expr = parsed_expr.replace("^", "**")
            
            # Safely evaluate
            result = self.safe_eval(parsed_expr)
            
            # Format result nicely
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            return SkillResult()\
                .with_message(f"The result is {result}")\
                .with_data({
                    'expression': parsed_expr,
                    'result': result
                })\
                .build()
        
        except ValueError as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response(f"Calculation failed: {e}")


# Register calculator command
@command(["calculate", "what is", "what's", "compute"], priority=50)
def cmd_calculate(ctx: AssistantContext, query: str) -> Dict[str, Any]:
    return CalculatorSkill().execute(ctx, query)