#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PEP8 Checker"""

import ast
import re
import typing as t

from cqas.constructs.pep8 import PEP8CheckResult, StyleIssue

__all__: t.Tuple[str, ...] = ("PEP8ASTChecker", "PEP8StyleChecker")


class PEP8StyleChecker:  # pylint: disable=R0903
    """PEP8 and style compliance checker"""

    def __init__(self) -> None:
        self.issues: t.List[StyleIssue] = []

    def check(self, content: str) -> PEP8CheckResult:
        """Check file content for PEP8 compliance"""

        self.issues = []
        lines: t.List[str] = content.splitlines()
        total_checks: int = 0
        failed_checks: int = 0

        for line_num, line in enumerate(lines, 1):
            total_checks += self._check_line(line, line_num)

        try:
            tree: ast.Module = ast.parse(content)
            ast_checker: PEP8ASTChecker = PEP8ASTChecker()
            ast_checker.visit(tree)
            self.issues.extend(ast_checker.issues)
            total_checks += len(ast_checker.total_checks)
            failed_checks += len(ast_checker.issues)
        except SyntaxError:
            pass

        compliance_score: float = (
            (total_checks - failed_checks) / max(total_checks, 1)
        ) * 100

        return PEP8CheckResult(
            issues=self.issues,
            compliance_score=max(0.0, compliance_score),
        )

    def _check_line(self, line: str, line_num: int) -> int:
        """Check individual line for PEP8 issues and return number of checks performed"""
        checks: int = 0

        # Check line length
        checks += 1
        if len(line) > 120:
            self.issues.append(
                StyleIssue(
                    line=line_num,
                    column=len(line),
                    message=f"Line too long ({len(line)} > 120 characters)",
                )
            )

        # Check trailing whitespace
        checks += 1
        if line.rstrip() != line:
            self.issues.append(
                StyleIssue(
                    line=line_num,
                    column=len(line.rstrip()),
                    message="Trailing whitespace",
                )
            )

        # Check indentation (multiple of 4)
        if line.lstrip() != line:
            checks += 1
            indent: int = len(line) - len(line.lstrip())
            if indent % 4 != 0:
                self.issues.append(
                    StyleIssue(
                        line=line_num,
                        column=1,
                        message="Indentation is not a multiple of four",
                    )
                )

        # Check for tabs
        if "\t" in line:
            checks += 1
            tab_index: int = line.index("\t") + 1
            self.issues.append(
                StyleIssue(
                    line=line_num,
                    column=tab_index,
                    message="Indentation contains tabs",
                )
            )

        # Multiple statements on one line
        if ";" in line and not line.strip().startswith("#"):
            checks += 1
            semicolon_index: int = line.index(";") + 1
            self.issues.append(
                StyleIssue(
                    line=line_num,
                    column=semicolon_index,
                    message="Multiple statements on one line (semicolon)",
                )
            )

        return checks


class PEP8ASTChecker(ast.NodeVisitor):
    """AST-based PEP8 style checks"""

    def __init__(self) -> None:
        self.issues: t.List[StyleIssue] = []
        self.total_checks: t.List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition"""

        self.total_checks.append(f"function_naming_{node.name}")
        if not self._is_snake_case(node.name) and not node.name.startswith("_"):
            self.issues.append(
                StyleIssue(
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Function name should be lowercase with underscores: {node.name}",
                )
            )

        self.total_checks.append(f"function_args_{node.name}")
        total_args: int = len(node.args.args) + len(node.args.kwonlyargs)
        if total_args > 7:
            self.issues.append(
                StyleIssue(
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Too many arguments ({total_args}/7)",
                )
            )

        if not node.name.startswith("_") and (
            not node.body
            or not isinstance(node.body[0], ast.Expr)
            or not isinstance(node.body[0].value, ast.Constant)
        ):
            self.total_checks.append(f"function_docstring_{node.name}")
            self.issues.append(
                StyleIssue(
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Missing docstring in public function: {node.name}",
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition"""

        self.total_checks.append(f"class_naming_{node.name}")
        if not self._is_pascal_case(node.name):
            self.issues.append(
                StyleIssue(
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Class name should use PascalCase: {node.name}",
                )
            )

        if not node.name.startswith("_") and (
            not node.body
            or not isinstance(node.body[0], ast.Expr)
            or not isinstance(node.body[0].value, ast.Constant)
        ):
            self.total_checks.append(f"class_docstring_{node.name}")
            self.issues.append(
                StyleIssue(
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Missing docstring in public class: {node.name}",
                )
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Visit name"""

        if isinstance(node.ctx, ast.Store):
            self.total_checks.append(f"variable_naming_{node.id}")
            if (
                not self._is_snake_case(node.id)
                and not node.id.isupper()
                and not node.id.startswith("_")
            ):
                self.issues.append(
                    StyleIssue(
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Variable name should be lowercase with underscores: {node.id}",
                    )
                )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import"""

        for alias in node.names:
            self.total_checks.append(f"import_{alias.name}")
            if alias.name == "*":
                self.issues.append(
                    StyleIssue(
                        line=node.lineno,
                        column=node.col_offset,
                        message="Wildcard import should be avoided",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from statement"""

        for alias in node.names:
            self.total_checks.append(f"from_import_{alias.name}")
            if alias.name == "*":
                self.issues.append(
                    StyleIssue(
                        line=node.lineno,
                        column=node.col_offset,
                        message="Wildcard import should be avoided",
                    )
                )
        self.generic_visit(node)

    def _is_snake_case(self, name: str) -> bool:
        check: bool = re.match(r"^[a-z_][a-z0-9_]*$", name) is not None
        return check

    def _is_pascal_case(self, name: str) -> bool:
        check: bool = re.match(r"^[A-Z][a-zA-Z0-9]*$", name) is not None
        return check
