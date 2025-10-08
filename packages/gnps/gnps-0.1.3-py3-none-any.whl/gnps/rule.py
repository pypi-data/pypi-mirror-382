from .parser.ast.boolean_expression import BooleanExpression
from .parser.ast.expression import Expression
from .parser.ast.variable import Variable


class Rule:
    guard: BooleanExpression
    producer: Expression
    consumer: Variable
    vars: dict[str, Variable]

    def __init__(self, consumer: Variable, producer: Expression, guard: BooleanExpression):
        self.guard = guard
        self.producer = producer
        self.consumer = consumer
        self.vars: dict[str, Variable] = producer.get_variables()

    def __str__(self):
        g = self.guard.__str__()
        p = self.producer.__str__()
        return f"{g} : {p} -> {self.consumer}"

    def __repr__(self):
        return self.__str__()
