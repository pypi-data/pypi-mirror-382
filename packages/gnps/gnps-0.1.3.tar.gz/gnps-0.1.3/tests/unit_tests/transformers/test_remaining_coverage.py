"""Additional tests to cover remaining uncovered lines and edge cases."""

import pytest
from unittest.mock import Mock, patch
from io import StringIO
import tempfile
from pathlib import Path
import os

from gnps.transformers.python_transformer import PythonTransformer
from gnps.cli_transform import get_transformer, main
from gnps.parser.ast.value import NumericalValue


class TestRemainingCoverage:
    """Tests to cover remaining uncovered lines."""

    def test_cli_transform_get_transformer_error_handling(self):
        """Test error handling in get_transformer when called through main."""
        with patch('sys.argv', ['gnps-transformer', 'test.yaml', '-t', 'python']):
            with patch('gnps.cli_transform.get_transformer') as mock_get_transformer:
                mock_get_transformer.side_effect = ValueError("Test error")
                with patch('sys.stderr', new_callable=Mock):
                    with pytest.raises(SystemExit) as excinfo:
                        main()
                    assert excinfo.value.code == 1

    def test_python_transformer_csv_without_output_vars(self):
        """Test CSV generation when system has no output variables."""
        transformer = PythonTransformer()

        # Create system without output variables but with input variables
        system = Mock()
        system.cells = []
        system.rules = []
        system.input_variables = {"input_x": Mock()}
        system.output_variables = None

        result = transformer.transform(system)

        # Should handle case where no output variables are defined
        assert "# No output variables defined, return all variables" in result

    def test_python_transformer_csv_no_inputs_no_outputs(self):
        """Test CSV generation when system has no input or output variables."""
        transformer = PythonTransformer()

        # Create system without input or output variables
        system = Mock()
        system.cells = []
        system.rules = []
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should generate CSV writer with all variables
        assert "all_vars = system.get_variables()" in result
        assert "fieldnames = ['step'] + list(all_vars.keys())" in result

    def test_python_transformer_consumer_attribute_access(self):
        """Test when consumer has name attribute vs string representation."""
        transformer = PythonTransformer()

        # Create mock rule with consumer that has no name attribute
        guard = Mock()
        producer = Mock()

        # Create a simple consumer object that returns string representation
        class SimpleConsumer:
            def __str__(self):
                return "consumer_var"

        consumer = SimpleConsumer()

        # Mock get_variables method
        producer.get_variables = Mock(return_value={})

        rule = Mock()
        rule.guard = guard
        rule.producer = producer
        rule.consumer = consumer

        # Create system with rule
        system = Mock()
        system.cells = []
        system.rules = [rule]
        system.input_variables = None
        system.output_variables = None

        result = transformer.transform(system)

        # Should use string representation when name attribute is not available
        assert "consumer_var_new +=" in result

    def test_python_transformer_input_variable_error_path(self):
        """Test input variable error handling path in CSV processing."""
        transformer = PythonTransformer()

        # Create system with input variables to generate CSV processing code
        system = Mock()
        system.cells = []
        system.rules = []
        system.input_variables = {"missing_var": Mock()}
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain error handling for missing input variables
        assert "if 'missing_var' in input_row:" in result
        assert "else:" in result
        assert "print(f'Error: Input variable missing_var not found" in result
        assert "sys.exit(1)" in result

    def test_python_transformer_no_input_warning_path(self):
        """Test warning path when no input data is found."""
        transformer = PythonTransformer()

        # Create system with input variables to generate the CSV processing path
        system = Mock()
        system.cells = []
        system.rules = []
        system.input_variables = {"input_x": Mock()}
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain warning for no input data
        assert "if step_num == 0:" in result
        assert "print('Warning: No input data found.', file=sys.stderr)" in result

    def test_python_transformer_success_message_path(self):
        """Test success message path in CSV processing."""
        transformer = PythonTransformer()

        # Create system with input variables
        system = Mock()
        system.cells = []
        system.rules = []
        system.input_variables = {"input_x": Mock()}
        system.output_variables = None

        result = transformer.transform(system)

        # Should contain success message
        assert "else:" in result
        assert "print(f'Processed {step_num} input rows successfully.', file=sys.stderr)" in result

    def test_base_transformer_abstract_methods(self):
        """Test that BaseTransformer abstract methods are properly defined."""
        from gnps.transformers.base_transformer import BaseTransformer

        # Verify that trying to instantiate abstract class fails
        with pytest.raises(TypeError):
            BaseTransformer()

        # Verify abstract methods exist
        assert hasattr(BaseTransformer, 'transform')
        assert hasattr(BaseTransformer, 'get_file_extension')

    def test_base_transformer_concrete_methods(self):
        """Test concrete methods that might not be covered."""
        from gnps.transformers.base_transformer import BaseTransformer

        # Create a concrete implementation to test the concrete methods
        class TestTransformer(BaseTransformer):
            def transform(self, system):
                # Test the concrete methods during transformation
                self.reset()
                self.add_line("test line")
                self.add_line("indented line", indent=1)
                self.add_line()  # empty line
                return self.get_output()

            def get_file_extension(self):
                return ".test"

        transformer = TestTransformer()
        result = transformer.transform(None)

        # Verify the concrete methods worked correctly
        assert "test line" in result
        assert "    indented line" in result
        lines = result.split('\n')
        assert len(lines) == 3  # test line, indented line, empty line

    def test_transformers_init_coverage(self):
        """Test transformers __init__ module for 100% coverage."""
        # Import the module to ensure it's executed
        import gnps.transformers

        # Verify the imports work
        from gnps.transformers import BaseTransformer, PythonTransformer
        assert BaseTransformer is not None
        assert PythonTransformer is not None

    def test_cli_verbose_traceback_path(self):
        """Test the verbose traceback path in CLI error handling."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "__test1.yaml"
            test_file.write_text("dummy content")

            with patch('gnps.cli_transform.GnpsSystem.from_yaml') as mock_from_yaml:
                mock_from_yaml.side_effect = Exception("Test parsing error")

                with patch('sys.argv', [
                    'gnps-transformer',
                    str(test_file),
                    '-t', 'python',
                    '--verbose'  # This should trigger traceback printing
                ]):
                    with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                        with patch('traceback.print_exc') as mock_traceback:
                            main()

                            # Verify traceback was printed in verbose mode
                            mock_traceback.assert_called_once()

    def test_cli_directory_creation(self):
        """Test that CLI creates output directory if it doesn't exist."""
        import os
        mock_system = Mock()
        mock_transformer = Mock()
        mock_transformer.transform.return_value = "# Generated Python code"
        mock_transformer.get_file_extension.return_value = ".py"

        with patch('gnps.cli_transform.GnpsSystem.from_yaml', return_value=mock_system):
            with patch('gnps.cli_transform.get_transformer', return_value=mock_transformer):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    test_file = Path(tmp_dir) / "__test1.yaml"
                    test_file.write_text("dummy content")

                    # Use a non-existent output directory
                    output_dir = Path(tmp_dir) / "non_existent" / "subdir"

                    with patch('sys.argv', [
                        'gnps-transformer',
                        str(test_file),
                        '-t', 'python',
                        '-o', str(output_dir)
                    ]):
                        try:
                            main()

                            # Check that directory was created and file exists
                            assert output_dir.exists()
                            expected_output_file = output_dir / "__test1.py"
                            assert expected_output_file.exists()
                        finally:
                            # Clean up any files that might have been created in the project root
                            root_test_file = Path("__test1.py")
                            if root_test_file.exists():
                                os.remove(root_test_file)
