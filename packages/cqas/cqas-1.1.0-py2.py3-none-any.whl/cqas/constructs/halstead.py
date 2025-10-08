#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Halstead metrics"""

import typing as t
from dataclasses import dataclass

__all__: t.Tuple[str, ...] = ("HalsteadMetrics",)


@dataclass
class HalsteadMetrics:
    """Halstead metrics"""

    volume: float
    difficulty: float
    effort: float
    bugs_estimate: float
    time_to_implement: float
    vocabulary: int
    length: int
