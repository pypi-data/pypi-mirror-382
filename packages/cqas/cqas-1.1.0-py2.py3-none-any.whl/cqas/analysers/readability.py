#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code readability analyser"""

import ast
import re
import typing as t

from cqas.constructs.readability import ReadabilityMetrics

from .base import BaseAnalyser

__all__: t.Tuple[str, ...] = ("ReadabilityAnalyser",)


class ReadabilityAnalyser(BaseAnalyser):
    """Comprehensive code readability assessment"""

    def __init__(self, file_path: str, content: str):
        super().__init__(file_path, content)
        self.metrics: ReadabilityMetrics = ReadabilityMetrics()
        self.variable_names: t.List[str] = []
        self.function_names: t.List[str] = []
        self.class_names: t.List[str] = []
        self.nesting_depths: t.List[int] = []
        self.current_nesting: int = 0
        self.docstring_count: int = 0
        self.function_count: int = 0
        self.class_count: int = 0
        self.type_hints_found: int = 0
        self.total_annotations: int = 0

    def get_metrics(self) -> ReadabilityMetrics:
        """Perform comprehensive readability analysis"""
        self._analyse_line_metrics()

        if self.tree:
            self.visit(self.tree)

        self._calculate_naming_scores()
        self._calculate_documentation_quality()
        self._calculate_final_metrics()

        return self.metrics

    def _analyse_line_metrics(self) -> None:
        """Analyse line-level metrics"""
        line_lengths: t.List[int] = []
        comment_lines: int = 0

        for line in self.lines:
            line_lengths.append(len(line))
            if line.strip().startswith("#"):
                comment_lines += 1

        if line_lengths:
            self.metrics.avg_line_length = sum(line_lengths) / len(line_lengths)
            self.metrics.max_line_length = max(line_lengths)

        total_lines: int = len([line for line in self.lines if line.strip()])
        self.metrics.comment_ratio = (comment_lines / max(total_lines, 1)) * 100

    def visit_FunctionDef(
        self, node: t.Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> None:
        """Visit function definitions"""

        self.function_count += 1
        self.function_names.append(node.name)

        # Check for docstring
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        ):
            self.docstring_count += 1

        # Check for type hints
        if node.returns:
            self.type_hints_found += 1
        self.total_annotations += 1

        for arg in node.args.args:
            if arg.annotation:
                self.type_hints_found += 1
            self.total_annotations += 1

        old_nesting = self.current_nesting
        self.current_nesting += 1
        self.nesting_depths.append(self.current_nesting)
        self.generic_visit(node)
        self.current_nesting = old_nesting

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions"""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions"""
        self.class_count += 1
        self.class_names.append(node.name)

        # Check for docstring
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        ):
            self.docstring_count += 1

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Visit variable names"""
        if isinstance(node.ctx, ast.Store):
            self.variable_names.append(node.id)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Track nesting in if statements"""
        old_nesting = self.current_nesting
        self.current_nesting += 1
        self.nesting_depths.append(self.current_nesting)
        self.generic_visit(node)
        self.current_nesting = old_nesting

    def visit_For(self, node: ast.For) -> None:
        """Track nesting in for loops"""
        old_nesting = self.current_nesting
        self.current_nesting += 1
        self.nesting_depths.append(self.current_nesting)
        self.generic_visit(node)
        self.current_nesting = old_nesting

    def visit_While(self, node: ast.While) -> None:
        """Track nesting in while loops"""
        old_nesting = self.current_nesting
        self.current_nesting += 1
        self.nesting_depths.append(self.current_nesting)
        self.generic_visit(node)
        self.current_nesting = old_nesting

    def _calculate_naming_scores(self) -> None:
        """Calculate naming convention scores"""
        self.metrics.variable_naming_score = self._score_names(
            self.variable_names, "snake_case"
        )
        self.metrics.function_naming_score = self._score_names(
            self.function_names, "snake_case"
        )
        self.metrics.class_naming_score = self._score_names(
            self.class_names, "pascal_case"
        )

    def _score_names(self, names: t.List[str], convention: str) -> float:
        """Score naming convention adherence"""
        if not names:
            return 100.0

        good_names = 0
        for name in names:
            if convention == "snake_case":
                if re.match(r"^[a-z_][a-z0-9_]*$", name) and len(name) > 1:
                    good_names += 1
            elif convention == "pascal_case":
                if re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                    good_names += 1

        return (good_names / len(names)) * 100

    def _calculate_documentation_quality(self) -> None:
        """Calculate documentation quality metrics"""
        # Type hint coverage
        if self.total_annotations > 0:
            self.metrics.type_hint_coverage = (
                self.type_hints_found / self.total_annotations
            ) * 100

        # Docstring coverage
        total_definitions = self.function_count + self.class_count
        if total_definitions > 0:
            self.metrics.docstring_coverage = (
                self.docstring_count / total_definitions
            ) * 100

        # Overall documentation quality
        doc_factors = [
            self.metrics.type_hint_coverage,
            self.metrics.docstring_coverage,
            min(100, self.metrics.comment_ratio * 2),  # Cap comment contribution
        ]
        self.metrics.documentation_quality = sum(doc_factors) / len(doc_factors)

    def _calculate_final_metrics(self) -> None:
        """Calculate final readability metrics"""
        if self.nesting_depths:
            self.metrics.nesting_depth_avg = sum(self.nesting_depths) / len(
                self.nesting_depths
            )
            self.metrics.nesting_depth_max = max(self.nesting_depths)
