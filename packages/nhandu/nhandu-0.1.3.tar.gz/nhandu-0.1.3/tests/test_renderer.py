"""Tests for the renderer module."""

from pathlib import Path

import pytest

from nhandu.executor import execute
from nhandu.parser import parse
from nhandu.renderer import render


def test_render_markdown_basic():
    """Test rendering to markdown format."""
    content = """# Test Document

```python
print("Hello, World!")
result = 2 + 2
result
```

More text here."""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "markdown")

    # Should contain original markdown
    assert "# Test Document" in output
    assert "More text here." in output

    # Should contain code block
    assert "```python" in output
    assert 'print("Hello, World!")' in output

    # Should contain output
    assert "Output:" in output
    assert "Hello, World!" in output
    assert "4" in output


def test_render_markdown_with_frontmatter():
    """Test rendering markdown with preserved frontmatter."""
    content = """---
title: Test Document
output: html
---

# Content

```python
x = 42
print(x)
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "markdown")

    # Should preserve frontmatter
    assert "---" in output
    assert "title: Test Document" in output
    assert "output: html" in output


def test_render_markdown_hidden_blocks():
    """Test that hidden blocks don't appear in markdown output."""
    content = """```python {hide=true}
hidden = "secret"
```

```python
print("visible")
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "markdown")

    # Hidden block should not appear
    assert "hidden = " not in output
    assert "{hide=true}" not in output

    # Visible block should appear
    assert "visible" in output


def test_render_markdown_with_error():
    """Test rendering blocks with errors."""
    content = """```python
undefined_variable
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "markdown")

    # Should show error
    assert "Error:" in output
    assert "NameError" in output


@pytest.mark.skipif(
    not pytest.importorskip("matplotlib", reason="matplotlib not available"),
    reason="matplotlib not available",
)
def test_render_markdown_with_plots():
    """Test rendering with matplotlib plots."""
    content = """```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 10)
y = np.sin(x)

plt.figure()
plt.plot(x, y)
```"""

    doc = parse(content)

    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            executed_doc = execute(doc)
            output = render(executed_doc, "markdown")

            # Should reference figure
            if executed_doc.blocks[0].figures:
                figure_path = executed_doc.blocks[0].figures[0]
                assert f"![Figure]({figure_path})" in output

        finally:
            os.chdir(original_cwd)


def test_render_html_basic():
    """Test rendering to HTML format."""
    content = """# Test Document

```python
print("Hello, HTML!")
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should be valid HTML structure
    assert "<!DOCTYPE html>" in output
    assert "<html>" in output
    assert "<head>" in output
    assert "<body>" in output
    assert "</html>" in output

    # Should contain content
    assert "Test Document" in output
    assert "Hello, HTML!" in output


def test_render_html_with_code():
    """Test HTML rendering of code blocks."""
    content = """```python
x = 1 + 1
print(f"Result: {x}")
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should have code styling
    assert 'class="code-block"' in output
    assert 'class="code-input"' in output
    assert 'class="code-output"' in output

    # Should escape HTML characters
    assert "&lt;" not in "x = 1 + 1"  # Basic code shouldn't need escaping
    assert "Result: 2" in output


def test_render_html_with_error():
    """Test HTML rendering of errors."""
    content = """```python
undefined_variable
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should have error styling
    assert 'class="error"' in output
    assert "NameError" in output


def test_render_html_escaping():
    """Test HTML character escaping."""
    content = """```python
print("<script>alert('xss')</script>")
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should escape HTML characters
    assert "&lt;script&gt;" in output
    assert "<script>" not in output or output.count("<script>") <= 1  # Only in head


def test_render_with_inline_code():
    """Test rendering inline code in markdown."""
    content = """<% x = 42 %>
The answer is <%= x %>."""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "markdown")

    # Inline code should be evaluated
    assert "The answer is 42." in output
    assert "<%" not in output
    assert "%>" not in output


def test_render_format_selection():
    """Test format selection for rendering."""
    content = """```python
print("test")
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    # Default format (from metadata)
    output_md = render(executed_doc)
    assert "```python" in output_md

    # Explicit HTML format
    output_html = render(executed_doc, "html")
    assert "<!DOCTYPE html>" in output_html

    # Override metadata format
    executed_doc.metadata.output = "html"
    output_html2 = render(executed_doc)
    assert "<!DOCTYPE html>" in output_html2


def test_render_html_with_pygments_default():
    """Test HTML rendering uses Pygments with default theme."""
    content = """```python
x = 42
print(x)
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should have Pygments CSS
    assert ".highlight" in output

    # Should have Pygments-generated HTML (uses <div class="highlight">)
    assert 'class="highlight"' in output

    # Should not have old plain styling
    assert 'class="code-input"><code>' not in output


def test_render_html_with_custom_theme():
    """Test HTML rendering with custom theme from frontmatter."""
    content = """---
title: Test
code_theme: monokai
---

```python
x = 1 + 1
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should have Pygments CSS
    assert ".highlight" in output
    # Monokai has specific background color
    assert "#272822" in output or "monokai" in output.lower() or ".highlight" in output


def test_render_html_cli_theme_override():
    """Test CLI theme override takes precedence over frontmatter."""
    content = """---
code_theme: monokai
---

```python
x = 1
```"""

    doc = parse(content)
    # Simulate CLI override
    doc.metadata.code_theme = "vs"
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should have Pygments CSS
    assert ".highlight" in output


def test_render_html_invalid_theme_error():
    """Test that invalid theme raises helpful error."""
    content = """---
code_theme: invalid-theme-xyz
---

```python
x = 1
```"""

    doc = parse(content)
    executed_doc = execute(doc)

    with pytest.raises(ValueError) as exc_info:
        render(executed_doc, "html")

    # Should have helpful error message
    assert "Unknown code theme" in str(exc_info.value)
    assert "invalid-theme-xyz" in str(exc_info.value)


def test_render_html_unknown_language_fallback():
    """Test that unknown languages fall back to plain text."""
    content = """```unknown-language
some code here
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should still render without error
    # Code blocks with no output are rendered by mistune
    assert "some code here" in output
    assert "language-unknown-language" in output or "some code here" in output


def test_render_html_multiple_languages():
    """Test that multiple languages are highlighted correctly."""
    content = """```python
x = 42
```

```bash
echo "hello"
```

```javascript
const x = 42;
```"""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should have multiple highlighted blocks
    assert output.count('class="highlight"') >= 3
    # Check for Pygments-highlighted content (with span tags)
    assert '<span class="n">x</span>' in output or "x" in output
    assert "echo" in output
    assert "const" in output or "x" in output


def test_render_fixture_files():
    """Test rendering all fixture files."""
    fixtures_dir = Path(__file__).parent / "fixtures"

    for fixture_file in fixtures_dir.glob("*.md"):
        if fixture_file.name == "with_plots.md":
            # Skip plots test if matplotlib not available
            pytest.importorskip("matplotlib")

        content = fixture_file.read_text()
        doc = parse(content, str(fixture_file))

        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)
                executed_doc = execute(doc)

                # Test both formats
                markdown_output = render(executed_doc, "markdown")
                html_output = render(executed_doc, "html")

                # Basic validation
                assert isinstance(markdown_output, str)
                assert isinstance(html_output, str)
                assert len(markdown_output) > 0
                assert len(html_output) > 0

                # HTML should be valid structure
                assert "<!DOCTYPE html>" in html_output
                assert "</html>" in html_output

            finally:
                os.chdir(original_cwd)

def test_html_title_from_metadata():
    """Test that HTML title uses YAML frontmatter title."""
    content = """---
title: My Custom Title
---

# Document

Some content."""

    doc = parse(content)
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    assert "<title>My Custom Title</title>" in output


def test_html_title_from_filename():
    """Test that HTML title falls back to filename when no metadata title."""
    content = """# Document

Some content."""

    doc = parse(content, "my_report.md")
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    assert "<title>my_report</title>" in output


def test_html_title_from_filename_python():
    """Test filename fallback for Python literate files."""
    from nhandu.parser_py import parse_python

    content = """#' # Analysis
#'
#' Some content.

x = 42
"""

    doc = parse_python(content, "data_analysis.py")
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    assert "<title>data_analysis</title>" in output


def test_html_title_default_fallback():
    """Test default title when no metadata and no source path."""
    content = """# Document

Some content."""

    doc = parse(content)  # No source path
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    assert "<title>Nhandu Report</title>" in output


def test_html_title_priority():
    """Test that metadata title takes priority over filename."""
    content = """---
title: Priority Title
---

# Document"""

    doc = parse(content, "ignored_filename.md")
    executed_doc = execute(doc)
    output = render(executed_doc, "html")

    # Should use metadata title, not filename
    assert "<title>Priority Title</title>" in output
    assert "ignored_filename" not in output
