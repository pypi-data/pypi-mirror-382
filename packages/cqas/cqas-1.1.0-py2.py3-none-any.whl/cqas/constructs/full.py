#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full code analysis"""

import typing as t
from dataclasses import dataclass, field

from cqas.lang import s

from .complexity import ComplexityHotspot
from .dead_code import DeadCodeInfo
from .duplication import DuplicationResult
from .halstead import HalsteadMetrics
from .imports import ImportAnalysisResult
from .pep8 import PEP8CheckResult
from .readability import ReadabilityMetrics
from .security import CVSSSeverity, SecurityIssue

__all__: t.Tuple[str, ...] = (
    "ExtendedQualityMetrics",
    "FileAnalysisResult",
    "ProjectAnalysisResult",
)


@dataclass
class ExtendedQualityMetrics:
    """Comprehensive code quality metrics"""

    # Basic metrics
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    logical_lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0

    # Code structure
    function_count: int = 0
    class_count: int = 0
    method_count: int = 0
    avg_function_complexity: float = 0.0
    max_function_complexity: int = 0
    avg_function_length: float = 0.0
    max_function_length: int = 0

    # Quality indices
    code_duplication: float = 0.0
    maintainability_index: float = 0.0
    technical_debt_ratio: float = 0.0
    technical_debt_minutes: float = 0.0
    readability_score: float = 0.0
    code_quality_index: float = 0.0

    # Halstead metrics
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    halstead_bugs: float = 0.0
    halstead_time: float = 0.0

    # Complexity details
    max_nesting_depth: int = 0
    avg_nesting_depth: float = 0.0
    complexity_hotspots: t.List[ComplexityHotspot] = field(default_factory=list)  # type: ignore

    # Line analysis
    avg_line_length: float = 0.0
    max_line_length: int = 0
    long_line_count: int = 0

    # Documentation metrics
    docstring_coverage: float = 0.0
    comment_ratio: float = 0.0
    type_hint_coverage: float = 0.0

    # Import metrics
    total_imports: int = 0
    unique_modules: int = 0
    stdlib_imports: int = 0
    third_party_imports: int = 0
    local_imports: int = 0
    circular_imports: int = 0

    # Style metrics
    pep8_compliance: float = 100.0
    style_issues: int = 0
    naming_violations: int = 0

    # Bug prediction
    estimated_bugs: float = 0.0
    bug_density: float = 0.0  # per 1000 lines


@dataclass
class FileAnalysisResult:
    """Complete analysis result for a single file with extensive metrics"""

    file_path: str
    analysis_time: float = 0.0
    syntax_errors: t.List[str] = field(default_factory=list)  # type: ignore

    # Core metrics
    quality_metrics: ExtendedQualityMetrics = field(
        default_factory=ExtendedQualityMetrics
    )

    # Analysis results
    security_issues: t.List[SecurityIssue] = field(default_factory=list)  # type: ignore
    dead_code_info: t.List[DeadCodeInfo] = field(default_factory=list)  # type: ignore
    pep8_result: PEP8CheckResult = field(
        default_factory=lambda: PEP8CheckResult([], 100.0)
    )
    readability_metrics: ReadabilityMetrics = field(default_factory=ReadabilityMetrics)
    import_analysis: ImportAnalysisResult = field(
        default_factory=lambda: ImportAnalysisResult([], [], 0, 0, 0, 0, 0, [])
    )
    halstead_metrics: HalsteadMetrics = field(
        default_factory=lambda: HalsteadMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0, 0)
    )

    # Duplication analysis
    duplication_percentage: float = 0.0
    duplicate_blocks: int = 0

    def get_overall_quality_score(self) -> float:
        """Calculate comprehensive quality score"""
        # Weight different aspects of code quality
        complexity_score = max(
            0, 100 - (self.quality_metrics.cyclomatic_complexity * 1.8)
        )
        maintainability_score = self.quality_metrics.maintainability_index
        readability_score = self.readability_metrics.score
        style_score = self.pep8_result.compliance_score
        duplication_score = max(0, 100 - (self.duplication_percentage * 4))
        debt_score = max(0, 100 - self.quality_metrics.technical_debt_ratio)

        weights = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
        scores = [
            complexity_score,
            maintainability_score,
            readability_score,
            style_score,
            duplication_score,
            debt_score,
        ]

        return sum(score * weight for score, weight in zip(scores, weights))

    def get_security_score(self) -> float:
        """Calculate security score based on CVSS impact"""
        if not self.security_issues:
            return 100.0

        total_impact = 0.0
        for issue in self.security_issues:
            # Weight by severity
            if issue.severity == CVSSSeverity.CRITICAL:
                total_impact += issue.cvss_score * 2.0
            elif issue.severity == CVSSSeverity.HIGH:
                total_impact += issue.cvss_score * 1.5
            else:
                total_impact += issue.cvss_score

        # Normalise to 0-100 scale
        max_possible_impact = len(self.security_issues) * 20.0
        security_score = max(0.0, 100.0 - (total_impact / max_possible_impact) * 100.0)
        return min(100.0, security_score)

    def get_maintainability_category_human(self) -> str:
        """Get human maintainability category based on index"""
        score: float = self.quality_metrics.maintainability_index
        if score >= 85:
            return s("excellent")
        if score >= 70:
            return s("good")
        if score >= 55:
            return s("fair")
        if score >= 25:
            return s("poor")
        return s("legacy")

    def get_complexity_category_human(self) -> str:
        """Get human complexity category"""
        complexity = self.quality_metrics.cyclomatic_complexity
        if complexity <= 10:
            return s("simple")
        if complexity <= 20:
            return s("moderate")
        if complexity <= 50:
            return s("complex")
        return s("very_complex")

    def get_maintainability_category(self) -> str:
        """Get maintainability category based on index"""
        score: float = self.quality_metrics.maintainability_index
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Good"
        if score >= 55:
            return "Fair"
        if score >= 25:
            return "Poor"
        return "Legacy"

    def get_complexity_category(self) -> str:
        """Get complexity category"""
        complexity = self.quality_metrics.cyclomatic_complexity
        if complexity <= 10:
            return "Simple"
        if complexity <= 20:
            return "Moderate"
        if complexity <= 50:
            return "Complex"
        return "Very Complex"


@dataclass
class ProjectAnalysisResult:
    """Comprehensive project-level analysis results"""

    project_path: str
    analysis_start_time: float
    analysis_duration: float
    total_files_found: int
    files_analysed: int
    files_with_errors: int

    # File results
    file_results: t.List[FileAnalysisResult] = field(default_factory=list)  # type: ignore

    # Project-level metrics
    duplication_result: DuplicationResult = field(
        default_factory=lambda: DuplicationResult(0, 0, 0, 0.0, {})
    )

    # Aggregated statistics
    total_lines: int = 0
    total_logical_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    total_security_issues: int = 0
    total_style_issues: int = 0
    total_dead_code_items: int = 0

    # Quality distribution
    quality_distribution: t.Dict[str, int] = field(default_factory=dict)  # type: ignore
    complexity_distribution: t.Dict[str, int] = field(default_factory=dict)  # type: ignore
    maintainability_distribution: t.Dict[str, int] = field(default_factory=dict)  # type: ignore

    # Security analysis
    security_issues_by_severity: t.Dict[str, int] = field(default_factory=dict)  # type: ignore
    most_vulnerable_files: t.List[t.Tuple[str, int]] = field(default_factory=list)  # type: ignore

    # Technical debt
    total_technical_debt_hours: float = 0.0
    avg_technical_debt_ratio: float = 0.0

    def get_overall_project_quality(self) -> float:
        """Calculate overall project quality score"""
        if not self.file_results:
            return 0.0
        return sum(
            result.get_overall_quality_score() for result in self.file_results
        ) / len(self.file_results)

    def get_overall_project_security(self) -> float:
        """Calculate overall project security score"""
        if not self.file_results:
            return 100.0
        return sum(result.get_security_score() for result in self.file_results) / len(
            self.file_results
        )
