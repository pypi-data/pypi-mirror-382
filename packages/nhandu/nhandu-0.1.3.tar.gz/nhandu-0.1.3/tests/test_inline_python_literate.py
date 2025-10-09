"""Tests for inline code in Python literate format."""

from nhandu.executor import execute
from nhandu.parser_py import parse_python
from nhandu.renderer import render


def test_inline_expression_in_python_literate():
    """Test inline expressions in Python literate format."""
    content = """#' Result: <%= 2 + 2 %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "Result: 4" in markdown_block.content


def test_inline_statement_in_python_literate():
    """Test inline statements in Python literate format."""
    content = """#' <% x = 42 %>
#' The value is <%= x %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "The value is 42" in markdown_block.content


def test_inline_code_with_regular_code_blocks():
    """Test inline code referencing variables from regular code blocks."""
    content = """#' # Report
#'
#' <% import datetime %>
#' Today: <%= datetime.date.today() %>

x = 100
y = 50

#' Sum: <%= x + y %>
#' Product: <%= x * y %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    # Find markdown blocks
    markdown_blocks = [
        b for b in executed_doc.blocks if b.block_type.value == "markdown"
    ]

    # Check first markdown block has date
    assert "Today:" in markdown_blocks[0].content

    # Check second markdown block has calculations
    assert "Sum: 150" in markdown_blocks[1].content
    assert "Product: 5000" in markdown_blocks[1].content


def test_inline_code_with_hidden_blocks():
    """Test inline code with hidden code blocks."""
    content = """#' # Analysis
#'
#' <% import math %>

#| hide
radius = 10
#|

#' Area: <%= math.pi * radius ** 2 %>
#' Circumference: <%= 2 * math.pi * radius %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_blocks = [
        b for b in executed_doc.blocks if b.block_type.value == "markdown"
    ]

    # Should have calculations with radius from hidden block
    assert "Area:" in markdown_blocks[1].content
    assert "314.159" in markdown_blocks[1].content
    assert "Circumference:" in markdown_blocks[1].content
    assert "62.83" in markdown_blocks[1].content


def test_inline_code_multiple_expressions():
    """Test multiple inline expressions in one markdown block."""
    content = """#' Values: <%= 1 %>, <%= 2 %>, <%= 3 %>
#' Sum: <%= 1 + 2 + 3 %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "Values: 1, 2, 3" in markdown_block.content
    assert "Sum: 6" in markdown_block.content


def test_inline_code_with_formatting():
    """Test inline code with formatted strings."""
    content = """#' <% value = 1234.5678 %>
#' Default: <%= value %>
#' Formatted: <%= f"{value:.2f}" %>
#' With commas: <%= f"{value:,.2f}" %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "Default: 1234.5678" in markdown_block.content
    assert "Formatted: 1234.57" in markdown_block.content
    assert "With commas: 1,234.57" in markdown_block.content


def test_inline_code_conditional():
    """Test inline code with conditional logic."""
    content = """#' <% x = 90 %>
#' <% result = "pass" if x >= 60 else "fail" %>
#' Score: <%= x %>
#' Result: <%= result %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "Score: 90" in markdown_block.content
    assert "Result: pass" in markdown_block.content


def test_inline_code_list_comprehension():
    """Test inline code with list comprehension."""
    content = """#' <% numbers = [1, 2, 3, 4, 5] %>
#' Squares: <%= [n**2 for n in numbers] %>
#' Evens: <%= [n for n in numbers if n % 2 == 0] %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_block = executed_doc.blocks[0]
    assert "Squares: [1, 4, 9, 16, 25]" in markdown_block.content
    assert "Evens: [2, 4]" in markdown_block.content


def test_inline_code_shared_namespace():
    """Test that inline code shares namespace across blocks."""
    content = """#' <% counter = 0 %>
#' Initial: <%= counter %>

x = 10

#' <% counter = counter + x %>
#' After increment: <%= counter %>"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_blocks = [
        b for b in executed_doc.blocks if b.block_type.value == "markdown"
    ]

    assert "Initial: 0" in markdown_blocks[0].content
    assert "After increment: 10" in markdown_blocks[1].content


def test_inline_code_error_handling():
    """Test that inline code errors are handled gracefully."""
    content = """#' Before error
#' Value: <%= undefined_variable %>
#' After error"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    # Should keep original text on error
    markdown_block = executed_doc.blocks[0]
    assert "Before error" in markdown_block.content
    # Original inline code should remain if there's an error
    assert "undefined_variable" in markdown_block.content


def test_inline_code_rendering_html():
    """Test that inline code renders correctly in HTML."""
    content = """#' <% x = 42 %>
#' The answer is <%= x %>."""

    doc = parse_python(content)
    executed_doc = execute(doc)
    html_output = render(executed_doc, "html")

    assert "The answer is 42." in html_output
    # Should not contain the inline code syntax in output
    assert "<%=" not in html_output
    assert "%>" not in html_output


def test_inline_code_rendering_markdown():
    """Test that inline code renders correctly in Markdown."""
    content = """#' <% name = "Nhandu" %>
#' Welcome to <%= name %>!"""

    doc = parse_python(content)
    executed_doc = execute(doc)
    md_output = render(executed_doc, "markdown")

    assert "Welcome to Nhandu!" in md_output
    # Should not contain the inline code syntax in output
    assert "<%=" not in md_output
    assert "%>" not in md_output


def test_inline_code_complex_example():
    """Test a complex real-world example with inline code."""
    content = """#' # Sales Report
#'
#' <% import datetime %>
#' Report generated: <%= datetime.date.today() %>

sales_q1 = 125000
sales_q2 = 148000
sales_q3 = 162000
sales_q4 = 189000

#' <% total = sales_q1 + sales_q2 + sales_q3 + sales_q4 %>
#' <% avg = total / 4 %>
#' <% growth = ((sales_q4 - sales_q1) / sales_q1) * 100 %>
#' <% target = 500000 %>
#' <% status = "exceeded" if total > target else "below" %>
#'
#' ## Summary
#'
#' - Total Sales: $<%= f"{total:,}" %>
#' - Average: $<%= f"{avg:,.0f}" %>
#' - Growth: <%= f"{growth:.1f}" %>%
#' - Status: <%= status %> target"""

    doc = parse_python(content)
    executed_doc = execute(doc)

    markdown_blocks = [
        b for b in executed_doc.blocks if b.block_type.value == "markdown"
    ]

    # Check report header
    assert "Report generated:" in markdown_blocks[0].content

    # Check summary calculations
    summary = markdown_blocks[1].content
    assert "Total Sales: $624,000" in summary
    assert "Average: $156,000" in summary
    assert "Growth: 51.2%" in summary
    assert "Status: exceeded target" in summary
