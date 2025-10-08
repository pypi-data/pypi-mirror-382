#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyser constructs"""

# pylint: disable=R0801

import typing as t

from . import classification, dead_code, duplication, full, halstead, imports, pep8, readability, security

__all__: t.Tuple[str, ...] = (
    "classification",
    "dead_code",
    "duplication",
    "full",
    "halstead",
    "imports",
    "pep8",
    "readability",
    "security",
)
