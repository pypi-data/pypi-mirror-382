#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code readability constructs"""

import typing as t
from dataclasses import dataclass

__all__: t.Tuple[str, ...] = ("ReadabilityMetrics",)


@dataclass
class ReadabilityMetrics:
    """Code readability assessment metrics"""

    avg_line_length: float = 0.0
    max_line_length: int = 0
    variable_naming_score: float = 0.0
    function_naming_score: float = 0.0
    class_naming_score: float = 0.0
    comment_ratio: float = 0.0
    docstring_coverage: float = 0.0
    nesting_depth_avg: float = 0.0
    nesting_depth_max: int = 0
    type_hint_coverage: float = 0.0
    documentation_quality: float = 0.0

    @property
    def score(self) -> float:
        """Calculate overall readability score"""
        scores: t.Tuple[float, ...] = (
            min(
                100, max(0, 100 - (self.avg_line_length - 60) * 2)
            ),  # Penalise long lines
            min(100, max(0, 150 - self.max_line_length)),  # Penalise very long lines
            self.variable_naming_score,
            self.function_naming_score,
            self.class_naming_score,
            min(100, self.comment_ratio * 200),  # Reward comments up to 50%
            self.docstring_coverage,
            max(0, 100 - self.nesting_depth_avg * 10),  # Penalise deep nesting
            max(0, 100 - self.nesting_depth_max * 5),
            self.type_hint_coverage,
            self.documentation_quality,
        )
        return sum(scores) / len(scores)
