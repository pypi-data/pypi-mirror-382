"""Data models for Nhandu documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class BlockType(Enum):
    """Types of blocks in a document."""

    MARKDOWN = "markdown"
    CODE = "code"
    INLINE_CODE = "inline_code"


@dataclass
class Block:
    """Base class for document blocks."""

    block_type: BlockType
    content: str
    line_number: int = 0


@dataclass
class MarkdownBlock(Block):
    """A markdown text block."""

    def __init__(self, content: str, line_number: int = 0) -> None:
        super().__init__(BlockType.MARKDOWN, content, line_number)


@dataclass
class CodeBlock(Block):
    """A code block to be executed."""

    language: str = "python"
    hidden: bool = False
    output: str | None = None
    error: str | None = None
    figures: list[Path] = field(default_factory=list)

    def __init__(
        self,
        content: str,
        language: str = "python",
        hidden: bool = False,
        line_number: int = 0,
    ) -> None:
        super().__init__(BlockType.CODE, content, line_number)
        self.language = language
        self.hidden = hidden
        self.output = None
        self.error = None
        self.figures = []


@dataclass
class InlineCode:
    """Inline code within markdown text."""

    expression: str
    is_statement: bool  # True for <% %>, False for <%= %>
    result: str | None = None
    position: int = 0  # Position in the markdown text


@dataclass
class DocumentMetadata:
    """Document metadata from YAML frontmatter."""

    title: str | None = None
    output: str = "markdown"
    plot_dpi: int = 100
    number_format: str = ".4f"
    working_dir: str | None = None
    code_theme: str | None = None
    show_footer: bool = True
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentMetadata:
        """Create metadata from a dictionary."""
        return cls(
            title=data.get("title"),
            output=data.get("output", "markdown"),
            plot_dpi=data.get("plot_dpi", 100),
            number_format=data.get("number_format", ".4f"),
            working_dir=data.get("working_dir"),
            code_theme=data.get("code_theme"),
            show_footer=data.get("show_footer", True),
            raw=data,
        )


@dataclass
class Document:
    """A parsed Nhandu document."""

    blocks: list[Block]
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    source_path: Path | None = None


@dataclass
class ExecutedDocument(Document):
    """A document after code execution."""

    namespace: dict[str, Any] = field(default_factory=dict)
    execution_errors: list[str] = field(default_factory=list)
