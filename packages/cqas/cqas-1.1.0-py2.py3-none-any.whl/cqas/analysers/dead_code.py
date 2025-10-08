#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dead code analyser"""

import ast
import typing as t

from cqas.constructs.classification import Confidence, ElementType
from cqas.constructs.dead_code import DeadCodeInfo

from .base import BaseAnalyser

__all__: t.Tuple[str, ...] = ("DeadCodeAnalyser",)


class DeadCodeAnalyser(BaseAnalyser):
    """Dead code detection"""

    SPECIAL_METHODS: t.Final[t.FrozenSet[str]] = frozenset(
        {
            "__init__",
            "__str__",
            "__repr__",
            "__len__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__iter__",
            "__next__",
            "__enter__",
            "__exit__",
            "__call__",
            "__eq__",
            "__ne__",
            "__lt__",
            "__le__",
            "__gt__",
            "__ge__",
            "__hash__",
            "__bool__",
            "__add__",
            "__sub__",
            "__mul__",
            "__truediv__",
            "__floordiv__",
            "__mod__",
            "__pow__",
            "__and__",
            "__or__",
            "__xor__",
            "__lshift__",
            "__rshift__",
            "__contains__",
            "__missing__",
            "__getattr__",
            "__setattr__",
            "__delattr__",
            "__dir__",
            "__get__",
            "__set__",
            "__delete__",
            "__slots__",
            "__dict__",
            "__weakref__",
            "__doc__",
            "__module__",
            "__qualname__",
            "__annotations__",
        }
    )

    def __init__(self, file_path: str, content: str):
        super().__init__(file_path, content)
        self.defined_functions: t.Dict[str, int] = {}
        self.defined_classes: t.Dict[str, int] = {}
        self.defined_variables: t.Dict[str, int] = {}
        self.imported_modules: t.Dict[str, int] = {}
        self.used_names: t.Set[str] = set()
        self.function_calls: t.Set[str] = set()
        self.attribute_access: t.Set[str] = set()
        self.string_literals: t.Set[str] = set()
        self.decorators: t.Set[str] = set()

    def visit_FunctionDef(
        self, node: t.Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> None:
        """Visit function definitions"""

        # Don't mark special methods, test functions, or entry points as dead
        if (
            not node.name.startswith("_")
            or node.name in self.SPECIAL_METHODS
            or node.name.startswith("test_")
            or node.name == "main"
        ):
            self.defined_functions[node.name] = node.lineno

        # Check for decorators that might make functions callable externally
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                self.decorators.add(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                self.decorators.add(decorator.attr)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions"""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions"""
        self.defined_classes[node.name] = node.lineno
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignments with variable tracking"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Track module-level constants and variables
                if not target.id.startswith("_"):
                    self.defined_variables[target.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Visit name usage"""
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls"""
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.function_calls.add(node.func.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute access"""
        self.attribute_access.add(node.attr)
        self.used_names.add(node.attr)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements"""
        for alias in node.names:
            import_name = alias.asname if alias.asname else alias.name
            self.imported_modules[import_name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from imports"""
        if node.module:
            self.imported_modules[node.module] = node.lineno
        for alias in node.names:
            import_name = alias.asname if alias.asname else alias.name
            self.imported_modules[import_name] = node.lineno
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Visit string constants (might reference names)"""
        if isinstance(node.value, str) and len(node.value) < 100:
            self.string_literals.add(node.value)
        self.generic_visit(node)

    def find_dead_code(self) -> t.List[DeadCodeInfo]:
        """Find potentially dead code"""

        dead_code: t.List[DeadCodeInfo] = []

        # Check for unused functions
        for func_name, line_no in self.defined_functions.items():
            if (
                func_name not in self.used_names
                and func_name not in self.function_calls
            ):

                # Check if function name appears in string literals (dynamic calls)
                found_in_strings: bool = any(
                    func_name in literal for literal in self.string_literals
                )

                # Check if function has decorators that might expose it
                is_decorated: bool = func_name in self.decorators

                if not found_in_strings and not is_decorated:
                    dead_code.append(
                        DeadCodeInfo(
                            line_number=line_no,
                            element_type=ElementType.FUNCTION,
                            element_name=func_name,
                            reason="Function is defined but never called",
                            confidence=(
                                Confidence.HIGH
                                if func_name not in self.attribute_access
                                else Confidence.MEDIUM
                            ),
                        )
                    )

        # Check for unused classes
        for class_name, line_no in self.defined_classes.items():
            if class_name not in self.used_names:
                found_in_strings = any(
                    class_name in literal for literal in self.string_literals
                )
                if not found_in_strings:
                    dead_code.append(
                        DeadCodeInfo(
                            line_number=line_no,
                            element_type=ElementType.CLASS,
                            element_name=class_name,
                            reason="Class is defined but never instantiated or referenced",
                            confidence=Confidence.HIGH,
                        )
                    )

        # Check for unused imports
        for import_name, line_no in self.imported_modules.items():
            if (
                import_name not in self.used_names
                and import_name not in self.function_calls
                and import_name not in self.attribute_access
            ):

                dead_code.append(
                    DeadCodeInfo(
                        line_number=line_no,
                        element_type=ElementType.IMPORT,
                        element_name=import_name,
                        reason="Module imported but never used",
                        confidence=Confidence.HIGH,
                    )
                )

        # Check for unused variables
        for var_name, line_no in self.defined_variables.items():
            if (
                var_name not in self.used_names
                and var_name.islower()  # Only variables
                and len(var_name) > 2  # Avoid single letter vars
            ):
                dead_code.append(
                    DeadCodeInfo(
                        line_number=line_no,
                        element_type=ElementType.VARIABLE,
                        element_name=var_name,
                        reason="Variable is defined but never used",
                        confidence=Confidence.MEDIUM,
                    )
                )

        return dead_code
