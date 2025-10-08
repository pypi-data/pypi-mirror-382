#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base analyser"""

import ast
import sys
import typing as t
from abc import ABC

__all__: t.Tuple[str, ...] = ("BaseAnalyser",)


class BaseAnalyser(ast.NodeVisitor, ABC):
    """Base class for AST analysers"""

    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content = content
        self.lines = content.splitlines()
        self.tree = None
        try:
            self.tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            err_msg: str = (
                f"SyntaxError in file '{e.filename}', line {e.lineno}, offset {e.offset}:\n"
                f"    {e.text.strip() if e.text else ''}\n"
                f"    {' ' * ((e.offset or 1) - 1)}^\n"
                f"{e.msg}"
            )
            print(err_msg, file=sys.stderr)
            sys.exit(1)
