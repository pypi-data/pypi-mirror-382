import pytest
from gnps import GnpsSystem
from gnps import Rule
from gnps.parser.ast import Variable, VariableExpression, BooleanConstantExpression
from gnps.parser.ast import SumExpression


class TestSystem:

    def test_empty(self):
        assert True

    def test_empty_system(self):
        system = GnpsSystem()
        assert system.rules == []

    @pytest.mark.xfail(reason="Should fail")
    def test_full(self):
        assert False


class TestRule:
    def test_rule(self):
        x = Variable("x", 1)
        y = Variable("y", 2)
        rule = Rule(x, SumExpression(VariableExpression(x), VariableExpression(y)), BooleanConstantExpression(True))
        assert rule.guard.__str__() == "True"
        assert rule.producer.__str__() == "(x + y)"
        assert rule.consumer.__str__() == "x"
        assert rule.vars == {"x": x, "y": y}
        assert rule.__str__() == "True : (x + y) -> x"
        assert rule.__repr__() == "True : (x + y) -> x"


if __name__ == '__main__':
    pytest.main()  # pragma: no cover
