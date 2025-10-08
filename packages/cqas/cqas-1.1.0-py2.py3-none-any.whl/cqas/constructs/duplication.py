#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code duplication"""

import typing as t
from dataclasses import dataclass

__all__: t.Tuple[str, ...] = ("DuplicationResult",)


@dataclass
class DuplicationResult:
    """Code duplication result"""

    duplicate_blocks_count: int
    duplicated_lines_estimate: int
    total_code_lines: int
    duplication_percentage: float
    duplicates: t.Dict[str, t.List[t.Tuple[str, int]]]
