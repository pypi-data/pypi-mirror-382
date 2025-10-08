#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full code analyser"""

import math
import os
import sys
import time
import typing as t

from cqas._colours import COLOURS_AVAILABLE, Fore, Style
from cqas.analysers.complexity import ComplexityAnalyser
from cqas.analysers.dead_code import DeadCodeAnalyser
from cqas.analysers.duplication import DuplicationDetector
from cqas.analysers.halstead import HalsteadAnalyser
from cqas.analysers.imports import ImportAnalyser
from cqas.analysers.pep8 import PEP8StyleChecker
from cqas.analysers.readability import ReadabilityAnalyser
from cqas.analysers.security import SecurityAnalyser
from cqas.constructs.duplication import DuplicationResult
from cqas.constructs.full import ExtendedQualityMetrics, FileAnalysisResult, ProjectAnalysisResult
from cqas.constructs.halstead import HalsteadMetrics
from cqas.lang import s

__all__: t.Tuple[str, ...] = ("FullAnalyser",)


class FullAnalyser:
    """Full Code Quality and Security Analyser"""

    def __init__(
        self,
        verbose: bool = False,
        colour: bool = True,
        progress: bool = True,
    ):
        self.verbose: bool = verbose
        self.colour: bool = colour and COLOURS_AVAILABLE
        self.progress: bool = progress
        self.duplication_detector: DuplicationDetector = DuplicationDetector()
        self.pep8_checker: PEP8StyleChecker = PEP8StyleChecker()

    def _log_info(self, message: str) -> None:
        """Log info message with optional colour"""
        if self.verbose:
            if self.colour:
                print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")
            else:
                print(f"[INFO] {message}")

    def _log_warning(self, message: str) -> None:
        """Log warning message with optional colour"""
        if self.verbose:
            if self.colour:
                print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")
            else:
                print(f"[WARNING] {message}")

    def _log_error(self, message: str) -> None:
        """Log error message with optional colour"""
        if self.colour:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}", file=sys.stderr)
        else:
            print(f"[ERROR] {message}", file=sys.stderr)

    def _log_progress(self, current: int, total: int, file_path: str) -> None:
        """Log progress message"""
        if self.progress:
            percentage = (current / total) * 100 if total > 0 else 0
            if self.colour:
                print(
                    f"{Fore.GREEN}{s('analysing')} ({current}/{total}){Style.RESET_ALL} \
[{percentage:.1f}%]: {file_path}"
                )
            else:
                print(
                    f"{s('analysing')} ({current}/{total}) [{percentage:.1f}%]: {file_path}"
                )

    def analyse_file(self, file_path: str) -> FileAnalysisResult:
        """Analyse a single Python file with comprehensive metrics"""

        start_time: float = time.time()
        result: FileAnalysisResult = FileAnalysisResult(file_path=file_path)
        self._log_info(s("starting_analysis_of", file_path))
        try:
            content: t.Optional[str] = self._read_file_content(file_path, result)

            if content is None or not content.strip():
                self._log_warning(s("skipping_empty_file", file_path))
                return result

            self._calculate_basic_line_metrics(content, result)
            analysers = self._initialize_analysers(file_path, content, result)
            if not analysers:
                return result

            self._run_ast_analysis(analysers, file_path, result)
            self._extract_metrics(analysers, result, content)
            self._calculate_derived_metrics(result)
        except Exception as error:
            self._log_error(f"Unexpected error analysing {file_path}: {error}")
            result.syntax_errors.append(f"Unexpected error: {error}")

        result.analysis_time = time.time() - start_time
        self._log_info(
            s("completed_analysis_of_file", file_path, f"{result.analysis_time:.2f}s")
        )
        return result

    def _read_file_content(
        self, file_path: str, result: FileAnalysisResult
    ) -> t.Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as error:
                self._log_error(f"Failed to read {file_path}: {error}")
                result.syntax_errors.append(f"File read error: {error}")
                return None
        except Exception as error:
            self._log_error(f"Failed to read {file_path}: {error}")
            result.syntax_errors.append(f"File read error: {error}")
            return None

    def _calculate_basic_line_metrics(
        self, content: str, result: FileAnalysisResult
    ) -> None:
        lines: t.List[str] = content.splitlines()
        metrics = result.quality_metrics
        metrics.lines_of_code = len(lines)
        metrics.logical_lines_of_code = len(
            [
                line
                for line in lines
                if line.strip() and not line.strip().startswith("#")
            ]
        )
        metrics.comment_lines = len(
            [line for line in lines if line.strip().startswith("#")]
        )
        metrics.blank_lines = len([line for line in lines if not line.strip()])
        line_lengths = [len(line) for line in lines]
        metrics.avg_line_length = sum(line_lengths) / max(len(lines), 1)
        metrics.max_line_length = max(line_lengths) if line_lengths else 0
        metrics.long_line_count = len([l for l in line_lengths if l > 120])

    def _initialize_analysers(
        self, file_path: str, content: str, result: FileAnalysisResult
    ) -> t.Dict[str, t.Any]:
        analysers: t.Dict[str, t.Any] = {}
        try:
            analysers["complexity"] = ComplexityAnalyser(file_path, content)
            analysers["halstead"] = HalsteadAnalyser(file_path, content)
            analysers["dead_code"] = DeadCodeAnalyser(file_path, content)
            analysers["security"] = SecurityAnalyser(file_path, content)
            analysers["readability"] = ReadabilityAnalyser(file_path, content)
            analysers["imports"] = ImportAnalyser(file_path, content)
        except SyntaxError as error:
            self._log_error(f"Syntax error in {file_path}: {error}")
            result.syntax_errors.append(f"Syntax error: {error}")
            return {}
        except Exception as error:
            self._log_error(f"Analysis setup error in {file_path}: {error}")
            result.syntax_errors.append(f"Setup error: {error}")
            return {}
        return analysers

    def _run_ast_analysis(
        self, analysers: t.Dict[str, t.Any], file_path: str, result: FileAnalysisResult
    ) -> None:
        for analyser_name, analyser in analysers.items():
            try:
                if analyser.tree:
                    analyser.visit(analyser.tree)
                    self._log_info(
                        s("completed_analyser_of_file", analyser_name, file_path)
                    )
            except Exception as error:
                self._log_error(
                    f"{analyser_name} analysis failed for {file_path}: {error}"
                )
                result.syntax_errors.append(f"{analyser_name} error: {error}")

    def _extract_metrics(
        self,
        analysers: t.Dict[str, t.Any],
        result: FileAnalysisResult,
        content: str,
    ) -> None:
        try:
            complexity_metrics = analysers["complexity"].get_metrics()
            qm = result.quality_metrics
            qm.cyclomatic_complexity = complexity_metrics.cyclomatic_complexity
            qm.cognitive_complexity = complexity_metrics.cognitive_complexity
            qm.function_count = complexity_metrics.function_count
            qm.class_count = complexity_metrics.class_count
            qm.avg_function_complexity = complexity_metrics.avg_function_complexity
            qm.max_function_complexity = complexity_metrics.max_function_complexity
            qm.max_nesting_depth = complexity_metrics.max_nesting_depth
            qm.complexity_hotspots = complexity_metrics.complexity_hotspots
            if complexity_metrics.function_complexities:
                avg_nesting = sum(
                    1 for _ in complexity_metrics.function_complexities
                ) / len(complexity_metrics.function_complexities)
                qm.avg_nesting_depth = avg_nesting
        except Exception as error:
            self._log_error(f"Complexity metrics extraction failed: {error}")

        try:
            result.halstead_metrics = analysers["halstead"].get_metrics()
            qm = result.quality_metrics
            hal = result.halstead_metrics
            qm.halstead_volume = hal.volume
            qm.halstead_difficulty = hal.difficulty
            qm.halstead_effort = hal.effort
            qm.halstead_bugs = hal.bugs_estimate
            qm.halstead_time = hal.time_to_implement
        except Exception as error:
            self._log_error(f"Halstead metrics extraction failed: {error}")

        try:
            result.security_issues = analysers["security"].issues
        except Exception as error:
            self._log_error(f"Security analysis extraction failed: {error}")

        try:
            result.dead_code_info = analysers["dead_code"].find_dead_code()
        except Exception as error:
            self._log_error(f"Dead code analysis extraction failed: {error}")

        try:
            result.readability_metrics = analysers["readability"].get_metrics()
            qm = result.quality_metrics
            readability = result.readability_metrics
            qm.readability_score = readability.score
            qm.docstring_coverage = readability.docstring_coverage
            qm.comment_ratio = readability.comment_ratio
            qm.type_hint_coverage = readability.type_hint_coverage
        except Exception as error:
            self._log_error(f"Readability analysis extraction failed: {error}")

        try:
            result.import_analysis = analysers["imports"].analyse()
            qm = result.quality_metrics
            imports = result.import_analysis
            qm.total_imports = imports.total_imports
            qm.unique_modules = imports.unique_modules
            qm.stdlib_imports = imports.stdlib_imports
            qm.third_party_imports = imports.third_party_imports
            qm.local_imports = imports.local_imports
            qm.circular_imports = len(imports.circular_dependencies)
        except Exception as error:
            self._log_error(f"Import analysis extraction failed: {error}")

        try:
            result.pep8_result = self.pep8_checker.check(content)
            qm = result.quality_metrics
            qm.pep8_compliance = result.pep8_result.compliance_score
            qm.style_issues = len(result.pep8_result.issues)
        except Exception as error:
            self._log_error(f"PEP8 checking failed: {error}")

        try:
            result.duplication_percentage = self.duplication_detector.check(content)
            result.quality_metrics.code_duplication = result.duplication_percentage
        except Exception as error:
            self._log_error(f"Duplication analysis failed: {error}")

    def _calculate_derived_metrics(self, result: FileAnalysisResult) -> None:
        """Calculate derived quality metrics"""
        try:
            metrics: ExtendedQualityMetrics = result.quality_metrics

            # Maintainability Index (enhanced IEEE calculation)
            mi: float = self._calculate_maintainability_index(
                result.halstead_metrics,
                metrics.cyclomatic_complexity,
                metrics.logical_lines_of_code,
                metrics.comment_ratio,
                metrics.avg_nesting_depth,
                result.duplication_percentage,
            )
            metrics.maintainability_index = mi

            # Technical debt ratio and time estimation
            debt_ratio, debt_minutes = self._calculate_technical_debt(
                metrics.cyclomatic_complexity,
                result.duplication_percentage,
                len(result.security_issues),
                metrics.pep8_compliance,
                metrics.lines_of_code,
            )
            metrics.technical_debt_ratio = debt_ratio
            metrics.technical_debt_minutes = debt_minutes

            # Bug prediction
            metrics.estimated_bugs = (
                result.halstead_metrics.bugs_estimate
                + (metrics.cyclomatic_complexity / 50.0)
                + (len(result.security_issues) * 0.1)
            )

            if metrics.lines_of_code > 0:
                metrics.bug_density = (
                    metrics.estimated_bugs / metrics.lines_of_code
                ) * 1000

            # Overall quality index
            metrics.code_quality_index = self._calculate_quality_index(result)

        except Exception as error:
            self._log_error(f"Error calculating derived metrics: {error}")

    def _calculate_maintainability_index(
        self,
        halstead: HalsteadMetrics,
        complexity: int,
        source_lines: int,
        comment_ratio: float,
        avg_nesting: float,
        duplication: float,
    ) -> float:
        """Calculate enhanced IEEE maintainability index"""
        try:
            if source_lines <= 0:
                return 100.0

            # Enhanced IEEE formula with additional factors
            volume_term: float = 5.2 * math.log(max(halstead.volume, 1))
            complexity_term: float = 0.23 * complexity
            loc_term: float = 16.2 * math.log(max(source_lines, 1))
            comment_term: float = 50 * math.sin(math.sqrt(2.4 * (comment_ratio / 100)))

            # Additional penalty factors
            nesting_penalty: float = avg_nesting * 2.0
            duplication_penalty: float = duplication * 0.3

            raw_mi = (
                171
                - volume_term
                - complexity_term
                - loc_term
                + comment_term
                - nesting_penalty
                - duplication_penalty
            )

            # Normalise to 0-100 scale
            normalised_mi: float = max(0.0, min(100.0, (raw_mi / 171) * 100))
            return round(normalised_mi, 2)
        except (ValueError, OverflowError, ZeroDivisionError):
            return 50.0

    def _calculate_technical_debt(
        self,
        complexity: int,
        duplication: float,
        security_issues: int,
        pep8_score: float,
        lines_of_code: int,
    ) -> t.Tuple[float, float]:
        """Calculate technical debt ratio and estimated time to fix"""
        try:
            # Debt factors
            complexity_debt: float = min(complexity / 50.0, 1.0)
            duplication_debt: float = min(duplication / 20.0, 1.0)
            security_debt: float = min(security_issues / 10.0, 1.0)
            style_debt: float = max(0, (100 - pep8_score) / 100.0)

            # Weighted debt ratio
            debt_ratio: float = (
                complexity_debt * 0.30
                + duplication_debt * 0.20
                + security_debt * 0.35
                + style_debt * 0.15
            ) * 100

            # Time estimation (minutes to fix)
            base_time_per_issue: int = 15  # minutes
            debt_minutes: float = (
                (complexity / 10) * base_time_per_issue
                + (duplication / 5) * base_time_per_issue
                + security_issues * base_time_per_issue * 2
                + ((100 - pep8_score) / 10) * base_time_per_issue
            )

            # Scale by file size
            size_factor: float = math.log10(max(lines_of_code, 10)) / 2
            debt_minutes *= size_factor

            return round(debt_ratio, 2), round(debt_minutes, 1)
        except (ValueError, OverflowError, ZeroDivisionError):
            return 0.0, 0.0

    def _calculate_quality_index(self, result: FileAnalysisResult) -> float:
        """Calculate comprehensive code quality index"""
        try:
            metrics: ExtendedQualityMetrics = result.quality_metrics

            # Individual quality scores
            complexity_score: int = max(0, 100 - (metrics.cyclomatic_complexity * 2))
            maintainability_score: float = metrics.maintainability_index
            readability_score: float = result.readability_metrics.score
            style_score: float = metrics.pep8_compliance
            duplication_score: float = max(0, 100 - (metrics.code_duplication * 4))
            debt_score: float = max(0, 100 - metrics.technical_debt_ratio)
            security_score: float = result.get_security_score()

            # Weighted average
            weights: t.Tuple[float, ...] = (0.18, 0.18, 0.16, 0.14, 0.12, 0.12, 0.10)
            scores: t.Tuple[t.Any, ...] = (
                complexity_score,
                maintainability_score,
                readability_score,
                style_score,
                duplication_score,
                debt_score,
                security_score,
            )

            quality_index: float = sum(
                score * weight for score, weight in zip(scores, weights)
            )
            return round(quality_index, 2)
        except Exception:
            return 0.0

    def analyse_project(
        self, project_path: str, max_files: int = 1000
    ) -> ProjectAnalysisResult:
        """Perform comprehensive project-level analysis"""
        start_time: float = time.time()

        # Find Python files
        python_files = self._find_python_files(project_path)
        total_found = len(python_files)

        if total_found == 0:
            raise ValueError(f"No Python files found in {project_path}")

        if total_found > max_files:
            self._log_warning(s("limiting_analysis_to_n", max_files, total_found))
            python_files = python_files[:max_files]

        if self.progress:
            print(s("found_n_files_to_analyse", len(python_files)))

        # Analyse individual files
        file_results: t.List[FileAnalysisResult] = []
        files_with_errors: int = 0

        for idx, file_path in enumerate(python_files, 1):
            if self.progress:
                self._log_progress(idx, len(python_files), file_path)

            try:
                result: FileAnalysisResult = self.analyse_file(file_path)
                file_results.append(result)
                if result.syntax_errors:
                    files_with_errors += 1
            except Exception as error:
                self._log_error(f"Failed to analyse {file_path}: {error}")
                files_with_errors += 1

        # Project-level duplication analysis
        self._log_info(s("performing_project_level_dedup") + "...")
        duplication_result: DuplicationResult = self._analyse_project_duplication(
            file_results
        )

        # Calculate project statistics
        project_result = ProjectAnalysisResult(
            project_path=project_path,
            analysis_start_time=start_time,
            analysis_duration=time.time() - start_time,
            total_files_found=total_found,
            files_analysed=len(file_results),
            files_with_errors=files_with_errors,
            file_results=file_results,
            duplication_result=duplication_result,
        )

        # Calculate aggregated statistics
        self.calculate_project_statistics(project_result)

        if self.progress:
            print(
                f"\n{Fore.GREEN}{s('generating_report_for_n_files', str(len(file_results)))}...{Style.RESET_ALL}"
            )

        return project_result

    def _find_python_files(self, path: str) -> t.List[str]:
        """Find all Python files with smart filtering"""

        python_files: t.List[str] = []

        # Directories to skip
        skip_dirs: t.Set[str] = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            ".mypy_cache",
            "venv",
            "env",
            ".venv",
            ".env",
            "node_modules",
            ".tox",
            ".coverage",
            "htmlcov",
            "build",
            "dist",
            ".eggs",
            "site-packages",
            ".idea",
            ".vscode",
            "migrations",
        }

        if os.path.isfile(path):
            if path.endswith(".py"):
                python_files.append(path)
        else:
            for root, dirs, files in os.walk(path):
                # Filter out directories to skip
                dirs[:] = [d for d in dirs if d not in skip_dirs]

                for file in files:
                    if (
                        file.endswith(".py")
                        and not file.startswith(".")
                        and not file.startswith("test_")
                        and file != "__init__.py"
                    ):
                        python_files.append(os.path.join(root, file))
                    elif (
                        file == "__init__.py"
                        and os.path.getsize(os.path.join(root, file)) > 100
                    ):
                        # Include non-trivial __init__.py files
                        python_files.append(os.path.join(root, file))

        return sorted(python_files)

    def _analyse_project_duplication(
        self, file_results: t.List[FileAnalysisResult]
    ) -> DuplicationResult:
        """Analyse cross-file duplication"""

        try:
            file_contents: t.List[t.Tuple[str, str]] = []

            for result in file_results:
                if result.syntax_errors:
                    continue

                try:
                    with open(
                        result.file_path, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        content: str = f.read()
                        if content.strip():
                            file_contents.append((result.file_path, content))
                except Exception as error:
                    self._log_warning(
                        f"Could not read {result.file_path} for duplication analysis: {error}"
                    )

            return self.duplication_detector.analyse_project(file_contents)
        except Exception as error:
            self._log_error(f"Project duplication analysis failed: {error}")
            return DuplicationResult(0, 0, 0, 0.0, {})

    def calculate_project_statistics(
        self, project_result: ProjectAnalysisResult
    ) -> None:
        """Calculate comprehensive project statistics"""

        try:
            results = project_result.file_results

            if not results:
                return

            # Aggregate basic metrics
            project_result.total_lines = sum(
                r.quality_metrics.lines_of_code for r in results
            )
            project_result.total_logical_lines = sum(
                r.quality_metrics.logical_lines_of_code for r in results
            )
            project_result.total_functions = sum(
                r.quality_metrics.function_count for r in results
            )
            project_result.total_classes = sum(
                r.quality_metrics.class_count for r in results
            )
            project_result.total_security_issues = sum(
                len(r.security_issues) for r in results
            )
            project_result.total_style_issues = sum(
                len(r.pep8_result.issues) for r in results
            )
            project_result.total_dead_code_items = sum(
                len(r.dead_code_info) for r in results
            )

            # Quality distribution
            quality_categories: t.Dict[str, int] = {
                "Excellent": 0,
                "Good": 0,
                "Fair": 0,
                "Poor": 0,
                "Critical": 0,
            }
            complexity_categories: t.Dict[str, int] = {
                "Simple": 0,
                "Moderate": 0,
                "Complex": 0,
                "Very Complex": 0,
            }
            maintainability_categories: t.Dict[str, int] = {
                "Excellent": 0,
                "Good": 0,
                "Fair": 0,
                "Poor": 0,
                "Legacy": 0,
            }

            for result in results:
                # Quality distribution
                quality_score = result.get_overall_quality_score()
                if quality_score >= 90:
                    quality_categories["Excellent"] += 1
                elif quality_score >= 75:
                    quality_categories["Good"] += 1
                elif quality_score >= 60:
                    quality_categories["Fair"] += 1
                elif quality_score >= 40:
                    quality_categories["Poor"] += 1
                else:
                    quality_categories["Critical"] += 1

                # Complexity distribution
                complexity_categories[result.get_complexity_category()] += 1

                # Maintainability distribution
                maintainability_categories[result.get_maintainability_category()] += 1

            project_result.quality_distribution = quality_categories
            project_result.complexity_distribution = complexity_categories
            project_result.maintainability_distribution = maintainability_categories

            # Security issues by severity
            security_by_severity: t.Dict[str, int] = {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
            }
            most_vulnerable: t.List[t.Tuple[str, int]] = []

            for result in results:
                security_count = len(result.security_issues)
                if security_count > 0:
                    most_vulnerable.append((result.file_path, security_count))

                for issue in result.security_issues:
                    security_by_severity[issue.severity.severity_name] += 1

            project_result.security_issues_by_severity = security_by_severity
            project_result.most_vulnerable_files = sorted(
                most_vulnerable, key=lambda x: x[1], reverse=True
            )[:10]

            # Technical debt
            total_debt_hours: float = (
                sum(r.quality_metrics.technical_debt_minutes for r in results) / 60.0
            )
            avg_debt_ratio: float = sum(
                r.quality_metrics.technical_debt_ratio for r in results
            ) / len(results)

            project_result.total_technical_debt_hours = round(total_debt_hours, 1)
            project_result.avg_technical_debt_ratio = round(avg_debt_ratio, 1)
        except Exception as error:
            self._log_error(f"Error calculating project statistics: {error}")
