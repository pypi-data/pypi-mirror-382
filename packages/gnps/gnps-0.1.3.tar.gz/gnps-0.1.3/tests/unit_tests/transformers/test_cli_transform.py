"""Tests for cli_transform module."""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from io import StringIO
import os

from gnps.cli_transform import get_transformer, main, TRANSFORMERS
from gnps.transformers import PythonTransformer
from gnps.system import GnpsSystem


class TestGetTransformer:
    """Test the get_transformer function."""

    def test_get_transformer_python(self):
        """Test getting a Python transformer."""
        transformer = get_transformer('python')
        assert isinstance(transformer, PythonTransformer)

    def test_get_transformer_invalid_type(self):
        """Test getting an invalid transformer type."""
        with pytest.raises(ValueError) as excinfo:
            get_transformer('invalid')
        assert "Unsupported transformation type 'invalid'" in str(excinfo.value)
        assert "Available types: python" in str(excinfo.value)


class TestMain:
    """Test the main CLI function."""

    def test_main_help(self):
        """Test CLI help message."""
        with patch('sys.argv', ['gnps-transformer', '--help']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0

    def test_main_no_args(self):
        """Test CLI with no arguments."""
        with patch('sys.argv', ['gnps-transformer']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code != 0

    def test_main_missing_type(self):
        """Test CLI with missing type argument."""
        with patch('sys.argv', ['gnps-transformer', 'test.yaml']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code != 0

    def test_main_invalid_type(self):
        """Test CLI with invalid transformation type."""
        with patch('sys.argv', ['gnps-transformer', 'test.yaml', '-t', 'invalid']):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as excinfo:
                    main()
                assert excinfo.value.code == 2  # argparse returns 2 for invalid choice
                assert "Error: Unsupported transformation type 'invalid'" not in mock_stderr.getvalue()

    def test_main_file_not_found(self):
        """Test CLI with non-existent file."""
        with patch('sys.argv', ['gnps-transformer', 'nonexistent.yaml', '-t', 'python']):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                main()
                assert "Error: File 'nonexistent.yaml' not found" in mock_stderr.getvalue()

    def test_main_successful_transformation(self):
        """Test successful file transformation."""
        # Mock the GnpsSystem.from_yaml and transformer to avoid YAML parsing issues
        mock_system = Mock()
        mock_transformer = Mock()
        mock_transformer.transform.return_value = "# Generated Python code"
        mock_transformer.get_file_extension.return_value = ".py"

        with patch('gnps.cli_transform.GnpsSystem.from_yaml', return_value=mock_system):
            with patch('gnps.cli_transform.get_transformer', return_value=mock_transformer):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    output_dir = Path(tmp_dir)
                    test_file = output_dir / "__test1.yaml"
                    test_file.write_text("dummy content")

                    with patch('sys.argv', [
                        'gnps-transformer',
                        str(test_file),
                        '-t', 'python',
                        '-o', str(output_dir),
                        '--verbose'
                    ]):
                        try:
                            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                                main()

                            # Check that output file was created
                            expected_output_file = output_dir / "__test1.py"
                            assert expected_output_file.exists()

                            # Check verbose output
                            output = mock_stdout.getvalue()
                            assert "Processing:" in output
                            assert "Transformation complete." in output
                        finally:
                            # Clean up any files that might have been created in the project root
                            root_test_file = Path("__test1.py")
                            if root_test_file.exists():
                                os.remove(root_test_file)

    def test_main_with_output_suffix(self):
        """Test transformation with output suffix."""
        # Mock the system and transformer
        mock_system = Mock()
        mock_transformer = Mock()
        mock_transformer.transform.return_value = "# Generated Python code"
        mock_transformer.get_file_extension.return_value = ".py"

        with patch('gnps.cli_transform.GnpsSystem.from_yaml', return_value=mock_system):
            with patch('gnps.cli_transform.get_transformer', return_value=mock_transformer):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    output_dir = Path(tmp_dir)
                    test_file = output_dir / "__test1.yaml"
                    test_file.write_text("dummy content")

                    with patch('sys.argv', [
                        'gnps-transformer',
                        str(test_file),
                        '-t', 'python',
                        '-o', str(output_dir),
                        '--output-suffix', '_generated'
                    ]):
                        try:
                            main()

                            # Check that output file was created with suffix
                            expected_output_file = output_dir / "__test1_generated.py"
                            assert expected_output_file.exists()
                        finally:
                            # Clean up any files that might have been created in the project root
                            root_test_file = Path("__test1.py")
                            if root_test_file.exists():
                                os.remove(root_test_file)
                            root_test_generated_file = Path("__test1_generated.py")
                            if root_test_generated_file.exists():
                                os.remove(root_test_generated_file)

    def test_main_transformation_error(self):
        """Test handling of transformation errors."""
        # Create a temporary file that exists but will cause an error
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "__test1.yaml"
            test_file.write_text("dummy content")

            with patch('gnps.cli_transform.GnpsSystem.from_yaml') as mock_from_yaml:
                mock_from_yaml.side_effect = Exception("Test parsing error")

                with patch('sys.argv', [
                    'gnps-transformer',
                    str(test_file),
                    '-t', 'python',
                    '--verbose'
                ]):
                    try:
                        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                            main()

                            # Check that error was reported
                            error_output = mock_stderr.getvalue()
                            assert f"Error processing '{test_file}'" in error_output
                    finally:
                        # Clean up any files that might have been created in the project root
                        root_test_file = Path("__test1.py")
                        if root_test_file.exists():
                            os.remove(root_test_file)

    def test_main_multiple_files(self):
        """Test processing multiple files."""
        # Mock the system and transformer
        mock_system = Mock()
        mock_transformer = Mock()
        mock_transformer.transform.return_value = "# Generated Python code"
        mock_transformer.get_file_extension.return_value = ".py"

        with patch('gnps.cli_transform.GnpsSystem.from_yaml', return_value=mock_system):
            with patch('gnps.cli_transform.get_transformer', return_value=mock_transformer):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    output_dir = Path(tmp_dir)
                    test_files = []

                    for i in range(2):
                        test_file = output_dir / f"__test1_{i}.yaml"
                        test_file.write_text("dummy content")
                        test_files.append(str(test_file))

                    with patch('sys.argv', [
                        'gnps-transformer',
                        *test_files,
                        '-t', 'python',
                        '-o', str(output_dir)
                    ]):
                        try:
                            main()

                            # Check that both output files were created
                            for i in range(2):
                                expected_output_file = output_dir / f"__test1_{i}.py"
                                assert expected_output_file.exists()
                        finally:
                            # Clean up any files that might have been created in the project root
                            for i in range(2):
                                root_test_file = Path(f"__test1_{i}.py")
                                if root_test_file.exists():
                                    os.remove(root_test_file)

    def test_transformers_registry(self):
        """Test that TRANSFORMERS registry is properly configured."""
        assert 'python' in TRANSFORMERS
        assert TRANSFORMERS['python'] == PythonTransformer

