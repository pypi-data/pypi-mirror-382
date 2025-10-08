#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complexity analyser"""

import ast
import typing as t

from cqas.constructs.classification import ElementType
from cqas.constructs.complexity import ComplexityHotspot, ComplexityMetrics, FunctionComplexity

from .base import BaseAnalyser

__all__: t.Tuple[str, ...] = ("ComplexityAnalyser",)


class ComplexityAnalyser(BaseAnalyser):
    """Cyclomatic and cognitive complexity analysis"""

    def __init__(self, file_path: str, content: str):
        super().__init__(file_path, content)
        self.cyclomatic_complexity: int = 1  # Base complexity
        self.cognitive_complexity: int = 0
        self.nesting_level: int = 0
        self.function_complexities: t.List[FunctionComplexity] = []
        self.current_function_complexity: int = 0
        self.current_function_name: str = ""
        self.function_count: int = 0
        self.class_count: int = 0
        self.max_nesting: int = 0
        self.complexity_hotspots: t.List[ComplexityHotspot] = []

    def visit_FunctionDef(
        self, node: t.Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> None:
        """Visit function definition"""
        self.function_count += 1

        old_complexity: int = self.current_function_complexity
        old_name: str = self.current_function_name

        self.current_function_complexity = 1  # Base complexity
        self.current_function_name = node.name

        old_nesting: int = self.nesting_level

        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.function_complexities.append(
            FunctionComplexity(
                name=node.name,
                cyclomatic=self.current_function_complexity,
                line=node.lineno,
            )
        )

        if self.current_function_complexity > 10:
            hotspot: ComplexityHotspot = ComplexityHotspot(
                type=ElementType.FUNCTION,
                name=node.name,
                complexity=self.current_function_complexity,
                line=node.lineno,
            )
            self.complexity_hotspots.append(hotspot)

        self.current_function_complexity = old_complexity
        self.current_function_name = old_name
        self.nesting_level = old_nesting

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions"""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions with method counting"""

        self.class_count += 1
        method_count = sum(
            1
            for n in ast.walk(node)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        )

        if method_count > 20:
            hotspot: ComplexityHotspot = ComplexityHotspot(
                type=ElementType.CLASS,
                name=node.name,
                method_count=method_count,
                line=node.lineno,
            )
            self.complexity_hotspots.append(hotspot)

        self.generic_visit(node)

    def _increment_complexity(self, cognitive_increment: int = 1) -> None:
        """Increment both complexity metrics"""
        self.cyclomatic_complexity += 1
        self.current_function_complexity += 1
        self.cognitive_complexity += cognitive_increment + self.nesting_level

    def visit_If(self, node: ast.If) -> None:
        """Visit if statements"""
        self._increment_complexity()
        old_nesting = self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level = old_nesting

    def visit_For(self, node: ast.For) -> None:
        """Visit for loops"""
        self._increment_complexity()
        old_nesting = self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level = old_nesting

    def visit_While(self, node: ast.While) -> None:
        """Visit while loops"""
        self._increment_complexity()
        old_nesting = self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level = old_nesting

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statements"""

        handlers_complexity = len(node.handlers)
        if node.orelse:  # else clause
            handlers_complexity += 1
        if node.finalbody:  # finally clause
            handlers_complexity += 1

        self.cyclomatic_complexity += handlers_complexity
        self.current_function_complexity += handlers_complexity
        self.cognitive_complexity += handlers_complexity
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit except handlers"""
        old_nesting = self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level = old_nesting

    def visit_With(self, node: ast.With) -> None:
        """Visit with statements"""
        self._increment_complexity()
        old_nesting = self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level = old_nesting

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit boolean operations (and/or)"""
        complexity_increment = len(node.values) - 1
        self.cyclomatic_complexity += complexity_increment
        self.current_function_complexity += complexity_increment
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Visit list comprehensions"""
        self._increment_complexity(0)  # Lower cognitive load
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Visit dictionary comprehensions"""
        self._increment_complexity(0)  # Lower cognitive load
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Visit set comprehensions"""
        self._increment_complexity(0)  # Lower cognitive load
        self.generic_visit(node)

    def get_metrics(self) -> ComplexityMetrics:
        """Get complexity metrics"""
        avg_function_complexity = (
            sum(comp.cyclomatic for comp in self.function_complexities)
            / len(self.function_complexities)
            if self.function_complexities
            else 0.0
        )

        max_function_complexity = (
            max(comp.cyclomatic for comp in self.function_complexities)
            if self.function_complexities
            else 0
        )

        return ComplexityMetrics(
            cyclomatic_complexity=self.cyclomatic_complexity,
            cognitive_complexity=self.cognitive_complexity,
            function_count=self.function_count,
            class_count=self.class_count,
            avg_function_complexity=round(avg_function_complexity, 2),
            max_function_complexity=max_function_complexity,
            max_nesting_depth=self.max_nesting,
            function_complexities=self.function_complexities,
            complexity_hotspots=self.complexity_hotspots,
        )
