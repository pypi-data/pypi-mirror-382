"""Code execution engine for Nhandu."""

from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
from typing import Any

from nhandu.models import (
    CodeBlock,
    Document,
    ExecutedDocument,
    MarkdownBlock,
)


class CodeExecutor:
    """Executes code blocks and captures output."""

    def __init__(
        self, working_dir: str | None = None, timeout: float | None = None
    ) -> None:
        self.working_dir = working_dir
        self.timeout = timeout
        self.namespace: dict[str, Any] = {}
        self.figure_counter = 0

    def execute_document(self, doc: Document) -> ExecutedDocument:
        """Execute all code blocks in a document."""
        # Set working directory if specified
        original_dir = os.getcwd()
        if doc.metadata.working_dir:
            os.chdir(doc.metadata.working_dir)
        elif self.working_dir:
            os.chdir(self.working_dir)

        # Create output directory for figures relative to source document
        if doc.source_path:
            output_dir = doc.source_path.parent / "figures"
        else:
            output_dir = Path("figures")
        output_dir.mkdir(exist_ok=True)

        # Reset namespace for fresh execution
        self.namespace = self._create_initial_namespace()
        self.figure_counter = 0

        executed_doc = ExecutedDocument(
            blocks=[],
            metadata=doc.metadata,
            source_path=doc.source_path,
            namespace=self.namespace,
        )

        try:
            for block in doc.blocks:
                if isinstance(block, CodeBlock):
                    self._execute_code_block(block, output_dir)
                    executed_doc.blocks.append(block)
                elif isinstance(block, MarkdownBlock):
                    executed_block = self._process_markdown_block(block)
                    executed_doc.blocks.append(executed_block)
                else:
                    executed_doc.blocks.append(block)

        finally:
            # Restore original directory
            os.chdir(original_dir)

        return executed_doc

    def _create_initial_namespace(self) -> dict[str, Any]:
        """Create initial namespace with common imports."""
        namespace = {
            "__name__": "__main__",
            "__doc__": None,
            "__package__": None,
        }
        return namespace

    def _execute_code_block(self, block: CodeBlock, output_dir: Path) -> None:
        """Execute a single code block."""
        if block.language.lower() != "python":
            return

        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        # Import matplotlib if available for plot capture
        plt: Any | None = None
        try:
            import matplotlib

            matplotlib.use("Agg")  # Non-interactive backend
            import matplotlib.pyplot as plt
        except ImportError:
            pass

        # Clear any existing plots
        if plt:
            plt.close("all")

        try:
            with contextlib.redirect_stdout(stdout_buffer):
                with contextlib.redirect_stderr(stderr_buffer):
                    # Try to handle mixed statements and expressions
                    lines = block.content.strip().split("\n")

                    if len(lines) == 1:
                        # Single line - try as expression first
                        try:
                            result = eval(lines[0], self.namespace)
                            if result is not None:
                                print(repr(result))
                        except Exception:
                            # Fall back to statement execution
                            exec(lines[0], self.namespace)
                    else:
                        # Multiple lines - check if last line is an expression
                        if lines:
                            last_line = lines[-1].strip()
                            last_is_expression = False

                            # Check if we're inside a control structure
                            in_control_structure = any(
                                line.rstrip().endswith(":") for line in lines
                            )

                            # Test if last line is an expression
                            # (only if not in control structure)
                            if last_line and not in_control_structure:
                                try:
                                    compile(last_line, "<string>", "eval")
                                    last_is_expression = True
                                except SyntaxError:
                                    last_is_expression = False

                            if last_is_expression:
                                # Execute all but last line, then evaluate last line
                                statements = "\n".join(lines[:-1])
                                if statements.strip():
                                    exec(statements, self.namespace)

                                # Evaluate last line as expression
                                try:
                                    result = eval(last_line, self.namespace)
                                    if result is not None:
                                        print(repr(result))
                                except Exception:
                                    # Fallback to statement execution
                                    exec(last_line, self.namespace)
                            else:
                                # Execute entire block as statements
                                full_code = block.content.strip()
                                exec(full_code, self.namespace)

            # Capture output
            output = stdout_buffer.getvalue()
            if output:
                block.output = output.rstrip()

            # Capture any matplotlib figures
            if plt:
                figures = []
                for fig_num in plt.get_fignums():
                    fig = plt.figure(fig_num)
                    figure_path = output_dir / f"figure_{self.figure_counter}.png"
                    fig.savefig(
                        figure_path,
                        dpi=100,
                        bbox_inches="tight",
                    )
                    figures.append(figure_path)
                    self.figure_counter += 1
                    plt.close(fig)
                block.figures = figures

        except Exception as e:
            # Format error message
            error_msg = f"{type(e).__name__}: {e!s}"
            if block.line_number:
                error_msg += f"\n  at line {block.line_number} in code block"
            block.error = error_msg

    def _process_markdown_block(self, block: MarkdownBlock) -> MarkdownBlock:
        """Process inline code in markdown blocks."""
        from nhandu.parser import NhanduParser

        parser = NhanduParser()
        text = block.content
        inline_codes = parser.extract_inline_code(text)

        if not inline_codes:
            return block

        # Process inline codes using regex replacement
        for inline in inline_codes:
            try:
                if inline.is_statement:
                    # Execute statement (no output)
                    exec(inline.expression, self.namespace)
                    replacement = ""
                else:
                    # Evaluate expression and format result
                    result = eval(inline.expression, self.namespace)
                    replacement = str(result) if result is not None else ""

                # Create pattern for replacement - escape regex special chars
                import re

                escaped_expr = re.escape(inline.expression)
                if inline.is_statement:
                    pattern = f"<%\\s*{escaped_expr}\\s*%>"
                else:
                    pattern = f"<%=\\s*{escaped_expr}\\s*%>"

                text = re.sub(pattern, replacement, text, count=1)

            except Exception:
                # Keep original on error
                pass

        return MarkdownBlock(text, block.line_number)


def execute(
    doc: Document,
    working_dir: str | None = None,
    timeout: float | None = None,
) -> ExecutedDocument:
    """Execute code blocks in a document."""
    executor = CodeExecutor(working_dir, timeout)
    return executor.execute_document(doc)
