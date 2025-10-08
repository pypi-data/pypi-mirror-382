#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code complexity constructs"""

import typing as t
from dataclasses import dataclass

from .classification import ElementType

__all__: t.Tuple[str, ...] = ("ComplexityMetrics",)


@dataclass
class FunctionComplexity:
    """Function complexity"""

    name: str
    cyclomatic: int
    line: int


@dataclass
class ComplexityHotspot:
    """Complexity hotspot"""

    type: ElementType
    name: str
    complexity: t.Optional[int] = None
    method_count: t.Optional[int] = None
    line: int = 0


@dataclass
class ComplexityMetrics:
    """Code complexity metrix"""

    cyclomatic_complexity: int
    cognitive_complexity: int
    function_count: int
    class_count: int
    avg_function_complexity: float
    max_function_complexity: int
    max_nesting_depth: int
    function_complexities: t.List[FunctionComplexity]
    complexity_hotspots: t.List[ComplexityHotspot]
