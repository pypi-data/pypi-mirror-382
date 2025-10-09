"""Tests for footer rendering functionality."""

from nhandu.executor import execute
from nhandu.models import CodeBlock, Document, DocumentMetadata, MarkdownBlock
from nhandu.parser import parse
from nhandu.renderer import render


def test_footer_rendered_by_default():
    """Test that footer is rendered by default in HTML output."""
    content = """# Title

Some content."""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Footer should be present
    assert '<footer class="nhandu-footer">' in html
    assert "Made with" in html
    assert "Nhandu" in html
    assert 'href="https://pypi.org/project/nhandu"' in html


def test_footer_not_in_markdown():
    """Test that footer is NOT rendered in Markdown output."""
    content = """# Title

Some content."""

    doc = parse(content)
    executed = execute(doc)
    md = render(executed, "markdown")

    # Footer should NOT be present in markdown
    assert "Made with" not in md
    assert "nhandu-footer" not in md


def test_footer_suppressed_via_metadata():
    """Test that footer can be suppressed via YAML frontmatter."""
    content = """---
title: Test
show_footer: false
---

# Content"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Footer should NOT be present
    assert '<footer class="nhandu-footer">' not in html
    assert "Made with" not in html or "Nhandu" not in html


def test_footer_enabled_via_metadata():
    """Test that footer can be explicitly enabled via YAML frontmatter."""
    content = """---
title: Test
show_footer: true
---

# Content"""

    doc = parse(content)
    executed = execute(doc)
    html = render(executed, "html")

    # Footer should be present
    assert '<footer class="nhandu-footer">' in html
    assert "Made with" in html
    assert "Nhandu" in html


def test_footer_link_attributes():
    """Test that footer link has correct attributes."""
    doc = Document(
        blocks=[MarkdownBlock("# Title", 1)],
        metadata=DocumentMetadata(show_footer=True),
    )
    executed = execute(doc)
    html = render(executed, "html")

    # Check link attributes
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html


def test_footer_css_included():
    """Test that footer CSS styles are included in HTML."""
    doc = Document(
        blocks=[MarkdownBlock("# Title", 1)],
        metadata=DocumentMetadata(show_footer=True),
    )
    executed = execute(doc)
    html = render(executed, "html")

    # Check CSS is present
    assert ".nhandu-footer" in html
    assert "text-align: center" in html
    assert "border-top:" in html


def test_footer_position_in_html():
    """Test that footer is positioned before closing body tag."""
    doc = Document(
        blocks=[
            MarkdownBlock("# Title", 1),
            CodeBlock("x = 42\nprint(x)", "python", False, 2),
        ],
        metadata=DocumentMetadata(show_footer=True),
    )
    executed = execute(doc)
    html = render(executed, "html")

    # Footer should come after content but before </body>
    footer_pos = html.find('<footer class="nhandu-footer">')
    body_close_pos = html.find("</body>")
    h1_pos = html.find("<h1>")

    assert footer_pos > h1_pos  # Footer after content
    assert footer_pos < body_close_pos  # Footer before closing body tag
    assert footer_pos > 0  # Footer exists


def test_footer_not_rendered_when_disabled():
    """Test that footer is completely absent when disabled."""
    doc = Document(
        blocks=[MarkdownBlock("# Title", 1)],
        metadata=DocumentMetadata(show_footer=False),
    )
    executed = execute(doc)
    html = render(executed, "html")

    # No footer element at all (CSS class may still be in styles section)
    assert "<footer" not in html
    assert 'class="nhandu-footer"' not in html


def test_footer_with_multiple_blocks():
    """Test footer rendering with complex document structure."""
    doc = Document(
        blocks=[
            MarkdownBlock("# Introduction", 1),
            CodeBlock("import sys", "python", True, 2),  # Hidden
            MarkdownBlock("## Section 1", 3),
            CodeBlock("x = 42", "python", False, 4),
            MarkdownBlock("## Conclusion", 5),
        ],
        metadata=DocumentMetadata(show_footer=True),
    )
    executed = execute(doc)
    html = render(executed, "html")

    # Footer should still be present once
    assert html.count('<footer class="nhandu-footer">') == 1
    assert "Made with" in html


def test_footer_default_value():
    """Test that show_footer defaults to True."""
    metadata = DocumentMetadata()
    assert metadata.show_footer is True


def test_footer_from_dict_default():
    """Test that show_footer defaults to True when created from dict."""
    metadata = DocumentMetadata.from_dict({"title": "Test"})
    assert metadata.show_footer is True


def test_footer_from_dict_explicit_false():
    """Test that show_footer can be set to False via from_dict."""
    metadata = DocumentMetadata.from_dict({"title": "Test", "show_footer": False})
    assert metadata.show_footer is False


def test_footer_from_dict_explicit_true():
    """Test that show_footer can be set to True via from_dict."""
    metadata = DocumentMetadata.from_dict({"title": "Test", "show_footer": True})
    assert metadata.show_footer is True
