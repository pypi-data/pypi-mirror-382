"""Tests for empty block filtering."""

from nhandu.executor import execute
from nhandu.models import CodeBlock, MarkdownBlock
from nhandu.parser import parse
from nhandu.parser_py import parse_python
from nhandu.renderer import render


def test_empty_code_block_markdown():
    """Test that empty code blocks in markdown format are filtered out."""
    content = """# Title

Some text.

```python

```

More text."""

    doc = parse(content)

    # Should only have markdown blocks, no empty code block
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_empty_code_block_with_whitespace():
    """Test that code blocks with only whitespace are filtered."""
    content = """```python


```

Text after."""

    doc = parse(content)

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], MarkdownBlock)


def test_empty_python_code_with_comments():
    """Test that Python code blocks with only comments are filtered."""
    content = """```python
# Just a comment

# Another comment
```

Text."""

    doc = parse(content)

    # Empty (comments-only) code block should be filtered
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], MarkdownBlock)


def test_non_empty_python_code_with_comments():
    """Test that Python code with comments AND actual code is not filtered."""
    content = """```python
# Comment
x = 42
```"""

    doc = parse(content)

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], CodeBlock)
    assert "x = 42" in doc.blocks[0].content


def test_empty_markdown_block():
    """Test that empty markdown blocks are filtered in Python literate format."""
    content = """#' # Title
#'
#'

x = 42"""

    doc = parse_python(content)

    # Should have 1 markdown block and 1 code block, no empty markdown
    assert len(doc.blocks) == 2
    assert isinstance(doc.blocks[0], MarkdownBlock)
    assert isinstance(doc.blocks[1], CodeBlock)
    assert doc.blocks[0].content.strip() == "# Title"


def test_empty_code_block_python_literate():
    """Test that empty code blocks in Python literate format are filtered."""
    content = """#' # Title

# Just comments


#' More text."""

    doc = parse_python(content)

    # Should only have markdown blocks
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_empty_hidden_block():
    """Test that empty hidden blocks are filtered."""
    content = """#' # Title

#| hide

#|

#' Text after."""

    doc = parse_python(content)

    # Should only have markdown blocks, no empty hidden block
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_empty_hidden_block_with_comments():
    """Test that hidden blocks with only comments are filtered."""
    content = """#' # Title

#| hide
# Setup comment
# Another comment
#|

#' Text after."""

    doc = parse_python(content)

    # Should only have markdown blocks
    assert len(doc.blocks) == 2
    assert all(isinstance(block, MarkdownBlock) for block in doc.blocks)


def test_non_empty_hidden_block():
    """Test that non-empty hidden blocks are preserved."""
    content = """#' # Title

#| hide
import sys
x = 42
#|

#' Text after."""

    doc = parse_python(content)

    # Should have 2 markdown blocks and 1 hidden code block
    assert len(doc.blocks) == 3
    assert isinstance(doc.blocks[1], CodeBlock)
    assert doc.blocks[1].hidden is True
    assert "import sys" in doc.blocks[1].content


def test_defensive_render_empty_code_with_output():
    """Test defensive rendering: empty code block with output is rendered."""
    # Manually create a document with empty code but output
    # (shouldn't happen in normal flow, but defensive)
    from nhandu.models import DocumentMetadata, ExecutedDocument

    code_block = CodeBlock(content="   ", language="python")
    code_block.output = "Some output appeared"

    doc = ExecutedDocument(
        blocks=[code_block],
        metadata=DocumentMetadata(),
    )

    # Should render because it has output
    html_output = render(doc, "html")
    assert "Some output appeared" in html_output

    md_output = render(doc, "markdown")
    assert "Some output appeared" in md_output


def test_defensive_render_empty_code_with_error():
    """Test defensive rendering: empty code block with error is rendered."""
    from nhandu.models import DocumentMetadata, ExecutedDocument

    code_block = CodeBlock(content="", language="python")
    code_block.error = "RuntimeError: Something went wrong"

    doc = ExecutedDocument(
        blocks=[code_block],
        metadata=DocumentMetadata(),
    )

    # Should render because it has error
    html_output = render(doc, "html")
    assert "RuntimeError" in html_output

    md_output = render(doc, "markdown")
    assert "RuntimeError" in md_output


def test_mixed_empty_and_non_empty_blocks():
    """Test document with mix of empty and non-empty blocks."""
    content = """#' # Title

```python

```

#' Section 1

```python
x = 42
print(x)
```

```python
# Just a comment
```

#' Section 2"""

    doc = parse(content)

    # Should have 3 markdown blocks and 1 code block
    # Empty code blocks are filtered
    assert len(doc.blocks) == 4
    markdown_blocks = [b for b in doc.blocks if isinstance(b, MarkdownBlock)]
    code_blocks = [b for b in doc.blocks if isinstance(b, CodeBlock)]

    assert len(markdown_blocks) == 3
    assert len(code_blocks) == 1
    assert "x = 42" in code_blocks[0].content


def test_javascript_empty_code_block():
    """Test that empty code blocks in other languages are filtered."""
    content = """```javascript
// Just comments
// More comments
```

Text."""

    doc = parse(content)

    # JavaScript with only comments should use simple whitespace check
    # (not filtered since it's not Python and has non-whitespace content)
    assert len(doc.blocks) == 2
    assert isinstance(doc.blocks[0], CodeBlock)


def test_javascript_truly_empty():
    """Test that truly empty JavaScript blocks are filtered."""
    content = """```javascript

```

Text."""

    doc = parse(content)

    # Truly empty (whitespace only) should be filtered regardless of language
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], MarkdownBlock)


def test_rendering_filters_empty_blocks():
    """Test that renderer filters out any empty blocks that slip through."""
    from nhandu.models import Document, DocumentMetadata

    # Manually create blocks including some empty ones
    blocks = [
        MarkdownBlock("# Title", 1),
        MarkdownBlock("   ", 2),  # Whitespace only
        CodeBlock("x = 42", "python", False, 3),
        MarkdownBlock("", 4),  # Empty
    ]

    doc = Document(blocks=blocks, metadata=DocumentMetadata())
    executed = execute(doc)

    html = render(executed, "html")
    md = render(executed, "markdown")

    # Should only render non-empty blocks
    # HTML converts markdown headings
    assert "<h1>Title</h1>" in html or "# Title" in html
    assert "x" in html and "42" in html  # Code is rendered
    assert "# Title" in md
    assert "x = 42" in md
