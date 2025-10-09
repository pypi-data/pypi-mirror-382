"""Renderer for Nhandu documents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound

from nhandu.models import (
    CodeBlock,
    ExecutedDocument,
    MarkdownBlock,
)


class Renderer(ABC):
    """Abstract base class for renderers."""

    @abstractmethod
    def render(self, doc: ExecutedDocument) -> str:
        """Render an executed document."""
        pass


class MarkdownRenderer(Renderer):
    """Renders to Markdown format with executed outputs."""

    def render(self, doc: ExecutedDocument) -> str:
        """Render document to Markdown."""
        output_parts = []

        # Add frontmatter if it exists
        if doc.metadata.raw:
            import yaml

            output_parts.append("---")
            yaml_output = yaml.dump(doc.metadata.raw, default_flow_style=False)
            if isinstance(yaml_output, str):
                output_parts.append(yaml_output.strip())
            output_parts.append("---")
            output_parts.append("")

        # Render blocks
        for block in doc.blocks:
            if isinstance(block, MarkdownBlock):
                # Defensive filter: skip empty markdown blocks
                if block.content.strip():
                    output_parts.append(block.content)
            elif isinstance(block, CodeBlock):
                # Defensive filter: render if has content OR output/error/figures
                if (
                    block.content.strip()
                    or block.output
                    or block.error
                    or block.figures
                ):
                    output_parts.append(self._render_code_block(block))

        return "\n".join(output_parts)

    def _render_code_block(self, block: CodeBlock) -> str:
        """Render a code block with its output."""
        parts = []

        # Don't render hidden blocks
        if block.hidden:
            return ""

        # Add code block
        attributes = ""
        if block.hidden:
            attributes = " {hide=true}"
        parts.append(f"```{block.language}{attributes}")
        parts.append(block.content.rstrip())
        parts.append("```")

        # Add output if present
        if block.output or block.error or block.figures:
            parts.append("")
            parts.append("Output:")
            parts.append("```")

            if block.output:
                parts.append(block.output)

            if block.error:
                parts.append(f"Error: {block.error}")

            parts.append("```")

            # Add figures
            for figure in block.figures:
                parts.append("")
                parts.append(f"![Figure]({figure})")

        parts.append("")
        return "\n".join(parts)


class HTMLRenderer(Renderer):
    """Renders to HTML format."""

    # Default theme for syntax highlighting
    DEFAULT_THEME = "github-dark"

    def __init__(self) -> None:
        """Initialize the HTML renderer."""
        self._current_theme: str | None = None
        self._formatter: HtmlFormatter | None = None

    def render(self, doc: ExecutedDocument) -> str:
        """Render document to HTML."""
        # Resolve theme from document metadata or use default
        theme = self._resolve_theme(doc.metadata.code_theme)
        self._setup_formatter(theme)

        # Determine page title: metadata > filename > default
        title = self._get_document_title(doc)

        # Basic HTML rendering for now
        # Will be enhanced with templates later
        parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            f"<title>{title}</title>",
            "<style>",
            self._get_default_css(),
            "</style>",
            "</head>",
            "<body>",
        ]

        # Render blocks
        for block in doc.blocks:
            if isinstance(block, MarkdownBlock):
                # Defensive filter: skip empty markdown blocks
                if block.content.strip():
                    # Markdown to HTML conversion with GFM support
                    import mistune

                    # Use create_markdown with plugins for GitHub Flavored Markdown
                    # Includes: tables, strikethrough, and footnotes
                    markdown_parser = mistune.create_markdown(
                        plugins=["table", "strikethrough", "footnotes"]
                    )
                    html_output = markdown_parser(block.content)
                    if isinstance(html_output, str):
                        parts.append(html_output)
            elif isinstance(block, CodeBlock) and not block.hidden:
                # Defensive filter: render if has content OR output/error/figures
                if (
                    block.content.strip()
                    or block.output
                    or block.error
                    or block.figures
                ):
                    parts.append(self._render_code_block_html(block))

        # Add footer if enabled
        if doc.metadata.show_footer:
            parts.append(self._render_footer())

        parts.extend(["</body>", "</html>"])
        return "\n".join(parts)

    def _get_document_title(self, doc: ExecutedDocument) -> str:
        """
        Get document title with fallback logic.

        Priority:
        1. YAML frontmatter title
        2. Source filename (without extension)
        3. Default "Nhandu Report"

        @param doc: The executed document
        @return: Document title string
        """
        # Use metadata title if available
        if doc.metadata.title:
            return doc.metadata.title

        # Fall back to filename if source path exists
        if doc.source_path:
            # Get filename without extension
            return doc.source_path.stem

        # Final fallback
        return "Nhandu Report"

    def _resolve_theme(self, requested_theme: str | None) -> str:
        """Resolve theme name with validation."""
        theme = requested_theme or self.DEFAULT_THEME

        # Validate theme
        valid_styles = list(get_all_styles())
        if theme not in valid_styles:
            # Try to provide helpful error message
            similar = [
                s for s in valid_styles if theme.lower() in s or s in theme.lower()
            ]
            if similar:
                suggestion = f" Did you mean: {', '.join(similar[:3])}?"
            else:
                top_themes = ", ".join(sorted(valid_styles)[:10])
                suggestion = f" Available themes: {top_themes}..."

            raise ValueError(f"Unknown code theme '{theme}'.{suggestion}")

        return theme

    def _setup_formatter(self, theme: str) -> None:
        """Setup Pygments formatter for the given theme."""
        if self._current_theme != theme:
            self._formatter = HtmlFormatter(
                style=theme,
                cssclass="highlight",
                noclasses=False,
            )
            self._current_theme = theme

    def _get_pygments_css(self) -> str:
        """Generate Pygments CSS for the current theme."""
        if self._formatter is None:
            # Fallback: create formatter with default theme
            self._formatter = HtmlFormatter(
                style=self.DEFAULT_THEME,
                cssclass="highlight",
                noclasses=False,
            )
        result: str = self._formatter.get_style_defs(".highlight")
        return result

    def _get_default_css(self) -> str:
        """Get default CSS styles including Pygments theme."""
        # Generate Pygments CSS for syntax highlighting
        pygments_css = self._get_pygments_css()

        return f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        pre {{
            background: #f5f5f5;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
        }}
        code {{
            background: #f5f5f5;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }}
        .code-block {{
            margin: 1.5rem 0;
        }}
        .code-input {{
            padding: 1rem;
            border-radius: 4px 4px 0 0;
            margin: 0;
        }}
        .code-input pre {{
            margin: 0;
            padding: 0;
            background: transparent;
        }}
        .code-output {{
            background: #f8f8f8;
            border: 1px solid #e1e4e8;
            border-top: none;
            padding: 1rem;
            border-radius: 0 0 4px 4px;
            margin: 0;
        }}
        .error {{
            color: #d73a49;
            background: #ffeef0;
            padding: 1rem;
            border-radius: 4px;
            border: 1px solid #ffdce0;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}

        /* Footer */
        .nhandu-footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e1e4e8;
            font-size: 0.875rem;
            color: #6c757d;
        }}
        .nhandu-footer a {{
            color: #0969da;
            text-decoration: none;
        }}
        .nhandu-footer a:hover {{
            text-decoration: underline;
        }}

        /* Pygments syntax highlighting */
        {pygments_css}
        """

    def _render_code_block_html(self, block: CodeBlock) -> str:
        """Render a code block as HTML with Pygments syntax highlighting."""
        parts = ['<div class="code-block">']

        # Code input with syntax highlighting
        highlighted_code = self._highlight_code(block.content.rstrip(), block.language)
        parts.append(f'<div class="code-input">{highlighted_code}</div>')

        # Output
        if block.output or block.error or block.figures:
            if block.error:
                parts.append(
                    f'<pre class="error">{self._escape_html(block.error)}</pre>'
                )
            elif block.output:
                parts.append(
                    f'<pre class="code-output">{self._escape_html(block.output)}</pre>'
                )

            # Figures - embed as base64 data URIs
            for figure in block.figures:
                try:
                    import base64
                    from pathlib import Path

                    figure_path = Path(figure)
                    if figure_path.exists():
                        with open(figure_path, "rb") as f:
                            image_data = f.read()

                        # Determine MIME type based on file extension
                        ext = figure_path.suffix.lower()
                        if ext == ".png":
                            mime_type = "image/png"
                        elif ext in [".jpg", ".jpeg"]:
                            mime_type = "image/jpeg"
                        elif ext == ".svg":
                            mime_type = "image/svg+xml"
                        else:
                            mime_type = "image/png"  # Default

                        # Encode as base64
                        encoded_image = base64.b64encode(image_data).decode("utf-8")
                        data_uri = f"data:{mime_type};base64,{encoded_image}"
                        parts.append(f'<img src="{data_uri}" alt="Figure">')
                    else:
                        # Fallback to file reference if file doesn't exist
                        parts.append(f'<img src="{figure}" alt="Figure">')
                except Exception:
                    # Fallback to file reference on any error
                    parts.append(f'<img src="{figure}" alt="Figure">')

        parts.append("</div>")
        return "\n".join(parts)

    def _highlight_code(self, code: str, language: str) -> str:
        """Highlight code using Pygments."""
        if self._formatter is None:
            # Fallback if formatter not setup (shouldn't happen)
            self._setup_formatter(self.DEFAULT_THEME)

        try:
            lexer = get_lexer_by_name(language or "python", stripall=False)
        except ClassNotFound:
            # Fallback to plain text for unknown languages
            lexer = TextLexer()

        # Ensure formatter is not None for mypy
        formatter = self._formatter if self._formatter is not None else HtmlFormatter()
        result: str = highlight(code, lexer, formatter)
        return result

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _render_footer(self) -> str:
        """
        Render the Nhandu attribution footer.

        @return: HTML footer element with link to Nhandu
        """
        return (
            '<footer class="nhandu-footer">\n'
            'Made with <a href="https://pypi.org/project/nhandu" '
            'target="_blank" rel="noopener noreferrer">Nhandu</a>\n'
            "</footer>"
        )


def render(doc: ExecutedDocument, format: str | None = None) -> str:
    """Render an executed document."""
    output_format = format or doc.metadata.output

    if output_format == "html":
        renderer: Renderer = HTMLRenderer()
    else:
        # Default to markdown
        renderer = MarkdownRenderer()

    return renderer.render(doc)
