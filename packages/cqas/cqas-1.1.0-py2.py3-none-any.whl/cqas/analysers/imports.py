#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imports analyser"""

import ast
import typing as t

from cqas.constructs.imports import FromImportEntry, ImportAnalysisResult, ImportEntry

from .base import BaseAnalyser

__all__: t.Tuple[str, ...] = ("ImportAnalyser",)


class ImportAnalyser(BaseAnalyser):
    """Analyse imports and dependencies"""

    STD_LIB_MODULES: t.Final[t.FrozenSet[str]] = frozenset(
        {
            "os",
            "sys",
            "json",
            "math",
            "random",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "operator",
            "pathlib",
            "subprocess",
            "threading",
            "multiprocessing",
            "asyncio",
            "re",
            "hashlib",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "sqlite3",
            "logging",
            "argparse",
            "configparser",
            "tempfile",
            "shutil",
        }
    )

    THIRD_PARTY_INDICATORS: t.Final[t.FrozenSet[str]] = frozenset(
        {
            "requests",
            "numpy",
            "pandas",
            "flask",
            "django",
            "sqlalchemy",
            "pytest",
            "click",
            "jinja2",
            "werkzeug",
            "urllib3",
            "certifi",
            "chardet",
            "idna",
            "six",
            "setuptools",
            "pip",
        }
    )

    def __init__(self, file_path: str, content: str) -> None:
        super().__init__(file_path, content)
        self.imports: t.List[ImportEntry] = []
        self.from_imports: t.List[FromImportEntry] = []
        self.circular_dependencies: t.List[t.Tuple[str, str]] = []  # (moduleA, moduleB)

    def analyse(self) -> ImportAnalysisResult:
        """Analyse import structure"""

        if self.tree:
            self.visit(self.tree)

        all_modules: t.List[str] = [imp.module for imp in self.imports] + [
            imp.module for imp in self.from_imports
        ]
        total_imports: int = len(self.imports) + len(self.from_imports)
        unique_modules: int = len(set(all_modules))
        stdlib_imports: int = self._count_stdlib_imports(all_modules)
        third_party_imports: int = self._count_third_party_imports(all_modules)
        local_imports: int = self._count_local_imports()

        import_graph: t.Dict[str, t.Set[str]] = {}
        current_module: str = self.file_path.rsplit("/", 1)[-1].replace(".py", "")

        imported_modules: t.Set[str] = set()
        for imp in self.imports:
            if imp.module:
                imported_modules.add(imp.module.split(".")[0])
        for fimp in self.from_imports:
            if fimp.level == 0 and fimp.module:
                imported_modules.add(fimp.module.split(".")[0])
        import_graph[current_module] = imported_modules

        # Detect self-import as circular dependency
        if current_module in imported_modules:
            self.circular_dependencies.append((current_module, current_module))

        return ImportAnalysisResult(
            imports=self.imports,
            from_imports=self.from_imports,
            total_imports=total_imports,
            unique_modules=unique_modules,
            stdlib_imports=stdlib_imports,
            third_party_imports=third_party_imports,
            local_imports=local_imports,
            circular_dependencies=self.circular_dependencies,
        )

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements"""
        for alias in node.names:
            self.imports.append(
                ImportEntry(
                    module=alias.name,
                    alias=alias.asname,
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from import statements"""
        if node.module:
            for alias in node.names:
                self.from_imports.append(
                    FromImportEntry(
                        module=node.module,
                        name=alias.name,
                        alias=alias.asname,
                        line=node.lineno,
                        level=node.level,
                    )
                )
        self.generic_visit(node)

    def _count_stdlib_imports(self, modules: t.List[str]) -> int:
        """Count standard library imports"""
        count: int = 0
        for module in modules:
            root_module: str = module.split(".")[0]
            if root_module in self.STD_LIB_MODULES:
                count += 1
        return count

    def _count_third_party_imports(self, modules: t.List[str]) -> int:
        """Count third-party imports"""
        count: int = 0
        for module in modules:
            root_module: str = module.split(".")[0]
            if root_module in self.THIRD_PARTY_INDICATORS:
                count += 1
        return count

    def _count_local_imports(self) -> int:
        """Count local/relative imports"""
        count: int = 0
        for imp in self.from_imports:
            if imp.level > 0:
                count += 1
        return count
