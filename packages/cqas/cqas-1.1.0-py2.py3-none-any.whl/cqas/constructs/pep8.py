#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PEP8 checker"""

import typing as t
from dataclasses import dataclass

__all__: t.Tuple[str, ...] = (
    "StyleIssue",
    "PEP8CheckResult",
)


@dataclass
class StyleIssue:
    """Style issue"""

    line: int
    column: int
    message: str


@dataclass
class PEP8CheckResult:
    """PEP8 checker result"""

    issues: t.List[StyleIssue]
    compliance_score: float
