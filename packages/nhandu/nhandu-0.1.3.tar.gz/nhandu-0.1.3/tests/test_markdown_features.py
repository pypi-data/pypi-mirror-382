"""Tests for extended markdown features (tables, strikethrough, footnotes)."""

from nhandu.executor import execute
from nhandu.parser import parse
from nhandu.renderer import render


def test_table_rendering():
    """Test that markdown tables render as HTML tables."""
    content = """# Document

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have table tags
    assert "<table>" in html
    assert "</table>" in html
    assert "<thead>" in html
    assert "<tbody>" in html
    assert "<th>Header 1</th>" in html
    assert "<td>Cell 1</td>" in html


def test_table_with_formatting():
    """Test tables with inline formatting (bold, italic, etc)."""
    content = """
| Measure | Range | Status |
|---------|-------|--------|
| **MLE** | [0,1] | ✓ Yes  |
| *PMI*   | (-∞,+∞) | ✗ No |
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have table
    assert "<table>" in html
    # Should preserve formatting inside cells
    assert "<strong>MLE</strong>" in html
    assert "<em>PMI</em>" in html


def test_table_alignment():
    """Test table column alignment."""
    content = """
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have table with alignment
    assert "<table>" in html
    # Mistune should handle alignment
    assert "<th" in html


def test_strikethrough():
    """Test strikethrough text rendering."""
    content = """# Document

This is ~~strikethrough~~ text.
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have del tag for strikethrough
    assert "<del>strikethrough</del>" in html


def test_footnotes():
    """Test footnote rendering."""
    content = """# Document

Here is a footnote[^1].

[^1]: This is the footnote text.
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have footnote markup
    assert "footnote" in html.lower()


def test_complex_table():
    """Test complex table from user's example."""
    content = """### Measure Properties

| Measure | Range | Asymmetric? | Interpretation |
|---------|-------|-------------|----------------|
| **MLE** | [0,1] | ✓ Yes | Direct conditional probability |
| **PMI** | (-∞,+∞) | ✗ No | Information content (0 = independent) |
| **Jaccard** | [0,1] | ✗ No | Context overlap similarity |

**Note:** Even symmetric measures like PMI return two values in ASymCat for
consistency, but both values are identical.
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have table
    assert "<table>" in html
    assert "<thead>" in html
    assert "<tbody>" in html

    # Should have all headers
    assert "<th>Measure</th>" in html
    assert "<th>Range</th>" in html
    assert "<th>Asymmetric?</th>" in html
    assert "<th>Interpretation</th>" in html

    # Should have bold measures
    assert "<strong>MLE</strong>" in html
    assert "<strong>PMI</strong>" in html
    assert "<strong>Jaccard</strong>" in html

    # Should have the note as separate paragraph
    assert "<strong>Note:</strong>" in html

    # Should NOT render as pipe-separated paragraph
    assert "| Measure |" not in html


def test_table_not_in_markdown_output():
    """Test that tables are preserved in markdown output."""
    content = """
| A | B |
|---|---|
| 1 | 2 |
"""

    doc = parse(content)
    executed = execute(doc)
    md = render(executed, "markdown")

    # Markdown output should preserve table syntax
    assert "| A | B |" in md
    # Should NOT have HTML table tags
    assert "<table>" not in md


def test_empty_table_cells():
    """Test tables with empty cells."""
    content = """
| Col1 | Col2 |
|------|------|
| A    |      |
|      | B    |
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    assert "<table>" in html
    assert "<td>A</td>" in html
    assert "<td>B</td>" in html


def test_table_with_code():
    """Test tables containing inline code."""
    content = """
| Function | Returns |
|----------|---------|
| `len()`  | int     |
| `str()`  | string  |
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    assert "<table>" in html
    assert "<code>len()</code>" in html
    assert "<code>str()</code>" in html


def test_multiple_tables():
    """Test document with multiple tables."""
    content = """# Doc

## Table 1
| A | B |
|---|---|
| 1 | 2 |

## Table 2
| X | Y |
|---|---|
| 3 | 4 |
"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Should have both tables
    assert html.count("<table>") == 2
    assert "<td>1</td>" in html
    assert "<td>4</td>" in html


def test_table_in_python_literate_format():
    """Test table rendering in Python literate format."""
    from nhandu.parser_py import parse_python

    content = """#' # Analysis
#'
#' | Method | Accuracy |
#' |--------|----------|
#' | A      | 95%      |
#' | B      | 87%      |

print("Analysis complete")
"""

    doc = parse_python(content)
    executed = execute(doc)
    html = render(executed, "html")

    assert "<table>" in html
    assert "<th>Method</th>" in html
    assert "<td>A</td>" in html
    assert "<td>95%</td>" in html
