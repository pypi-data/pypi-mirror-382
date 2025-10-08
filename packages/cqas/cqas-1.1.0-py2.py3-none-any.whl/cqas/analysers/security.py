#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Security analyser"""

import ast
import re
import typing as t

from cqas.constructs.classification import Confidence
from cqas.constructs.security import CVSSSeverity, SecurityIssue, VulnerabilityType

from .base import BaseAnalyser

__all__: t.Tuple[str, ...] = ("SecurityAnalyser",)


class SecurityAnalyser(BaseAnalyser):
    """Comprehensive security vulnerability detection covering all vulnerability types."""

    CODE_INJECTION_FUNCTIONS: t.Final[t.Dict[str, str]] = {
        "eval": "Use of eval call can risk executing arbitrary code",
        "exec": "Use of exec call can risk executing arbitrary code",
        "compile": "Compiling and running dynamic code",
        "__import__": "Dynamic module import",
        "getattr": "Dynamic attribute access",
        "setattr": "Dynamic attribute modification",
        "delattr": "Dynamic attribute deletion",
        "picle.load": "Arbitrary deserialisation can execute arbitrary code",
        "picle.loads": "Arbitrary string deserialisation can execute arbitrary code",
        "dill.load": "Arbitrary deserialisation can execute arbitrary code",
        "dill.loads": "Arbitrary string deserialisation can execute arbitrary code",
        "yaml.load": "yaml.load() call can lead to arbitrary Python execution",
        "yaml.loads": "yaml.loads() call can lead to arbitrary Python execution",
    }

    DANGEROUS_MODULES: t.Final[t.Dict[str, str]] = {
        "pickle": "Unsafe deserialisation can allow arbitrary code execution",
        "cPickle": "Unsafe deserialisation can allow arbitrary code execution",
        "dill": "Unsafe deserialisation can allow arbitrary code execution",
        "shelve": "Unsafe deserialisation can allow arbitrary code execution",
        "commands": "Module enabling command injection risk",
        "popen2": "Module enabling command injection risk",
    }

    WEAK_CRYPTO: t.Final[t.Dict[str, str]] = {
        "md5": "Weak cryptography algorithm vulnerable to collisions",
        "sha1": "Weak cryptography algorithm susceptible to attacks",
        "des": "Outdated cryptographic cipher with known weaknesses",
        "random.random": "Insecure random source, not cryptographically secure",
        "random.randint": "Insecure random source, not cryptographically secure",
        "random.choice": "Insecure random source, not cryptographically secure",
    }

    SQL_PATTERNS: t.Final[t.Dict[re.Pattern[str], str]] = {
        re.compile(
            r"SELECT\s+.*%s", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string formatting",
        re.compile(
            r"INSERT\s+.*%s", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string formatting",
        re.compile(
            r"UPDATE\s+.*%s", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string formatting",
        re.compile(
            r"DELETE\s+.*%s", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string formatting",
        re.compile(
            r"DROP\s+.*%s", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string formatting",
        re.compile(
            r"UNION\s+.*%s", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string formatting",
        re.compile(
            r"SELECT\s+.*\+.*", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string concatenation",
        re.compile(
            r"SELECT\s+.*format\(", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to .format() usage",
        re.compile(
            r"SELECT\s+.*\{.*\}", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to f-string or formatting",
        re.compile(
            r"WHERE\s+.*\+.*", re.IGNORECASE | re.MULTILINE
        ): "Possible SQL injection risk due to string concatenation",
    }

    SECRET_PATTERNS: t.Final[t.Dict[re.Pattern[str], str]] = {
        re.compile(
            r"""\b\w*(password|passwd)\w*\s*=\s*["'][^"']{8,}["']""",
            re.IGNORECASE | re.MULTILINE,
        ): "Hardcoded password detected",
        re.compile(
            r"""\b\w*secret\w*\s*=\s*["'][^"']{16,}["']""", re.IGNORECASE | re.MULTILINE
        ): "Hardcoded secret detected",
        re.compile(
            r"""\b\w*api[_-]?key\w*\s*=\s*["'][^"']{20,}["']""",
            re.IGNORECASE | re.MULTILINE,
        ): "Hardcoded API key detected",
        re.compile(
            r"""\b\w*token\w*\s*=\s*["'][^"']{20,}["']""", re.IGNORECASE | re.MULTILINE
        ): "Hardcoded token detected",
        re.compile(
            r"""\b\w*private[_-]?key\w*\s*=\s*["'][^"']{20,}["']""",
            re.IGNORECASE | re.MULTILINE,
        ): "Hardcoded private key detected",
        re.compile(
            r"""["'][A-Za-z0-9+/]{40,}={0,2}["']""", re.IGNORECASE | re.MULTILINE
        ): "Potential base64 encoded secret detected",
        re.compile(
            r"""[0-9a-fA-F]{32,}""", re.IGNORECASE | re.MULTILINE
        ): "Potential hex encoded secret detected",
    }

    COMMAND_INJECTION_PATTERNS: t.Final[t.Dict[re.Pattern[str], str]] = {
        re.compile(
            r"os\.system\s*\("
        ): "Use of os.system call - risk of command injection",
        re.compile(
            r"subprocess\.call\s*\([^)]*shell\s*=\s*True"
        ): "subprocess call with shell=True - command injection risk",
        re.compile(
            r"subprocess\.run\s*\([^)]*shell\s*=\s*True"
        ): "subprocess run with shell=True - command injection risk",
        re.compile(
            r"subprocess\.Popen\s*\([^)]*shell\s*=\s*True"
        ): "subprocess Popen with shell=True - command injection risk",
        re.compile(
            r"os\.popen\s*\("
        ): "Use of os.popen call - risk of command injection",
        re.compile(
            r"commands\.getoutput\s*\("
        ): "commands.getoutput call - risk of command injection",
    }

    def __init__(self, file_path: str, content: str) -> None:
        super().__init__(file_path, content)
        self.issues: t.List[SecurityIssue] = []
        self.lines = content.splitlines()
        self._scan_code_for_global_issues()

    def visit_Import(self, node: ast.Import) -> None:
        """Detect dangerous module imports."""
        for alias in node.names:
            root_module = alias.name.split(".")[0]
            if root_module in self.DANGEROUS_MODULES:
                self._add_issue(
                    node.lineno,
                    VulnerabilityType.DANGEROUS_IMPORT,
                    self.DANGEROUS_MODULES[root_module],
                    "Use safer alternatives or validate inputs",
                    Confidence.HIGH,
                    self._get_code_snippet(node.lineno),
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Detect dangerous from-imports."""
        if node.module:
            root_module = node.module.split(".")[0]
            if root_module in self.DANGEROUS_MODULES:
                description = self.DANGEROUS_MODULES[root_module]
                for alias in node.names:
                    self._add_issue(
                        node.lineno,
                        VulnerabilityType.DANGEROUS_IMPORT,
                        f"{description} ({node.module}.{alias.name})",
                        "Use safer alternatives or validate inputs",
                        Confidence.HIGH,
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect dangerous function calls."""
        func_name = self._get_function_name(node.func)

        # Code injection functions
        if func_name in self.CODE_INJECTION_FUNCTIONS:
            self._add_issue(
                node.lineno,
                VulnerabilityType.CODE_INJECTION,
                f"Use of dangerous function: {func_name}. {self.CODE_INJECTION_FUNCTIONS[func_name]}.",
                "Avoid dynamic code execution or use safer alternatives",
                Confidence.MEDIUM,
                self._get_code_snippet(node.lineno),
            )

        # Dangerous subprocess calls with shell=True
        if func_name in {"subprocess.call", "subprocess.run", "subprocess.Popen"}:
            for kw in node.keywords:
                if kw.arg == "shell" and self._is_true_constant(kw.value):
                    self._add_issue(
                        node.lineno,
                        VulnerabilityType.COMMAND_INJECTION,
                        "subprocess call with shell=True",
                        "Avoid shell=True or sanitize arguments properly",
                        Confidence.HIGH,
                        self._get_code_snippet(node.lineno),
                    )

        # Risky functions for command injection
        if func_name in {"os.system", "os.popen", "commands.getoutput"}:
            self._add_issue(
                node.lineno,
                VulnerabilityType.COMMAND_INJECTION,
                f"Use of risky function {func_name}",
                "Use subprocess module instead for better security",
                Confidence.HIGH,
                self._get_code_snippet(node.lineno),
            )

        # Weak cryptography or insecure random usage
        if func_name in self.WEAK_CRYPTO:
            description = self.WEAK_CRYPTO[func_name]
            remediation = (
                "Use stronger cryptography (e.g. hashlib.sha256) or secrets module"
            )
            self._add_issue(
                node.lineno,
                VulnerabilityType.WEAK_CRYPTO,
                f"Use of weak cryptographic or insecure function: {func_name} ({description})",
                remediation,
                Confidence.MEDIUM,
                self._get_code_snippet(node.lineno),
            )

        # Template injection
        if func_name in {"Template.substitute", "string.Template.substitute", "format"}:
            self._add_issue(
                node.lineno,
                VulnerabilityType.TEMPLATE_INJECTION,
                f"Potential template injection in call: {func_name}",
                "Validate and sanitize template inputs",
                Confidence.MEDIUM,
                self._get_code_snippet(node.lineno),
            )

        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check string constants for hardcoded secrets, SQL injection, and command injections."""
        if isinstance(node.value, str):
            self._check_string_vulnerabilities(node.lineno, node.value)
        self.generic_visit(node)

    def _scan_code_for_global_issues(self) -> None:
        """Scans code globally for global issues"""

        # Secrets
        for pattern, description in self.SECRET_PATTERNS.items():
            for match in pattern.finditer(self.content):
                char_pos: int = match.start()
                line_no: int = self.content.count("\n", 0, char_pos) + 1
                code_line: t.Optional[str] = self._get_code_snippet(line_no)
                if not code_line or code_line.startswith("#"):
                    continue
                self._add_issue(
                    line_no,
                    VulnerabilityType.HARDCODED_SECRET,
                    description,
                    "Use environment variables or secure key management",
                    Confidence.MEDIUM,
                    code_line,
                )

        # Command injection patterns
        for pattern, description in self.COMMAND_INJECTION_PATTERNS.items():
            for match in pattern.finditer(self.content):
                char_pos = match.start()
                line_no = self.content.count("\n", 0, char_pos) + 1
                code_line = self._get_code_snippet(line_no)
                if not code_line or code_line.startswith("#"):
                    continue
                self._add_issue(
                    line_no,
                    VulnerabilityType.COMMAND_INJECTION,
                    description,
                    "Use subprocess with argument lists instead of shell commands",
                    Confidence.HIGH,
                    code_line,
                )

    def _check_string_vulnerabilities(self, line_no: int, value: str) -> None:
        """Check string value against regex patterns for vulnerabilities."""
        # SQL injections
        for pattern, description in self.SQL_PATTERNS.items():
            if pattern.search(value):
                self._add_issue(
                    line_no,
                    VulnerabilityType.SQL_INJECTION,
                    description,
                    "Use parameterized queries or ORM methods",
                    Confidence.HIGH,
                    self._get_code_snippet(line_no),
                )
                return

    def _get_function_name(self, node: ast.AST) -> str:
        """Extract full dotted function name from AST node."""

        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            base = self._get_function_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr

        return ""

    def _is_true_constant(self, node: ast.AST) -> bool:
        """Check if AST node is a True boolean constant."""
        return isinstance(node, ast.Constant) and node.value is True

    def _get_code_snippet(self, line_no: int) -> t.Optional[str]:
        """Safely get the source code line snippet."""
        if 1 <= line_no <= len(self.lines):
            return self.lines[line_no - 1].strip()
        return None

    def _add_issue(
        self,
        line_number: int,
        vuln_type: VulnerabilityType,
        description: str,
        remediation: str,
        confidence: Confidence,
        code_snippet: t.Optional[str] = None,
    ) -> None:
        """Record a detected security issue."""
        severity = CVSSSeverity.from_score(vuln_type.base_cvss)
        issue = SecurityIssue(
            file_path=self.file_path,
            line_number=line_number,
            vulnerability_type=vuln_type,
            description=description,
            cvss_score=vuln_type.base_cvss,
            severity=severity,
            remediation=remediation,
            confidence=confidence,
            code_snippet=code_snippet,
        )
        self.issues.append(issue)
