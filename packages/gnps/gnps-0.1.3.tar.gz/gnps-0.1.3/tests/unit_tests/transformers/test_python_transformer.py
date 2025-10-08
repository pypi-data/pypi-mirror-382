"""Tests for PythonTransformer class."""

import pytest
from unittest.mock import Mock, patch

from gnps.transformers.python_transformer import PythonTransformer
from gnps.system import GnpsSystem
from gnps.cell import Cell
from gnps.rule import Rule
from gnps.parser.ast.expression import ConstantExpression, VariableExpression, SumExpression
from gnps.parser.ast.expression import DifferenceExpression, MultiplicationExpression, DivisionExpression
from gnps.parser.ast.expression import UnaryMinusExpression, IntMultiplicationExpression, IntDivisionExpression
from gnps.parser.ast.expression import FunctionCallExpression
from gnps.parser.ast.boolean_expression import BooleanConstantExpression, BooleanAndExpression
from gnps.parser.ast.boolean_expression import BooleanOrExpression, BooleanNotExpression
from gnps.parser.ast.boolean_expression import BooleanLessTestExpression, BooleanLessEqualTestExpression
from gnps.parser.ast.boolean_expression import BooleanGreaterTestExpression, BooleanGreaterEqualTestExpression
from gnps.parser.ast.boolean_expression import BooleanEqualTestExpression, BooleanNotEqualTestExpression
from gnps.parser.ast.value import NumericalValue, ArrayValue


class MockVariable:
    """Mock variable for testing."""
    def __init__(self, name, value=0.0):
        self.name = name
        self.value = NumericalValue(value)


class MockRule:
    """Mock rule for testing."""
    def __init__(self, guard=None, producer=None, consumer=None):
        self.guard = guard or BooleanConstantExpression(True)
        self.producer = producer or ConstantExpression(NumericalValue(1.0))
        self.consumer = consumer or MockVariable("x")


class TestPythonTransformer:
    """Test the PythonTransformer class."""

    def test_initialization(self):
        """Test transformer initialization."""
        transformer = PythonTransformer()
        assert transformer.output == []
        assert transformer.variable_declarations == set()

    def test_get_file_extension(self):
        """Test get_file_extension method."""
        transformer = PythonTransformer()
        assert transformer.get_file_extension() == ".py"

    def test_visit_value_numeric(self):
        """Test visit_value with numeric values."""
        transformer = PythonTransformer()

        # Test integer value
        int_value = NumericalValue(42)
        result = transformer.visit_value(int_value)
        assert result == "42"

        # Test float value
        float_value = NumericalValue(3.14)
        result = transformer.visit_value(float_value)
        assert result == "3.14"

    def test_visit_value_array(self):
        """Test visit_value with array values."""
        transformer = PythonTransformer()

        array_value = ArrayValue("int", [1, 2, 3])
        result = transformer.visit_value(array_value)
        assert result == "[1, 2, 3]"

    def test_visit_value_fallback(self):
        """Test visit_value fallback for unknown types."""
        transformer = PythonTransformer()

        result = transformer.visit_value("string_value")
        assert result == "string_value"

    def test_visit_constant_expression(self):
        """Test visit_ConstantExpression method."""
        transformer = PythonTransformer()

        expr = ConstantExpression(NumericalValue(42))
        result = transformer.visit_ConstantExpression(expr)
        assert result == "42"

    def test_visit_variable_expression(self):
        """Test visit_VariableExpression method."""
        transformer = PythonTransformer()

        var = MockVariable("test_var")
        expr = VariableExpression(var)
        result = transformer.visit_VariableExpression(expr)
        assert result == "self.test_var"

    def test_visit_sum_expression(self):
        """Test visit_SumExpression method."""
        transformer = PythonTransformer()

        left = ConstantExpression(NumericalValue(1))
        right = ConstantExpression(NumericalValue(2))
        expr = SumExpression(left, right)

        result = transformer.visit_SumExpression(expr)
        assert result == "(1 + 2)"

    def test_visit_difference_expression(self):
        """Test visit_DifferenceExpression method."""
        transformer = PythonTransformer()

        left = ConstantExpression(NumericalValue(5))
        right = ConstantExpression(NumericalValue(3))
        expr = DifferenceExpression(left, right)

        result = transformer.visit_DifferenceExpression(expr)
        assert result == "(5 - 3)"

    def test_visit_multiplication_expression(self):
        """Test visit_MultiplicationExpression method."""
        transformer = PythonTransformer()

        left = ConstantExpression(NumericalValue(4))
        right = ConstantExpression(NumericalValue(5))
        expr = MultiplicationExpression(left, right)

        result = transformer.visit_MultiplicationExpression(expr)
        assert result == "(4 * 5)"

    def test_visit_division_expression(self):
        """Test visit_DivisionExpression method."""
        transformer = PythonTransformer()

        left = ConstantExpression(NumericalValue(10))
        right = ConstantExpression(NumericalValue(2))
        expr = DivisionExpression(left, right)

        result = transformer.visit_DivisionExpression(expr)
        assert result == "(10 / 2)"

    def test_visit_unary_minus_expression(self):
        """Test visit_UnaryMinusExpression method."""
        transformer = PythonTransformer()

        operand = ConstantExpression(NumericalValue(5))
        expr = UnaryMinusExpression(operand)

        result = transformer.visit_UnaryMinusExpression(expr)
        assert result == "(-5)"

    def test_visit_int_multiplication_expression(self):
        """Test visit_IntMultiplicationExpression method."""
        transformer = PythonTransformer()

        operand = ConstantExpression(NumericalValue(5))
        expr = IntMultiplicationExpression(3, operand)

        result = transformer.visit_IntMultiplicationExpression(expr)
        assert result == "(3 * 5)"

    def test_visit_int_division_expression(self):
        """Test visit_IntDivisionExpression method."""
        transformer = PythonTransformer()

        operand = ConstantExpression(NumericalValue(10))
        expr = IntDivisionExpression(2, operand)

        result = transformer.visit_IntDivisionExpression(expr)
        assert result == "(10 / 2)"

    def test_visit_function_call_expression_with_args(self):
        """Test visit_FunctionCallExpression with arguments."""
        transformer = PythonTransformer()

        arg1 = ConstantExpression(NumericalValue(1))
        arg2 = ConstantExpression(NumericalValue(2))
        expr = Mock()
        expr.function_name = "sin"
        expr.arguments = [arg1, arg2]

        result = transformer.visit_FunctionCallExpression(expr)
        assert result == "math.sin(1, 2)"

    def test_visit_function_call_expression_no_args(self):
        """Test visit_FunctionCallExpression without arguments (constants)."""
        transformer = PythonTransformer()

        expr = Mock()
        expr.function_name = "pi"
        expr.arguments = []

        result = transformer.visit_FunctionCallExpression(expr)
        assert result == "math.pi"

    def test_visit_function_call_expression_unmapped(self):
        """Test visit_FunctionCallExpression with unmapped function."""
        transformer = PythonTransformer()

        arg = ConstantExpression(NumericalValue(1))
        expr = Mock()
        expr.function_name = "custom_func"
        expr.arguments = [arg]

        result = transformer.visit_FunctionCallExpression(expr)
        assert result == "custom_func(1)"

    def test_visit_boolean_constant_expression(self):
        """Test visit_BooleanConstantExpression method."""
        transformer = PythonTransformer()

        # Test True
        expr_true = BooleanConstantExpression(True)
        result = transformer.visit_BooleanConstantExpression(expr_true)
        assert result == "True"

        # Test False
        expr_false = BooleanConstantExpression(False)
        result = transformer.visit_BooleanConstantExpression(expr_false)
        assert result == "False"

    def test_visit_boolean_and_expression(self):
        """Test visit_BooleanAndExpression method."""
        transformer = PythonTransformer()

        left = BooleanConstantExpression(True)
        right = BooleanConstantExpression(False)
        expr = BooleanAndExpression(left, right)

        result = transformer.visit_BooleanAndExpression(expr)
        assert result == "(True and False)"

    def test_visit_boolean_or_expression(self):
        """Test visit_BooleanOrExpression method."""
        transformer = PythonTransformer()

        left = BooleanConstantExpression(True)
        right = BooleanConstantExpression(False)
        expr = BooleanOrExpression(left, right)

        result = transformer.visit_BooleanOrExpression(expr)
        assert result == "(True or False)"

    def test_visit_boolean_not_expression(self):
        """Test visit_BooleanNotExpression method."""
        transformer = PythonTransformer()

        operand = BooleanConstantExpression(True)
        expr = BooleanNotExpression(operand)

        result = transformer.visit_BooleanNotExpression(expr)
        assert result == "(not True)"

    def test_visit_boolean_comparison_expressions(self):
        """Test all boolean comparison expressions."""
        transformer = PythonTransformer()

        left = ConstantExpression(NumericalValue(1))
        right = ConstantExpression(NumericalValue(2))

        # Less than
        expr_lt = BooleanLessTestExpression(left, right)
        result = transformer.visit_BooleanLessTestExpression(expr_lt)
        assert result == "(1 < 2)"

        # Less than or equal
        expr_le = BooleanLessEqualTestExpression(left, right)
        result = transformer.visit_BooleanLessEqualTestExpression(expr_le)
        assert result == "(1 <= 2)"

        # Greater than
        expr_gt = BooleanGreaterTestExpression(left, right)
        result = transformer.visit_BooleanGreaterTestExpression(expr_gt)
        assert result == "(1 > 2)"

        # Greater than or equal
        expr_ge = BooleanGreaterEqualTestExpression(left, right)
        result = transformer.visit_BooleanGreaterEqualTestExpression(expr_ge)
        assert result == "(1 >= 2)"

        # Equal
        expr_eq = BooleanEqualTestExpression(left, right)
        result = transformer.visit_BooleanEqualTestExpression(expr_eq)
        assert result == "(1 == 2)"

        # Not equal
        expr_ne = BooleanNotEqualTestExpression(left, right)
        result = transformer.visit_BooleanNotEqualTestExpression(expr_ne)
        assert result == "(1 != 2)"

    def test_generic_visit(self):
        """Test generic_visit for unknown node types."""
        transformer = PythonTransformer()

        class UnknownNode:
            pass

        node = UnknownNode()
        result = transformer.generic_visit(node)
        assert result == "# Unknown node type: UnknownNode"

    def test_visit_dispatch(self):
        """Test that visit method dispatches correctly."""
        transformer = PythonTransformer()

        # Test with known type
        expr = ConstantExpression(NumericalValue(42))
        result = transformer.visit(expr)
        assert result == "42"

        # Test with unknown type
        class UnknownExpr:
            pass

        unknown = UnknownExpr()
        result = transformer.visit(unknown)
        assert result == "# Unknown node type: UnknownExpr"

    def test_get_producer_variables(self):
        """Test _get_producer_variables method."""
        transformer = PythonTransformer()

        # Create a mock producer with get_variables method
        producer = Mock()
        producer.get_variables.return_value = {"x": Mock(), "y": Mock()}

        variables = transformer._get_producer_variables(producer)
        assert variables == {"x", "y"}

    def test_get_producer_variables_no_method(self):
        """Test _get_producer_variables with producer without get_variables."""
        transformer = PythonTransformer()

        # Create a mock producer without get_variables method
        producer = Mock(spec=[])  # Empty spec means no methods

        variables = transformer._get_producer_variables(producer)
        assert variables == set()

    def test_transform_simple_system_no_inputs_no_outputs(self):
        """Test transform with simple system with no inputs or outputs."""
        transformer = PythonTransformer()

        # Create a simple system
        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain basic Python structure
        assert "# Generated Python code from GNPS system" in result
        assert "import math" in result
        assert "class GnpsSystem:" in result
        assert "def __init__(self):" in result
        assert "def step(self):" in result
        assert "return self.get_variables()" in result
        assert "def get_variables(self):" in result

    def test_transform_system_with_variables(self):
        """Test transform with system containing variables."""
        transformer = PythonTransformer()

        # Create mock variable
        var_x = Mock()
        var_x.value = NumericalValue(1.0)

        # Create mock cell
        cell = Mock()
        cell.contents = {"x": var_x}

        # Create system with variables
        system = Mock(spec=GnpsSystem)
        system.cells = [cell]
        system.rules = []
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should initialize variable
        assert "self.x = 1.0" in result
        assert "def get_variables(self):" in result
        assert "'x': self.x," in result

    def test_transform_system_with_input_variables(self):
        """Test transform with system having input variables."""
        transformer = PythonTransformer()

        # Create system with input variables
        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = {"input_x": Mock()}
        system.output_variables = None

        result = transformer.transform(system)

        # Should have input parameter and validation
        assert "def step(self, inputs):" in result
        assert "required_inputs = ['input_x']" in result
        assert "for var_name in required_inputs:" in result
        assert "if var_name not in inputs:" in result
        assert "raise ValueError" in result
        assert "self.input_x = inputs['input_x']" in result

    def test_transform_system_with_output_variables(self):
        """Test transform with system having output variables."""
        transformer = PythonTransformer()

        # Create system with output variables
        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = {"output_y": Mock()}

        result = transformer.transform(system)

        # Should return specific output variables
        assert "return {" in result
        assert "'output_y': self.output_y," in result

    def test_transform_system_with_rules(self):
        """Test transform with system containing rules."""
        transformer = PythonTransformer()

        # Create mock rule
        guard = BooleanConstantExpression(True)
        producer = ConstantExpression(NumericalValue(2.0))
        consumer = Mock()
        consumer.name = "x"

        # Create mock producer with get_variables method
        producer.get_variables = Mock(return_value={"y": Mock()})

        rule = Mock()
        rule.guard = guard
        rule.producer = producer
        rule.consumer = consumer

        # Create system with rule
        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = [rule]
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain rule evaluation
        assert "# Rule 1" in result
        assert "if True:" in result
        assert "x_new += 2.0" in result
        assert "used_vars.add('y')" in result

    def test_transform_system_with_inputs_and_csv_processing(self):
        """Test transform generates CSV processing code for systems with inputs."""
        transformer = PythonTransformer()

        # Create system with input variables
        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = {"input_val": Mock()}
        system.output_variables = {"output_val": Mock()}

        result = transformer.transform(system)

        # Should contain CSV processing logic
        assert "import csv" in result
        assert "reader = csv.DictReader(sys.stdin)" in result
        assert "while True:" in result
        assert "input_row = next(reader)" in result
        assert "inputs['input_val'] = float(input_row['input_val'])" in result
        assert "output = system.step(inputs)" in result
        assert "except StopIteration:" in result

    def test_transform_system_without_inputs_csv_processing(self):
        """Test transform generates CSV processing for systems without inputs."""
        transformer = PythonTransformer()

        # Create system without input variables
        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = {"result": Mock()}

        result = transformer.transform(system)

        # Should contain steps parameter and loop
        assert "parser.add_argument('steps', type=int" in result
        assert "for step_num in range(args.steps):" in result
        assert "output = system.step()" in result

    def test_transform_system_main_function(self):
        """Test that transform generates main function."""
        transformer = PythonTransformer()

        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain main function and entry point
        assert "def main():" in result
        assert "system = GnpsSystem()" in result
        assert "if __name__ == '__main__':" in result
        assert "main()" in result

    def test_transform_system_format_float_function(self):
        """Test that transform generates format_float function."""
        transformer = PythonTransformer()

        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain format_float function
        assert "def format_float(value):" in result
        assert "if isinstance(value, (int, float)):" in result
        assert 'return f"{value:.6f}".rstrip("0").rstrip(".")' in result
        assert "return str(value)" in result

    def test_transform_resets_state(self):
        """Test that transform resets transformer state."""
        transformer = PythonTransformer()

        # Add some initial state
        transformer.output = ["existing line"]
        transformer.variable_declarations = {"old_var"}

        system = Mock(spec=GnpsSystem)
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = None

        transformer.transform(system)

        # State should be reset (variable_declarations cleared and repopulated)
        assert "existing line" not in transformer.get_output()

    def test_transform_complex_system(self):
        """Test transform with a more complex system."""
        transformer = PythonTransformer()

        # Create variables
        var_x = Mock()
        var_x.value = NumericalValue(1.0)
        var_y = Mock()
        var_y.value = NumericalValue(2.0)

        # Create cell
        cell = Mock()
        cell.contents = {"x": var_x, "y": var_y}

        # Create rule
        guard = BooleanConstantExpression(True)
        producer = ConstantExpression(NumericalValue(3.0))
        consumer = Mock()
        consumer.name = "x"
        producer.get_variables = Mock(return_value={"y": Mock()})

        rule = Mock()
        rule.guard = guard
        rule.producer = producer
        rule.consumer = consumer

        # Create system
        system = Mock(spec=GnpsSystem)
        system.cells = [cell]
        system.rules = [rule]
        system.input_variables = {"input_z": Mock()}
        system.output_variables = {"x": Mock(), "y": Mock()}

        result = transformer.transform(system)

        # Verify complex system transformation
        assert "self.x = 1.0" in result
        assert "self.y = 2.0" in result
        assert "def step(self, inputs):" in result
        assert "required_inputs = ['input_z']" in result
        assert "if True:" in result
        assert "x_new += 3.0" in result
        assert "'x': self.x," in result
        assert "'y': self.y," in result

