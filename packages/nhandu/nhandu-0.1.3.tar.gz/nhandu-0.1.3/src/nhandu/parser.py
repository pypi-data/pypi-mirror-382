"""Parser for Nhandu documents."""

from __future__ import annotations

import re

import yaml

from nhandu.models import (
    Block,
    CodeBlock,
    Document,
    DocumentMetadata,
    InlineCode,
    MarkdownBlock,
)


class NhanduParser:
    """Parser for Nhandu markdown documents."""

    def __init__(self) -> None:
        self.frontmatter_pattern = re.compile(
            r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL | re.MULTILINE
        )
        self.code_block_pattern = re.compile(
            r"^```(\w+)(\s+\{([^}]+)\})?\s*\n(.*?)^```",
            re.DOTALL | re.MULTILINE,
        )
        self.inline_code_pattern = re.compile(r"<%(?:=)?\s*(.*?)\s*%>")

    def parse(self, content: str, source_path: str | None = None) -> Document:
        """Parse a Nhandu document from text content."""
        metadata = self._extract_metadata(content)
        content_without_frontmatter = self._remove_frontmatter(content)
        blocks = self._parse_blocks(content_without_frontmatter)

        doc = Document(blocks=blocks, metadata=metadata)
        if source_path:
            from pathlib import Path

            doc.source_path = Path(source_path)

        return doc

    def _extract_metadata(self, content: str) -> DocumentMetadata:
        """Extract YAML frontmatter metadata."""
        match = self.frontmatter_pattern.match(content)
        if match:
            yaml_content = match.group(1)
            try:
                data = yaml.safe_load(yaml_content) or {}
                return DocumentMetadata.from_dict(data)
            except yaml.YAMLError:
                return DocumentMetadata()
        return DocumentMetadata()

    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        return self.frontmatter_pattern.sub("", content, count=1)

    def _parse_blocks(self, content: str) -> list[Block]:
        """Parse content into blocks."""
        blocks: list[Block] = []
        last_end = 0

        # If no content, return empty
        if not content.strip():
            return blocks

        # Find all code blocks
        for code_match in self.code_block_pattern.finditer(content):
            # Add markdown before this code block
            if code_match.start() > last_end:
                markdown_content = content[last_end : code_match.start()]
                if markdown_content.strip():
                    blocks.append(
                        MarkdownBlock(
                            markdown_content.rstrip(),
                            1 + content[:last_end].count("\n"),
                        )
                    )

            # Parse code block
            language = code_match.group(1)
            attributes = code_match.group(3)
            code_content = code_match.group(4)

            # Parse attributes (e.g., {hide=true})
            hidden = False
            if attributes:
                if "hide=true" in attributes or "hidden" in attributes:
                    hidden = True

            # Filter empty code blocks (whitespace only or only comments/blank lines)
            if self._is_empty_code(code_content, language):
                last_end = code_match.end()
                continue

            blocks.append(
                CodeBlock(
                    content=code_content,
                    language=language,
                    hidden=hidden,
                    line_number=1 + content[: code_match.start()].count("\n"),
                )
            )

            last_end = code_match.end()

        # Add any remaining markdown after the last code block
        if last_end < len(content):
            markdown_content = content[last_end:]
            if markdown_content.strip():
                blocks.append(
                    MarkdownBlock(
                        markdown_content.rstrip(),
                        1 + content[:last_end].count("\n"),
                    )
                )

        return blocks

    def _is_empty_code(self, code: str, language: str) -> bool:
        """
        Check if code block is empty (only whitespace, comments, or blank lines).

        For Python code, checks for comments and blank lines.
        For other languages, uses simple whitespace check.

        @param code: The code content to check
        @param language: The programming language
        @return: True if code is effectively empty
        """
        if language.lower() == "python":
            # Check if all lines are blank or comments
            lines = code.split("\n")
            return all(
                line.strip() == "" or line.strip().startswith("#") for line in lines
            )
        else:
            # For other languages, simple whitespace check
            return not code.strip()

    def extract_inline_code(self, text: str) -> list[InlineCode]:
        """Extract inline code from markdown text."""
        inline_codes = []
        for match in self.inline_code_pattern.finditer(text):
            full_match = match.group(0)
            code = match.group(1)
            is_statement = not full_match.startswith("<%=")
            inline_codes.append(
                InlineCode(
                    expression=code,
                    is_statement=is_statement,
                    position=match.start(),
                )
            )
        return inline_codes


def parse(content: str, source_path: str | None = None) -> Document:
    """Parse a Nhandu document."""
    parser = NhanduParser()
    return parser.parse(content, source_path)
