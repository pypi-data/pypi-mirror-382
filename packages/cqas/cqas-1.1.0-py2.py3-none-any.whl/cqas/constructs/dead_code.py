#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dead code constructs"""

import typing as t
from dataclasses import dataclass

from .classification import Confidence, ElementType

__all__: t.Tuple[str, ...] = ("DeadCodeInfo",)


@dataclass
class DeadCodeInfo:
    """Information about dead code detection"""

    line_number: int
    element_type: ElementType
    element_name: str
    reason: str
    confidence: Confidence
