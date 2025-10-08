#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Security Constructs"""

import typing as t
from dataclasses import dataclass
from enum import Enum

from .classification import Confidence

__all__: t.Tuple[str, ...] = ("CVSSSeverity", "VulnerabilityType", "SecurityIssue")


class CVSSSeverity(Enum):
    """CVSS severity classification"""

    NONE = (0.0, "NONE")
    LOW = (3.9, "LOW")
    MEDIUM = (6.9, "MEDIUM")
    HIGH = (8.9, "HIGH")
    CRITICAL = (10.0, "CRITICAL")

    def __init__(self, threshold: float, name: str):
        self.threshold = threshold
        self.severity_name = name

    @classmethod
    def from_score(cls, score: float) -> "CVSSSeverity":
        """Determine severity level from CVSS score"""
        if score == 0.0:
            return cls.NONE
        if score <= 3.9:
            return cls.LOW
        if score <= 6.9:
            return cls.MEDIUM
        if score <= 8.9:
            return cls.HIGH
        return cls.CRITICAL


class VulnerabilityType(Enum):
    """Types of security vulnerabilities"""

    SQL_INJECTION = ("sql_injection", 8.1)
    COMMAND_INJECTION = ("command_injection", 9.8)
    CODE_INJECTION = ("code_injection", 9.3)
    HARDCODED_SECRET = ("hardcoded_secret", 7.5)
    WEAK_CRYPTO = ("weak_cryptography", 7.4)
    DANGEROUS_IMPORT = ("dangerous_import", 4.3)
    DESERIALISATION = ("unsafe_deserialisation", 8.8)
    TEMPLATE_INJECTION = ("template_injection", 8.5)

    def __init__(self, vuln_type: str, base_cvss: float):
        self.vuln_type = vuln_type
        self.base_cvss = base_cvss


@dataclass
class SecurityIssue:
    """Represents a security vulnerability in code"""

    file_path: str
    line_number: int
    vulnerability_type: VulnerabilityType
    description: str
    cvss_score: float
    severity: CVSSSeverity
    confidence: Confidence
    remediation: t.Optional[str] = None
    code_snippet: t.Optional[str] = None
