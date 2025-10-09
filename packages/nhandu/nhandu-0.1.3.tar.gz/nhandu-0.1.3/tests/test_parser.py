"""Tests for the parser module."""

from pathlib import Path

from nhandu.models import CodeBlock, MarkdownBlock
from nhandu.parser import parse


def test_parse_basic_document():
    """Test parsing a basic document with code blocks."""
    content = """# Title

Some text here.

```python
print("hello")
x = 42
```

More text."""

    doc = parse(content)

    assert len(doc.blocks) == 3
    assert isinstance(doc.blocks[0], MarkdownBlock)
    assert isinstance(doc.blocks[1], CodeBlock)
    assert isinstance(doc.blocks[2], MarkdownBlock)

    code_block = doc.blocks[1]
    assert code_block.language == "python"
    assert 'print("hello")' in code_block.content
    assert "x = 42" in code_block.content


def test_parse_with_frontmatter():
    """Test parsing document with YAML frontmatter."""
    content = """---
title: Test Document
output: html
plot_dpi: 150
---

# Content

Some content here."""

    doc = parse(content)

    assert doc.metadata.title == "Test Document"
    assert doc.metadata.output == "html"
    assert doc.metadata.plot_dpi == 150
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], MarkdownBlock)


def test_parse_hidden_code_blocks():
    """Test parsing hidden code blocks."""
    content = """```python {hide=true}
hidden_code = True
```

```python {hidden}
also_hidden = True
```

```python
visible_code = True
```"""

    doc = parse(content)

    assert len(doc.blocks) == 3
    assert all(isinstance(block, CodeBlock) for block in doc.blocks)

    assert doc.blocks[0].hidden is True
    assert doc.blocks[1].hidden is True
    assert doc.blocks[2].hidden is False


def test_parse_multiple_languages():
    """Test parsing code blocks with different languages."""
    content = """```python
python_code = True
```

```javascript
let jsCode = true;
```

```bash
echo "shell command"
```"""

    doc = parse(content)

    assert len(doc.blocks) == 3
    assert doc.blocks[0].language == "python"
    assert doc.blocks[1].language == "javascript"
    assert doc.blocks[2].language == "bash"


def test_extract_inline_code():
    """Test extracting inline code from markdown."""
    from nhandu.parser import NhanduParser

    parser = NhanduParser()
    text = "The result is <%= 2 + 2 %> and <% x = 5 %> the value is <%= x %>."

    inline_codes = parser.extract_inline_code(text)

    assert len(inline_codes) == 3
    assert inline_codes[0].expression == "2 + 2"
    assert inline_codes[0].is_statement is False
    assert inline_codes[1].expression == "x = 5"
    assert inline_codes[1].is_statement is True
    assert inline_codes[2].expression == "x"
    assert inline_codes[2].is_statement is False


def test_parse_fixture_files():
    """Test parsing all fixture files."""
    fixtures_dir = Path(__file__).parent / "fixtures"

    for fixture_file in fixtures_dir.glob("*.md"):
        content = fixture_file.read_text()
        doc = parse(content, str(fixture_file))

        # Basic validation
        assert isinstance(doc.blocks, list)
        assert doc.source_path == fixture_file

        # Should have at least some content
        assert len(doc.blocks) > 0


def test_parse_invalid_yaml():
    """Test parsing with invalid YAML frontmatter."""
    content = """---
title: Test
invalid: [unclosed list
---

# Content"""

    doc = parse(content)

    # Should fall back to default metadata
    assert doc.metadata.title is None
    assert doc.metadata.output == "markdown"


def test_empty_document():
    """Test parsing an empty document."""
    doc = parse("")

    assert len(doc.blocks) == 0
    assert doc.metadata.output == "markdown"


def test_only_frontmatter():
    """Test parsing document with only frontmatter."""
    content = """---
title: Only Metadata
---"""

    doc = parse(content)

    assert doc.metadata.title == "Only Metadata"
    assert len(doc.blocks) == 0
