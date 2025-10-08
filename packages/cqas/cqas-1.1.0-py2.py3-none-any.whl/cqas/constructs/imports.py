#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imports analyser"""

import typing as t
from dataclasses import dataclass

__all__: t.Tuple[str, ...] = (
    "ImportEntry",
    "FromImportEntry",
    "ImportAnalysisResult",
)


@dataclass
class ImportEntry:
    """Import statment"""

    module: str
    alias: t.Optional[str]
    line: int


@dataclass
class FromImportEntry:
    """Import-from statement"""

    module: str
    name: str
    alias: t.Optional[str]
    line: int
    level: int  # Relative import level (0 = absolute)


@dataclass
class ImportAnalysisResult:
    """Import analyser result"""

    imports: t.List[ImportEntry]
    from_imports: t.List[FromImportEntry]
    total_imports: int
    unique_modules: int
    stdlib_imports: int
    third_party_imports: int
    local_imports: int
    circular_dependencies: t.List[t.Tuple[str, str]]  # (moduleA, moduleB)
