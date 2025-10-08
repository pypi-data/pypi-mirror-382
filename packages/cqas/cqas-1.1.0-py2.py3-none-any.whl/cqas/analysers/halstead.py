#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Halstead metrics calculation"""

import ast
import math
import typing as t
from collections import Counter

from cqas.constructs.halstead import HalsteadMetrics

from .base import BaseAnalyser

__all__: t.Tuple[str, ...] = ("HalsteadAnalyser",)


class HalsteadAnalyser(BaseAnalyser):
    """Halstead metrics calculation"""

    def __init__(self, file_path: str, content: str):
        super().__init__(file_path, content)
        self.operators: Counter[str] = Counter()
        self.operands: Counter[str] = Counter()

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Visit binary operations"""
        op_name = type(node.op).__name__
        self.operators[op_name] += 1
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        """Visit unary operations"""
        op_name = type(node.op).__name__
        self.operators[op_name] += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit boolean operations"""
        op_name = type(node.op).__name__
        self.operators[op_name] += 1
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        """Visit comparison operations"""
        for op in node.ops:
            op_name = type(op).__name__
            self.operators[op_name] += 1
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Visit variable names"""
        if not node.id.startswith("_"):  # Ignore private/special variables
            self.operands[node.id] += 1
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Visit constants (handles both new and old AST formats)"""
        const_repr = repr(node.value)[:50]  # Limit length
        self.operands[const_repr] += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions"""
        self.operators["def"] += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions"""
        self.operators["async_def"] += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions"""
        self.operators["class"] += 1
        self.generic_visit(node)

    def get_metrics(self) -> HalsteadMetrics:
        """Calculate Halstead metrics"""

        n1: int = len(self.operators)  # Unique operators
        n2: int = len(self.operands)  # Unique operands
        N1: int = sum(self.operators.values())  # Total operators
        N2: int = sum(self.operands.values())  # Total operands

        vocabulary: int = n1 + n2
        length: int = N1 + N2

        if vocabulary <= 1 or length == 0:
            return HalsteadMetrics(
                volume=0.0,
                difficulty=0.0,
                effort=0.0,
                bugs_estimate=0.0,
                time_to_implement=0.0,
                vocabulary=vocabulary,
                length=length,
            )

        try:
            volume = length * math.log2(vocabulary)
            difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0.0
            effort = difficulty * volume
            bugs_estimate = volume / 3000  # Halstead's formula
            time_to_implement = effort / 18  # Seconds

            return HalsteadMetrics(
                volume=round(volume, 2),
                difficulty=round(difficulty, 2),
                effort=round(effort, 2),
                bugs_estimate=round(bugs_estimate, 4),
                time_to_implement=round(time_to_implement, 2),
                vocabulary=vocabulary,
                length=length,
            )
        except (ValueError, ZeroDivisionError, OverflowError):
            return HalsteadMetrics(
                volume=0.0,
                difficulty=0.0,
                effort=0.0,
                bugs_estimate=0.0,
                time_to_implement=0.0,
                vocabulary=vocabulary,
                length=length,
            )
