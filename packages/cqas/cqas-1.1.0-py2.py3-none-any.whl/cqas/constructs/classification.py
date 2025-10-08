#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classification"""

import typing as t
from enum import Enum, auto

__all__: t.Tuple[str, ...] = ("Confidence", "ElementType")


class ElementType(Enum):
    """Element type"""

    FUNCTION = auto()
    CLASS = auto()
    VARIABLE = auto()
    IMPORT = auto()


class Confidence(Enum):
    """Confidence enum"""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
