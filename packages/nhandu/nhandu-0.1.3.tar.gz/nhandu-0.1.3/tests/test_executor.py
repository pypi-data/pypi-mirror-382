"""Tests for the executor module."""

import tempfile
from pathlib import Path

import pytest

from nhandu.executor import execute
from nhandu.parser import parse


def test_execute_basic_code():
    """Test executing basic Python code."""
    content = """```python
x = 2 + 2
print(f"Result: {x}")
x
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[0]
    assert code_block.output is not None
    assert "Result: 4" in code_block.output
    assert "4" in code_block.output  # Return value
    assert code_block.error is None


def test_execute_with_shared_namespace():
    """Test that code blocks share namespace."""
    content = """```python
x = 42
```

```python
y = x * 2
print(f"y = {y}")
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    # First block sets x
    assert executed_doc.blocks[0].output is None  # No output

    # Second block uses x
    code_block = executed_doc.blocks[1]
    assert "y = 84" in code_block.output


def test_execute_with_error():
    """Test error handling during execution."""
    content = """```python
undefined_variable
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[0]
    assert code_block.error is not None
    assert "NameError" in code_block.error
    assert "undefined_variable" in code_block.error


def test_execute_continues_after_error():
    """Test that execution continues after an error."""
    content = """```python
print("Before error")
```

```python
undefined_variable
```

```python
print("After error")
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    # First block succeeds
    assert "Before error" in executed_doc.blocks[0].output
    assert executed_doc.blocks[0].error is None

    # Second block has error
    assert executed_doc.blocks[1].error is not None

    # Third block still executes
    assert "After error" in executed_doc.blocks[2].output
    assert executed_doc.blocks[2].error is None


def test_execute_inline_code():
    """Test executing inline code in markdown."""
    content = """<% x = 42 %>
The value is <%= x %> and double is <%= x * 2 %>."""

    doc = parse(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "The value is 42" in markdown_block.content
    assert "double is 84" in markdown_block.content


def test_execute_non_python_code():
    """Test that non-Python code blocks are not executed."""
    content = """```bash
echo "This should not execute"
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    code_block = executed_doc.blocks[0]
    assert code_block.output is None
    assert code_block.error is None


def test_execute_hidden_blocks():
    """Test that hidden blocks still execute."""
    content = """```python {hide=true}
hidden_var = "secret"
```

```python
print(f"Hidden var: {hidden_var}")
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    # Hidden block executes but output won't be shown in rendering
    hidden_block = executed_doc.blocks[0]
    assert hidden_block.hidden is True

    # Visible block can access variables from hidden block
    visible_block = executed_doc.blocks[1]
    assert "Hidden var: secret" in visible_block.output


@pytest.mark.skipif(
    not pytest.importorskip("matplotlib", reason="matplotlib not available"),
    reason="matplotlib not available",
)
def test_execute_with_plots():
    """Test executing code that creates matplotlib plots."""
    content = """```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 10)
y = np.sin(x)

plt.figure()
plt.plot(x, y)
plt.title("Test Plot")
```"""

    doc = parse(content)

    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        try:
            # Change to temp directory for plot output
            import os

            os.chdir(tmpdir)

            executed_doc = execute(doc)

            code_block = executed_doc.blocks[0]
            assert len(code_block.figures) > 0

            # Check that figure file was created
            figure_path = code_block.figures[0]
            assert figure_path.exists()
            assert figure_path.suffix == ".png"

        finally:
            os.chdir(original_cwd)


def test_execute_with_working_dir():
    """Test executing with a specific working directory."""
    content = """```python
import os
print(f"Current directory: {os.getcwd()}")
```"""

    doc = parse(content)

    with tempfile.TemporaryDirectory() as tmpdir:
        executed_doc = execute(doc, working_dir=tmpdir)

        code_block = executed_doc.blocks[0]
        assert tmpdir in code_block.output


def test_execute_expression_vs_statement():
    """Test difference between expressions and statements."""
    content = """```python
# Expression - should show return value
2 + 2
```

```python
# Statement - should not show return value
x = 2 + 2
```

```python
# Expression again
x
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    # Expression shows result
    assert "4" in executed_doc.blocks[0].output

    # Assignment doesn't show result
    assert executed_doc.blocks[1].output is None or executed_doc.blocks[1].output == ""

    # Variable reference shows value
    assert "4" in executed_doc.blocks[2].output


def test_execute_fixture_files():
    """Test executing all fixture files."""
    fixtures_dir = Path(__file__).parent / "fixtures"

    for fixture_file in fixtures_dir.glob("*.md"):
        if fixture_file.name == "with_plots.md":
            # Skip plots test if matplotlib not available
            pytest.importorskip("matplotlib")

        content = fixture_file.read_text()
        doc = parse(content, str(fixture_file))

        executed_doc = execute(doc)

        # Should return ExecutedDocument
        assert hasattr(executed_doc, "namespace")
        assert isinstance(executed_doc.namespace, dict)

        # Should have same number of blocks
        assert len(executed_doc.blocks) == len(doc.blocks)
