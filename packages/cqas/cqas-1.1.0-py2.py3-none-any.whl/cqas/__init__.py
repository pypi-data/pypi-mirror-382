#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CQaS: Code Quality and Security analyser"""

import typing as t

from . import analysers, constructs

__version__: str = "1.1.0"
__all__: t.Tuple[str, ...] = (
    "__version__",
    "analysers",
    "constructs",
)
