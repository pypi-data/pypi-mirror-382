"""Python transformer for converting GNPS AST to Python code using visitor pattern."""

from typing import Any
from .base_transformer import BaseTransformer
from ..system import GnpsSystem
from ..parser.ast import *
from ..parser.ast.value import *


class PythonTransformer(BaseTransformer):
    """Transformer that converts GNPS systems to Python code using proper visitor pattern."""

    def __init__(self):
        super().__init__()
        self.variable_declarations = set()

    def get_file_extension(self) -> str:
        """Get the file extension for Python files."""
        return ".py"

    def transform(self, system: GnpsSystem) -> str:
        """Transform a GNPS system to Python code.

        Args:
            system: The GNPS system to transform

        Returns:
            Python code as a string
        """
        self.reset()
        self.variable_declarations = set()

        # Add imports and header
        self.add_line("# Generated Python code from GNPS system")
        self.add_line("import math")
        self.add_line()

        # Add class definition
        self.add_line("class GnpsSystem:")
        self.add_line("def __init__(self):", 1)

        # Initialize variables from all cells
        for cell in system.cells:
            for var_name, variable in cell.contents.items():
                if var_name not in self.variable_declarations:
                    initial_value = self.visit_value(variable.value)
                    self.add_line(f"self.{var_name} = {initial_value}", 2)
                    self.variable_declarations.add(var_name)
                else: # pragma: no cover
                    pass

        # Store input and output variable names
        input_vars = list(system.input_variables.keys()) if system.input_variables else []
        output_vars = list(system.output_variables.keys()) if system.output_variables else []

        self.add_line()

        # Add step method with input/output handling
        if input_vars:
            # When input variables exist, inputs parameter is required
            self.add_line("def step(self, inputs):", 1)
            self.add_line('"""Execute one step of the GNPS system.', 2)
            self.add_line("", 2)
            self.add_line("Args:", 2)
            self.add_line("inputs: Dictionary with input variable values (required)", 3)
            self.add_line("", 2)
            self.add_line("Returns:", 2)
            self.add_line("Dictionary with output variable values", 3)
            self.add_line('"""', 2)

            # Validate that all input variables are provided
            self.add_line("# Validate that all input variables are provided", 2)
            self.add_line(f"required_inputs = {input_vars}", 2)
            self.add_line("for var_name in required_inputs:", 2)
            self.add_line("if var_name not in inputs:", 3)
            self.add_line(f"raise ValueError(f'Input variable {{var_name}} is required but not provided')", 4)
            self.add_line()

            # Update input variables
            self.add_line("# Update input variables", 2)
            for var_name in input_vars:
                self.add_line(f"self.{var_name} = inputs['{var_name}']", 2)
            self.add_line()
        else:
            # When no input variables, inputs parameter is optional (absent)
            self.add_line("def step(self):", 1)
            self.add_line('"""Execute one step of the GNPS system.', 2)
            self.add_line("", 2)
            self.add_line("Returns:", 2)
            if output_vars:
                self.add_line("Dictionary with output variable values", 3)
            else:
                self.add_line("Dictionary with all variable values", 3)
            self.add_line('"""', 2)

        # GNPS algorithm implementation
        self.add_line("# GNPS step using _new variables approach", 2)
        self.add_line()

        # Step 1: Initialize _new versions of all variables
        self.add_line("# Step 1: Initialize _new versions of all variables", 2)
        var_names = sorted(self.variable_declarations)
        for var_name in var_names:
            self.add_line(f"{var_name}_new = self.{var_name}", 2)
        self.add_line()

        # Step 2: Track used variables
        self.add_line("# Step 2: Track variables used in productions", 2)
        self.add_line("used_vars = set()", 2)
        self.add_line()

        # Step 3: Generate rule evaluation with += operations
        self.add_line("# Step 3: Evaluate rules and accumulate productions", 2)
        for i, rule in enumerate(system.rules):
            self.add_line(f"# Rule {i + 1}", 2)
            guard_code = self.visit(rule.guard)
            producer_code = self.visit(rule.producer)
            consumer_name = rule.consumer.name if hasattr(rule.consumer, 'name') else str(rule.consumer)

            # Get variables used in this rule
            producer_vars = self._get_producer_variables(rule.producer)

            self.add_line(f"if {guard_code}:", 2)
            self.add_line(f"{consumer_name}_new += {producer_code}", 3)

            # Mark variables as used
            for var_name in producer_vars:
                self.add_line(f"used_vars.add('{var_name}')", 3)
            self.add_line()

        # Step 4: Handle used variables (new_value - old_value)
        self.add_line("# Step 4: For used variables, compute new_value - old_value", 2)
        for var_name in var_names:
            self.add_line(f"if '{var_name}' in used_vars:", 2)
            self.add_line(f"{var_name}_new -= self.{var_name}", 3)
        self.add_line()

        # Step 5: Update all variables to their _new values
        self.add_line("# Step 5: Update all variables to their final values", 2)
        for var_name in var_names:
            self.add_line(f"self.{var_name} = {var_name}_new", 2)

        # Return output variables
        self.add_line()
        if output_vars:
            self.add_line("# Return output variables", 2)
            self.add_line("return {", 2)
            for var_name in output_vars:
                self.add_line(f"'{var_name}': self.{var_name},", 3)
            self.add_line("}", 2)
        else:
            self.add_line("# No output variables defined, return all variables", 2)
            self.add_line("return self.get_variables()", 2)

        # Add method to get all variables
        self.add_line()
        self.add_line("def get_variables(self):", 1)
        self.add_line("return {", 2)
        for var_name in self.variable_declarations:
            self.add_line(f"'{var_name}': self.{var_name},", 3)
        self.add_line("}", 2)

        # Add main function for CSV processing
        self.add_line()
        self.add_line()
        self.add_line("def format_float(value):", 0)
        self.add_line('"""Format float values with proper precision."""', 1)
        self.add_line("if isinstance(value, (int, float)):", 1)
        self.add_line('return f"{value:.6f}".rstrip("0").rstrip(".")', 2)
        self.add_line("return str(value)", 1)
        self.add_line()
        self.add_line()
        self.add_line("def main():", 0)
        self.add_line('"""Main function for CSV processing."""', 1)
        self.add_line("import sys", 1)
        self.add_line("import csv", 1)
        self.add_line("import argparse", 1)
        self.add_line()

        # Parse command line arguments
        self.add_line("parser = argparse.ArgumentParser(description='GNPS System Simulator')", 1)
        if input_vars:
            # For systems with input variables, no steps parameter (run until input is exhausted)
            self.add_line("args = parser.parse_args()", 1)
        else:
            # For systems without input, steps is required
            self.add_line("parser.add_argument('steps', type=int, help='Number of steps to execute')", 1)
            self.add_line("args = parser.parse_args()", 1)
        self.add_line()

        # Initialize system
        self.add_line("system = GnpsSystem()", 1)
        self.add_line()

        if input_vars:
            # CSV processing for systems with input variables
            self.add_line("# Read CSV from stdin", 1)
            self.add_line("reader = csv.DictReader(sys.stdin)", 1)
            self.add_line("writer = None", 1)
            self.add_line()

            # Changed to continuous processing (no steps parameter)
            self.add_line("step_num = 0", 1)
            self.add_line("# Process all input rows until exhausted", 1)
            self.add_line("while True:", 1)
            self.add_line("try:", 2)
            self.add_line("# Read next input row", 3)
            self.add_line("input_row = next(reader)", 3)

            # Convert input values to appropriate types
            self.add_line("# Convert input values to float", 3)
            self.add_line("inputs = {}", 3)
            for var_name in input_vars:
                self.add_line(f"if '{var_name}' in input_row:", 3)
                self.add_line(f"inputs['{var_name}'] = float(input_row['{var_name}'])", 4)
                self.add_line(f"else:", 3)
                self.add_line(f"print(f'Error: Input variable {var_name} not found in CSV row {{step_num + 1}}', file=sys.stderr)", 4)
                self.add_line("sys.exit(1)", 4)
            self.add_line()

            # Execute step and get output
            self.add_line("# Execute step", 3)
            self.add_line("output = system.step(inputs)", 3)
            self.add_line()

            # Write output to CSV
            if output_vars:
                self.add_line("# Initialize CSV writer on first row", 3)
                self.add_line("if writer is None:", 3)
                self.add_line(f"fieldnames = ['step'] + {output_vars}", 4)
                self.add_line("writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)", 4)
                self.add_line("writer.writeheader()", 4)
                self.add_line()

                self.add_line("# Write output row with step number and formatted values", 3)
                self.add_line("output_row = {'step': step_num + 1}", 3)
                self.add_line("formatted_output = {k: format_float(v) for k, v in output.items()}", 3)
                self.add_line("output_row.update(formatted_output)", 3)
                self.add_line("writer.writerow(output_row)", 3)

            self.add_line("step_num += 1", 3)

            self.add_line("except StopIteration:", 2)
            self.add_line("# No more input rows, processing complete", 3)
            self.add_line("if step_num == 0:", 3)
            self.add_line("print('Warning: No input data found.', file=sys.stderr)", 4)
            self.add_line("else:", 3)
            self.add_line("print(f'Processed {step_num} input rows successfully.', file=sys.stderr)", 4)
            self.add_line("break", 3)
            self.add_line()
        else:
            # No input variables - run steps and output CSV for each step
            self.add_line("# No input variables - run steps and output CSV for each step", 1)
            self.add_line("writer = None", 1)
            self.add_line()

            # Add step 0 output (initial state)
            if output_vars:
                self.add_line("# Initialize CSV writer", 1)
                self.add_line(f"fieldnames = ['step'] + {output_vars}", 1)
                self.add_line("writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)", 1)
                self.add_line("writer.writeheader()", 1)
                self.add_line()
                self.add_line("# Write initial state (step 0) with formatted values", 1)
                self.add_line("initial_output = {", 1)
                for var_name in output_vars:
                    self.add_line(f"'{var_name}': format_float(system.{var_name}),", 2)
                self.add_line("}", 1)
                self.add_line("step0_row = {'step': 0}", 1)
                self.add_line("step0_row.update(initial_output)", 1)
                self.add_line("writer.writerow(step0_row)", 1)
                self.add_line()
            else:
                self.add_line("# Initialize CSV writer with all variables", 1)
                self.add_line("all_vars = system.get_variables()", 1)
                self.add_line("fieldnames = ['step'] + list(all_vars.keys())", 1)
                self.add_line("writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)", 1)
                self.add_line("writer.writeheader()", 1)
                self.add_line()
                self.add_line("# Write initial state (step 0) with formatted values", 1)
                self.add_line("step0_row = {'step': 0}", 1)
                self.add_line("formatted_all_vars = {k: format_float(v) for k, v in all_vars.items()}", 1)
                self.add_line("step0_row.update(formatted_all_vars)", 1)
                self.add_line("writer.writerow(step0_row)", 1)
                self.add_line()

            self.add_line("for step_num in range(args.steps):", 1)
            if output_vars:
                self.add_line("output = system.step()", 2)
                self.add_line("# Write output row with step number and formatted values", 2)
                self.add_line("output_row = {'step': step_num + 1}", 2)
                self.add_line("formatted_output = {k: format_float(v) for k, v in output.items()}", 2)
                self.add_line("output_row.update(formatted_output)", 2)
                self.add_line("writer.writerow(output_row)", 2)
            else:
                self.add_line("system.step()", 2)
                self.add_line("all_vars = system.get_variables()", 2)
                self.add_line("# Write row with step number and formatted values", 2)
                self.add_line("all_vars_row = {'step': step_num + 1}", 2)
                self.add_line("formatted_all_vars = {k: format_float(v) for k, v in all_vars.items()}", 2)
                self.add_line("all_vars_row.update(formatted_all_vars)", 2)
                self.add_line("writer.writerow(all_vars_row)", 2)

        self.add_line()
        self.add_line()
        self.add_line("if __name__ == '__main__':", 0)
        self.add_line("main()", 1)

        return self.get_output()

    def _get_producer_variables(self, producer_expr) -> set:
        """Extract variable names used in a producer expression."""
        variables = set()

        # Get all variables from the expression
        if hasattr(producer_expr, 'get_variables'):
            expr_vars = producer_expr.get_variables()
            variables.update(expr_vars.keys())

        return variables

    def visit(self, node) -> str:
        """Generic visit method that dispatches to specific visitor methods."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node) -> str:
        """Default visitor for unknown node types."""
        return f"# Unknown node type: {type(node).__name__}"

    # Expression visitors
    def visit_ConstantExpression(self, node: ConstantExpression) -> str:
        """Visit a constant expression."""
        return self.visit_value(node.value)

    def visit_VariableExpression(self, node: VariableExpression) -> str:
        """Visit a variable expression."""
        return f"self.{node.variable.name}"

    def visit_SumExpression(self, node: SumExpression) -> str:
        """Visit a sum expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} + {right})"

    def visit_DifferenceExpression(self, node: DifferenceExpression) -> str:
        """Visit a difference expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} - {right})"

    def visit_MultiplicationExpression(self, node: MultiplicationExpression) -> str:
        """Visit a multiplication expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} * {right})"

    def visit_DivisionExpression(self, node: DivisionExpression) -> str:
        """Visit a division expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} / {right})"

    def visit_UnaryMinusExpression(self, node: UnaryMinusExpression) -> str:
        """Visit a unary minus expression."""
        operand = self.visit(node.expression)
        return f"(-{operand})"

    def visit_IntMultiplicationExpression(self, node: IntMultiplicationExpression) -> str:
        """Visit an integer multiplication expression."""
        operand = self.visit(node.expression)
        return f"({node.constant} * {operand})"

    def visit_IntDivisionExpression(self, node: IntDivisionExpression) -> str:
        """Visit an integer division expression."""
        operand = self.visit(node.expression)
        return f"({operand} / {node.constant})"

    def visit_FunctionCallExpression(self, node) -> str:
        """Visit a function call expression."""
        args = [self.visit(arg) for arg in node.arguments]
        args_str = ", ".join(args)

        # Map common mathematical functions to Python's math module
        function_mappings = {
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'exp': 'math.exp',
            'log': 'math.log',
            'sqrt': 'math.sqrt',
            'pow': 'math.pow',
            'abs': 'abs',
            'floor': 'math.floor',
            'ceil': 'math.ceil',
            'pi': 'math.pi',
            'e': 'math.e'
        }

        python_function = function_mappings.get(node.function_name, node.function_name)

        # Handle constants (0-ary functions) differently
        if len(node.arguments) == 0:
            return python_function
        else:
            return f"{python_function}({args_str})"

    # Boolean expression visitors
    def visit_BooleanConstantExpression(self, node: BooleanConstantExpression) -> str:
        """Visit a boolean constant expression."""
        return "True" if node.value else "False"

    def visit_BooleanAndExpression(self, node: BooleanAndExpression) -> str:
        """Visit a boolean AND expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} and {right})"

    def visit_BooleanOrExpression(self, node: BooleanOrExpression) -> str:
        """Visit a boolean OR expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} or {right})"

    def visit_BooleanNotExpression(self, node: BooleanNotExpression) -> str:
        """Visit a boolean NOT expression."""
        operand = self.visit(node.expression)
        return f"(not {operand})"

    def visit_BooleanLessTestExpression(self, node: BooleanLessTestExpression) -> str:
        """Visit a boolean less than expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} < {right})"

    def visit_BooleanLessEqualTestExpression(self, node: BooleanLessEqualTestExpression) -> str:
        """Visit a boolean less than or equal expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} <= {right})"

    def visit_BooleanGreaterTestExpression(self, node: BooleanGreaterTestExpression) -> str:
        """Visit a boolean greater than expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} > {right})"

    def visit_BooleanGreaterEqualTestExpression(self, node: BooleanGreaterEqualTestExpression) -> str:
        """Visit a boolean greater than or equal expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} >= {right})"

    def visit_BooleanEqualTestExpression(self, node: BooleanEqualTestExpression) -> str:
        """Visit a boolean equality expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} == {right})"

    def visit_BooleanNotEqualTestExpression(self, node: BooleanNotEqualTestExpression) -> str:
        """Visit a boolean not equal expression."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({left} != {right})"

    def visit_value(self, value: Any) -> str:
        """Visit a value node and return Python representation."""
        if hasattr(value, 'value'):
            if isinstance(value.value, (int, float)):
                return str(value.value)
            elif isinstance(value.value, list): # pragma: no cover
                # Handle array values
                return f"[{', '.join(str(v) for v in value.value)}]"
        return str(value)
