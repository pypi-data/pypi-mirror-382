from lark import Lark, Transformer, GrammarError, Tree

from .ast.value import FloatValue
from .ast import *
from ..rule import Rule
from .ast.expression import FunctionCallExpression

expression_grammar = r"""
start: expr

?expr: term
      | expr "+" term  -> sum
      | expr "-" term  -> difference

?term: factor
     | term "*" factor  -> multiplication
     | term "/" factor  -> division

?factor: NUMBER       -> number
       | ID     -> variable
       | ID "(" [arg_list] ")"  -> function_call
       | "-" factor    -> unary_minus
       | "(" expr ")"

arg_list: expr ("," expr)*  -> arguments


%import common.NUMBER
%import common.CNAME -> ID
%import common.WS
%ignore WS
"""

boolean_expression_grammar = expression_grammar + r"""
?cond: and_cond
    | cond "||" cond  -> bor
    
?and_cond: atom
    | and_cond "&&" atom -> band

?atom: literal
    | "!" literal -> bnot


?literal: CONST -> constant
    | test
    | "(" cond ")"

CONST.2: "true"i | "false"i
    
?test: expr OP expr -> xtest

OP: ">=" | ">" | "==" | "<=" | "<" | "!="    
 
"""

rule_expression_grammar = boolean_expression_grammar + r"""
?rule: (cond (":" | "|"))? expr "->" ID  -> rule
"""

variable_assignment_expression_grammar = expression_grammar + r"""
?assignment: ID "=" expr ("," ID "=" expr)* -> assignment 
"""


# Create a custom transformer to build the expression tree
class ExpressionTransformer(Transformer):
    def __init__(self, context_variables: dict[str, Variable]):
        super().__init__()
        self.context_variables = context_variables

    def sum(self, args):
        return SumExpression(args[0], args[1])

    def difference(self, args):
        return DifferenceExpression(args[0], args[1])

    def multiplication(self, args):
        return MultiplicationExpression(args[0], args[1])

    def division(self, args):
        return DivisionExpression(args[0], args[1])

    def number(self, args):
        return ConstantExpression(FloatValue(args[0]))

    def unary_minus(self, args):
        return UnaryMinusExpression(args[0])

    def variable(self, args):
        if str(args[0]) in self.context_variables:
            return VariableExpression(self.context_variables[args[0]])
        else:
            raise GrammarError(f"Variable {args[0]} not defined in the context")  # pragma: no cover

    def arguments(self, args):
        return args

    def function_call(self, args):
        function_name = str(args[0])
        arguments = args[1] if len(args) > 1 else []
        return FunctionCallExpression(function_name, arguments)


class ConditionTransformer(ExpressionTransformer):
    def constant(self, args):
        if str(args[0]).lower() == "true":
            return BooleanConstantExpression(True)
        else:
            return BooleanConstantExpression(False)

    def bnot(self, args):
        return BooleanNotExpression(args[0])

    def band(self, args):
        return BooleanAndExpression(args[0], args[1])

    def bor(self, args):
        return BooleanOrExpression(args[0], args[1])

    def xtest(self, args):
        left = args[0]
        op = args[1]
        right = args[2]

        match op:
            case "<=":
                return BooleanLessEqualTestExpression(left, right)
            case "<":
                return BooleanLessTestExpression(left, right)
            case "==":
                return BooleanEqualTestExpression(left, right)
            case "!=":
                return BooleanNotEqualTestExpression(left, right)
            case ">=":
                return BooleanGreaterEqualTestExpression(left, right)
            case ">":
                return BooleanGreaterTestExpression(left, right)
            case _:  # pragma: no cover
                raise GrammarError(f"Operator {op} not defined")  # pragma: no cover


class RuleTransformer(ConditionTransformer):
    def rule(self, args):
        if len(args) == 3:
            guard = args[0]
            producer = args[1]
            consumer_str = args[2]
        else:
            guard = BooleanConstantExpression(True)
            producer = args[0]
            consumer_str = args[1]
        if consumer_str not in self.context_variables:
            raise GrammarError(f"Variable {consumer_str} not defined in the context")  # pragma: no cover
        return Rule(guard=guard, producer=producer, consumer=self.context_variables[consumer_str])


class AssignmentTransformer(ExpressionTransformer):
    def assignment(self, args):
        variables = {}
        nb = len(args)
        for i in range(0, nb, 2):
            variable_name = str(args[i])
            expr = args[i+1]

            # Check if the expression only references already defined variables
            for var_name in expr.get_variables():
                if var_name not in self.context_variables:
                    raise GrammarError(f"Variable {var_name} used in assignment is not defined") # pragma: no cover

            # Evaluate the expression to get its value
            result_value = expr.evaluate()

            # Store the variable
            if variable_name not in self.context_variables:
                variable = Variable(variable_name, result_value)
            else:
                variable = self.context_variables[variable_name]
                variable.value = result_value

            variables[variable_name] = variable
        return variables


# Parse the expression and build the expression tree
def parse_expression(expression_string: str, context_variables: dict[str, Variable]) -> Expression | Tree:
    parser = Lark(expression_grammar, parser="lalr", start="expr", transformer=ExpressionTransformer(context_variables))
    expression_tree = parser.parse(expression_string)
    return expression_tree


# Parse the condition and build the expression tree
def parse_condition(condition_string: str, context_variables: dict[str, Variable]) -> BooleanExpression | Tree:
    parser = Lark(boolean_expression_grammar,
                  parser="lalr", start="cond",
                  transformer=ConditionTransformer(context_variables))
    condition_tree = parser.parse(condition_string)
    return condition_tree


# Parse the rule and build the expression tree
def parse_rule(rule_string: str, context_variables: dict[str, Variable]) -> Rule | Tree:
    parser = Lark(rule_expression_grammar, parser="lalr", start="rule", transformer=RuleTransformer(context_variables))
    rule = parser.parse(rule_string)
    return rule


# Parse the rule and build the expression tree
def parse_variable_assignment(assignment_string: str,
                              context_variables: dict[str, Variable]) -> dict[str, Variable] | Tree:
    parser = Lark(variable_assignment_expression_grammar,
                  parser="lalr", start="assignment",
                  transformer=AssignmentTransformer(context_variables))
    variables = parser.parse(assignment_string)
    return variables
