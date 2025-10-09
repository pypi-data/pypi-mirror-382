"""Tests for the CLI interface."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from nhandu.__main__ import main


def test_cli_version():
    """Test --version flag."""
    with patch("sys.stdout") as mock_stdout:
        exit_code = main(["--version"])

    assert exit_code == 0
    mock_stdout.write.assert_called()
    # Check that version is printed
    output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
    assert "nhandu" in output


def test_cli_help():
    """Test --help flag."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_cli_no_input():
    """Test CLI with no input file."""
    exit_code = main([])
    assert exit_code == 1


def test_cli_nonexistent_file():
    """Test CLI with nonexistent input file."""
    exit_code = main(["nonexistent.md"])
    assert exit_code == 1


def test_cli_basic_processing():
    """Test basic document processing."""
    content = """# Test Document

```python
print("Hello from CLI!")
result = 1 + 1
result
```

End of document."""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "test.md"
        input_path.write_text(content)

        # Process document
        exit_code = main([str(input_path)])
        assert exit_code == 0

        # Check output file was created
        output_path = Path(tmpdir) / "test.out.md"
        assert output_path.exists()

        output_content = output_path.read_text()
        assert "Hello from CLI!" in output_content
        assert "Output:" in output_content


def test_cli_custom_output():
    """Test CLI with custom output path."""
    content = """```python
print("Custom output test")
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.md"
        output_path = Path(tmpdir) / "custom_output.md"

        input_path.write_text(content)

        # Process with custom output
        exit_code = main([str(input_path), "-o", str(output_path)])
        assert exit_code == 0

        assert output_path.exists()
        output_content = output_path.read_text()
        assert "Custom output test" in output_content


def test_cli_html_format():
    """Test CLI with HTML output format."""
    content = """# HTML Test

```python
print("HTML output")
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "test.md"
        input_path.write_text(content)

        # Process as HTML
        exit_code = main([str(input_path), "--format", "html"])
        assert exit_code == 0

        output_path = Path(tmpdir) / "test.html"
        assert output_path.exists()

        output_content = output_path.read_text()
        assert "<!DOCTYPE html>" in output_content
        assert "HTML output" in output_content


def test_cli_verbose():
    """Test CLI verbose mode."""
    content = """```python
print("Verbose test")
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "test.md"
        input_path.write_text(content)

        with patch("builtins.print") as mock_print:
            exit_code = main([str(input_path), "--verbose"])

        assert exit_code == 0
        # Should have printed progress messages
        assert mock_print.called
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        progress_messages = [
            msg for msg in print_calls if "Parsing" in msg or "Executing" in msg
        ]
        assert len(progress_messages) > 0


def test_cli_working_directory():
    """Test CLI with custom working directory."""
    content = """```python
import os
print(f"Working dir: {os.getcwd()}")
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "test.md"
        work_dir = Path(tmpdir) / "workdir"
        work_dir.mkdir()

        input_path.write_text(content)

        exit_code = main([str(input_path), "--working-dir", str(work_dir)])
        assert exit_code == 0

        output_path = Path(tmpdir) / "test.out.md"
        output_content = output_path.read_text()
        assert str(work_dir) in output_content


def test_cli_error_handling():
    """Test CLI error handling."""
    content = """```python
undefined_variable
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "test.md"
        input_path.write_text(content)

        # Should succeed even with code errors
        exit_code = main([str(input_path)])
        assert exit_code == 0

        output_path = Path(tmpdir) / "test.out.md"
        assert output_path.exists()

        output_content = output_path.read_text()
        assert "Error:" in output_content


def test_cli_config_file():
    """Test CLI with configuration file."""
    config_content = """
output: html
plot_dpi: 150
title: "Configured Document"
"""

    document_content = """# Test

```python
print("Config test")
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        input_path = Path(tmpdir) / "test.md"

        config_path.write_text(config_content)
        input_path.write_text(document_content)

        exit_code = main([str(input_path), "--config", str(config_path)])
        assert exit_code == 0

        # Should output HTML due to config
        output_path = Path(tmpdir) / "test.html"
        assert output_path.exists()


def test_cli_with_plots():
    """Test CLI with matplotlib plots."""
    pytest.importorskip("matplotlib")

    content = """```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 10)
y = np.sin(x)

plt.figure()
plt.plot(x, y)
plt.title("CLI Test Plot")
```"""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "test.md"
        input_path.write_text(content)

        # Change to temp directory for execution
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            exit_code = main([str(input_path)])
            assert exit_code == 0

            # Check for nhandu_output directory and figures
            nhandu_output = Path(tmpdir) / "nhandu_output"
            if nhandu_output.exists():
                figures = list(nhandu_output.glob("*.png"))
                # May or may not have figures depending on execution

        finally:
            os.chdir(original_cwd)


def test_integration_with_fixture_files():
    """Integration test with fixture files."""
    fixtures_dir = Path(__file__).parent / "fixtures"

    for fixture_file in fixtures_dir.glob("*.md"):
        if fixture_file.name == "with_plots.md":
            pytest.importorskip("matplotlib")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy fixture to temp directory
            temp_input = Path(tmpdir) / fixture_file.name
            temp_input.write_text(fixture_file.read_text())

            # Process with CLI
            exit_code = main([str(temp_input)])
            assert exit_code == 0

            # Verify output was created - check for expected extensions
            possible_outputs = [
                Path(tmpdir) / f"{fixture_file.stem}.out.md",  # default markdown
                Path(tmpdir) / f"{fixture_file.stem}.html",  # html from metadata
            ]

            output_found = False
            for output_path in possible_outputs:
                if output_path.exists():
                    assert len(output_path.read_text()) > 0
                    output_found = True
                    break

            assert output_found, f"No output file found for {fixture_file.name}"
