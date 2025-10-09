"""
Command-line interface (CLI) for the `bisslog_schema` package.

This module provides a CLI to interact with the `bisslog_schema` package, allowing users
to analyze metadata files in various formats (e.g., YAML, JSON) and perform other related tasks.

Commands
--------
- `analyze_metadata`: Analyze a metadata file and generate a report.
"""
import argparse
import sys

from .commands.analyze_metadata_file.analyze_metadata import analyze_command


def main():
    """Entry point for the CLI.

    Parses command-line arguments and executes the corresponding command.

    Commands
    --------
    analyze_metadata : str
        Command to analyze a metadata file with the following parameters:
        - path: Path to the metadata file (required)
        - format_file: File format (yaml|json|xml, default: yaml)
        - encoding: File encoding (default: utf-8)
        - min_warnings: Minimum warning percentage allowed (optional)

    Examples
    --------
    $ bisslog_schema analyze_metadata /path/to/file.yaml --min-warnings 0.5

    Raises
    ------
    SystemExit
        If an invalid command is provided (exit code 1) or execution fails (exit code 2).
    """
    parser = argparse.ArgumentParser(prog="bisslog_schema")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze_metadata", help="Analyze metadata file")
    analyze_parser.add_argument("path", help="Path to metadata file")
    analyze_parser.add_argument(
        "--format-file", help="Format to read the file (default: yaml)",
        default="yaml", choices=['yaml', 'json', 'xml'])
    analyze_parser.add_argument(
        "--encoding", help="Encoding to read the file (default: utf-8)",
        default="utf-8",
        type=lambda x: x if x.lower() in ['utf-8', 'ascii', 'latin-1']
                         else argparse.ArgumentTypeError("Invalid encoding"))
    analyze_parser.add_argument(
        "--min-warnings", help="Minimum percentage of warnings allowed",
        type=float, default=None)

    args = parser.parse_args()

    try:
        if args.command == "analyze_metadata":
            analyze_command(args.path,
                           format_file=args.format_file,
                           encoding=args.encoding,
                           min_warnings=args.min_warnings)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(2)
