"""Command-line interface for Nhandu."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nhandu import __version__, execute, parse, render
from nhandu.models import Document
from nhandu.parser_py import parse_python


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_argument_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"nhandu {__version__}")
        return 0

    try:
        process_document(args)
        return 0
    except Exception as e:
        if args.verbose:
            import traceback

            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="nhandu",
        description="A literate programming tool for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input file to process (.md markdown or .py literate Python)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: input with appropriate extension)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "md", "html"],
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--config",
        help="Configuration file (YAML)",
    )

    parser.add_argument(
        "--working-dir",
        help="Working directory for code execution",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        help="Execution timeout in seconds",
    )

    parser.add_argument(
        "--code-theme",
        help="Syntax highlighting theme for HTML output (e.g., github-dark, monokai)",
    )

    parser.add_argument(
        "--no-footer",
        action="store_true",
        help="Disable 'Made with Nhandu' footer in HTML output",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (not implemented yet)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    return parser


def process_document(args: argparse.Namespace) -> None:
    """Process a Nhandu document."""
    if not args.input:
        raise ValueError("No input file specified")

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read input file
    content = input_path.read_text(encoding="utf-8")

    # Detect format and parse document
    if args.verbose:
        print(f"Parsing {input_path}...")

    # Auto-detect Python literate format by file extension or presence of #' markers
    if input_path.suffix == ".py" or "#'" in content:
        doc = parse_python(content, str(input_path))
    else:
        doc = parse(content, str(input_path))

    # Load config if specified
    if args.config:
        load_config(doc, args.config)

    # Override with CLI arguments
    if args.format:
        doc.metadata.output = args.format.replace("md", "markdown")
    if args.code_theme:
        doc.metadata.code_theme = args.code_theme
    if args.no_footer:
        doc.metadata.show_footer = False

    # Execute code blocks
    if args.verbose:
        print("Executing code blocks...")
    executed_doc = execute(
        doc,
        working_dir=args.working_dir or doc.metadata.working_dir,
        timeout=args.timeout,
    )

    # Determine output format
    output_format = doc.metadata.output

    # Render output
    if args.verbose:
        print(f"Rendering to {output_format}...")
    output_content = render(executed_doc, output_format)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Generate output filename: source.out.ext or source.html
        if output_format == "html":
            output_path = input_path.with_suffix(".html")
        else:
            # Insert .out before extension: test.md -> test.out.md
            output_path = input_path.with_suffix(f".out{input_path.suffix}")

    # Write output
    output_path.write_text(output_content, encoding="utf-8")

    if args.verbose:
        print(f"Output written to {output_path}")

    # Print any execution errors
    if executed_doc.execution_errors:
        print("\nExecution errors encountered:", file=sys.stderr)
        for error in executed_doc.execution_errors:
            print(f"  - {error}", file=sys.stderr)


def load_config(doc: Document, config_path: str) -> None:
    """Load configuration from a YAML file."""
    import yaml

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    # Update document metadata with config
    if config_data:
        for key, value in config_data.items():
            if hasattr(doc.metadata, key):
                setattr(doc.metadata, key, value)
            doc.metadata.raw[key] = value


if __name__ == "__main__":
    sys.exit(main())
