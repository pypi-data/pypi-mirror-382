#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CQaS CLI"""

import argparse
import os
import sys
import time
import traceback
import typing as t
from warnings import filterwarnings as filter_warnings

from cqas._colours import COLOURS_AVAILABLE, Fore, Style
from cqas._reporter import CQaSReporter
from cqas.analysers.full import FullAnalyser
from cqas.constructs.full import FileAnalysisResult, ProjectAnalysisResult
from cqas.constructs.security import SecurityIssue
from cqas.lang import LANGS, set_language


def create_argument_parser() -> argparse.ArgumentParser:
    """Create comprehensive argument parser with all CLI options"""

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Code Quality and Security Analyser (CQaS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s myfile.py                       # Analyse single file
  %(prog)s src/ -v                         # Analyse directory with progress
  %(prog)s . --json --output report.json   # JSON output to file
  %(prog)s project/ -p --colour            # Project analysis with colours
  %(prog)s app.py -s HIGH -v               # High severity issues only
  %(prog)s . -p -f --max-files 500         # Full analysis with recommendations
        """,
    )

    parser.add_argument("path", help="Python file or directory to analyse")

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--json", "-j", action="store_true", help="Output results in JSON format"
    )
    output_group.add_argument("--output", "-o", help="Output file to save results")
    output_group.add_argument(
        "--colour",
        "--color",
        "-c",
        action="store_true",
        default=True,
        help="Enable coloured output (default: enabled)",
    )
    output_group.add_argument(
        "--no-colour",
        "--no-color",
        "-C",
        dest="colour",
        action="store_false",
        help="Disable coloured output",
    )
    output_group.add_argument(
        "--top-n",
        "-n",
        type=int,
        default=10,
        help="Top N statistics",
    )

    # Analysis options
    analysis_group = parser.add_argument_group("Analysis Options")
    analysis_group.add_argument(
        "--max-files",
        "-m",
        type=int,
        default=1000,
        help="Maximum number of files to analyse (default: 1000)",
    )
    analysis_group.add_argument(
        "--min-severity",
        "-s",
        choices=("LOW", "MEDIUM", "HIGH", "CRITICAL"),
        default="LOW",
        help="Minimum security issue severity to include (default: LOW)",
    )

    # Feedback and reporting
    reporting_group = parser.add_argument_group("Reporting Options")
    reporting_group.add_argument(
        "--feedback",
        "-f",
        action="store_true",
        help="Generate actionable recommendations and feedback",
    )
    reporting_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with progress tracking",
    )
    reporting_group.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress messages"
    )

    analysis_group.add_argument(
        "--lang",
        "-l",
        choices=tuple(LANGS.keys()),
        default="en",
        help="Natural language of choice (default: en)",
    )

    return parser


def filter_security_issues_by_severity(
    project_result: ProjectAnalysisResult, min_severity: str
) -> None:
    """Filter security issues by minimum severity level"""

    severity_levels: t.Dict[str, int] = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }
    min_level: int = severity_levels.get(min_severity, 1)

    def should_include(issue: SecurityIssue) -> bool:
        issue_level = severity_levels.get(issue.severity.severity_name, 1)
        return issue_level >= min_level

    # Filter issues in each file result
    for file_result in project_result.file_results:
        file_result.security_issues = [
            issue for issue in file_result.security_issues if should_include(issue)
        ]

    # Recalculate project-level security statistics
    project_result.total_security_issues = sum(
        len(result.security_issues) for result in project_result.file_results
    )

    # Recalculate security severity distribution
    project_result.security_issues_by_severity = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }
    for result in project_result.file_results:
        for issue in result.security_issues:
            project_result.security_issues_by_severity[
                issue.severity.severity_name
            ] += 1


def main() -> int:  # pylint: disable=R0911,R0912
    """entry / main function"""

    parser: argparse.ArgumentParser = create_argument_parser()
    args: t.Any = parser.parse_args()

    if args.top_n < 2:
        print("Error: --top-n should be at least `2`", file=sys.stderr)
        return 1

    set_language(args.lang)

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        return 1

    try:
        start_time = time.time()

        # Configure analyser
        analyser: FullAnalyser = FullAnalyser(
            verbose=args.verbose and not args.quiet,
            colour=args.colour,
            progress=not args.quiet,
        )

        # Configure reporter
        reporter: CQaSReporter = CQaSReporter(
            colour=args.colour, feedback=args.feedback, top_n=args.top_n
        )

        # Perform analysis
        if os.path.isfile(args.path):
            if not args.path.endswith(".py"):
                print(f"Error: '{args.path}' is not a Python file.", file=sys.stderr)
                return 1

            # Single file analysis
            file_result: FileAnalysisResult = analyser.analyse_file(args.path)

            # Create project result
            project_result: ProjectAnalysisResult = ProjectAnalysisResult(
                project_path=os.path.dirname(args.path) or ".",
                analysis_start_time=start_time,
                analysis_duration=time.time() - start_time,
                total_files_found=1,
                files_analysed=1,
                files_with_errors=1 if file_result.syntax_errors else 0,
                file_results=[file_result],
            )

            # Calculate basic project statistics
            analyser.calculate_project_statistics(project_result)

        else:
            # Directory or project analysis
            project_result = analyser.analyse_project(args.path, args.max_files)

        # Filter security issues by severity
        if args.min_severity != "LOW":
            filter_security_issues_by_severity(project_result, args.min_severity)

        # Generate output
        if args.json:
            output: str = reporter.generate_json_report(project_result)
        else:
            output = reporter.generate_comprehensive_report(project_result)

        # Save or display output
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)

                elapsed_time: float = time.time() - start_time
                success_msg: str = (
                    f"Analysis complete. Report saved to '{args.output}' ({elapsed_time:.2f}s)"
                )

                if args.colour and COLOURS_AVAILABLE:
                    print(f"{Fore.GREEN}✓ {success_msg}{Style.RESET_ALL}")
                else:
                    print(f"✓ {success_msg}")

            except IOError as error:
                print(f"Error writing to '{args.output}': {error}", file=sys.stderr)
                return 1
        else:
            print(output)

        return 0

    except KeyboardInterrupt:
        if args.colour and COLOURS_AVAILABLE:
            print(
                f"\n{Fore.YELLOW}Analysis interrupted by user.{Style.RESET_ALL}",
                file=sys.stderr,
            )
        else:
            print("\nAnalysis interrupted by user.", file=sys.stderr)
        return 1

    except Exception as error:
        if args.colour and COLOURS_AVAILABLE:
            print(
                f"{Fore.RED}Error during analysis: {error}{Style.RESET_ALL}",
                file=sys.stderr,
            )
        else:
            print(f"Error during analysis: {error}", file=sys.stderr)

        if args.verbose:
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    assert main.__annotations__.get("return") is int, "main() should return an integer"

    filter_warnings("error", category=Warning)
    raise SystemExit(main())
