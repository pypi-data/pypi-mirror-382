"""Parser for Python literate documents with Markdown in comments."""

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


class PythonLiterateParser:
    """Parser for Python files with literate comments."""

    def __init__(self) -> None:
        # Matches #' at start of line, captures rest of line
        self.markdown_line_pattern = re.compile(r"^#'\s?(.*?)$", re.MULTILINE)
        # Matches #| hide / #| block markers
        self.hide_marker_pattern = re.compile(r"^#\|\s*hide\s*$", re.MULTILINE)
        self.end_hide_marker_pattern = re.compile(r"^#\|\s*$", re.MULTILINE)
        # Inline code pattern (same as markdown parser)
        self.inline_code_pattern = re.compile(r"<%(?:=)?\s*(.*?)\s*%>")

    def parse(self, content: str, source_path: str | None = None) -> Document:
        """Parse a Python literate document from text content."""
        metadata = self._extract_metadata(content)
        blocks = self._parse_blocks(content)

        doc = Document(blocks=blocks, metadata=metadata)
        if source_path:
            from pathlib import Path

            doc.source_path = Path(source_path)

        return doc

    def _extract_metadata(self, content: str) -> DocumentMetadata:
        """Extract YAML frontmatter from initial comment block."""
        # Look for YAML frontmatter in comments at the start of file
        # Format:
        # #' ---
        # #' title: My Title
        # #' ---
        lines = content.split("\n")
        yaml_lines = []
        in_frontmatter = False
        frontmatter_ended = False

        for line in lines:
            if line.strip().startswith("#'"):
                # Extract the content after #'
                markdown_content = line[2:].lstrip()

                if markdown_content.strip() == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        frontmatter_ended = True
                        break

                if in_frontmatter:
                    yaml_lines.append(markdown_content)
            elif in_frontmatter and not line.strip().startswith("#"):
                # Hit non-comment line, stop looking
                break

        if yaml_lines and frontmatter_ended:
            yaml_content = "\n".join(yaml_lines)
            try:
                data = yaml.safe_load(yaml_content) or {}
                return DocumentMetadata.from_dict(data)
            except yaml.YAMLError:
                return DocumentMetadata()

        return DocumentMetadata()

    def _parse_blocks(self, content: str) -> list[Block]:
        """Parse content into blocks of markdown and code."""
        blocks: list[Block] = []
        lines = content.split("\n")

        current_markdown_lines: list[str] = []
        current_code_lines: list[str] = []
        in_hide_block = False
        hide_block_start_line = 0
        current_code_start_line = 0

        for line_num, line in enumerate(lines, start=1):
            # Check for hide markers
            if self.hide_marker_pattern.match(line):
                # Flush any accumulated markdown or code before starting hide block
                if current_markdown_lines:
                    markdown_content = "\n".join(current_markdown_lines)
                    if markdown_content.strip():
                        blocks.append(
                            MarkdownBlock(
                                markdown_content,
                                line_num - len(current_markdown_lines),
                            )
                        )
                    current_markdown_lines = []

                if current_code_lines:
                    code_content = "\n".join(current_code_lines)
                    if not self._is_empty_code(code_content):
                        blocks.append(
                            CodeBlock(
                                content=code_content,
                                language="python",
                                hidden=False,
                                line_number=current_code_start_line,
                            )
                        )
                    current_code_lines = []

                in_hide_block = True
                hide_block_start_line = line_num + 1
                continue

            if self.end_hide_marker_pattern.match(line) and in_hide_block:
                # End hide block - save hidden code (filter empty hidden blocks)
                if current_code_lines:
                    code_content = "\n".join(current_code_lines)
                    if not self._is_empty_code(code_content):
                        blocks.append(
                            CodeBlock(
                                content=code_content,
                                language="python",
                                hidden=True,
                                line_number=hide_block_start_line,
                            )
                        )
                    current_code_lines = []

                in_hide_block = False
                continue

            # Check if line is a markdown comment
            markdown_match = self.markdown_line_pattern.match(line)

            if markdown_match:
                # This is a markdown line
                # First, flush any accumulated code
                if current_code_lines:
                    code_content = "\n".join(current_code_lines)
                    if not self._is_empty_code(code_content):
                        blocks.append(
                            CodeBlock(
                                content=code_content,
                                language="python",
                                hidden=in_hide_block,
                                line_number=current_code_start_line,
                            )
                        )
                    current_code_lines = []

                # Add to markdown accumulator
                current_markdown_lines.append(markdown_match.group(1))
            else:
                # This is a code line (or blank/comment)
                # First, flush any accumulated markdown
                if current_markdown_lines:
                    markdown_content = "\n".join(current_markdown_lines)
                    if markdown_content.strip():
                        blocks.append(
                            MarkdownBlock(
                                markdown_content,
                                line_num - len(current_markdown_lines),
                            )
                        )
                    current_markdown_lines = []

                # Add to code accumulator (including blank lines and regular comments)
                if not current_code_lines:
                    current_code_start_line = line_num
                current_code_lines.append(line)

        # Flush any remaining content
        if current_markdown_lines:
            markdown_content = "\n".join(current_markdown_lines)
            if markdown_content.strip():
                blocks.append(
                    MarkdownBlock(
                        markdown_content,
                        len(lines) - len(current_markdown_lines) + 1,
                    )
                )

        if current_code_lines:
            code_content = "\n".join(current_code_lines)
            if not self._is_empty_code(code_content):
                blocks.append(
                    CodeBlock(
                        content=code_content,
                        language="python",
                        hidden=in_hide_block,
                        line_number=current_code_start_line,
                    )
                )

        return blocks

    def _is_empty_code(self, code: str) -> bool:
        """
        Check if Python code is empty (only whitespace, comments, or blank lines).

        @param code: The Python code content to check
        @return: True if code is effectively empty
        """
        lines = code.split("\n")
        return all(line.strip() == "" or line.strip().startswith("#") for line in lines)

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


def parse_python(content: str, source_path: str | None = None) -> Document:
    """Parse a Python literate document."""
    parser = PythonLiterateParser()
    return parser.parse(content, source_path)
