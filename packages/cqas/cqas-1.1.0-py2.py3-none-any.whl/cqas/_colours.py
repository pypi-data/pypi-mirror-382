#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Colours"""

import typing as t

try:
    import colorama  # type: ignore
    from colorama import Back, Fore, Style  # type: ignore

    colorama.init(autoreset=True)
    COLOURS_AVAILABLE: bool = True  # type: ignore
except ImportError:
    COLOURS_AVAILABLE = False  # type: ignore

    class Fore:  # type: ignore
        """Foregound colours"""

        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""

    class Style:  # type: ignore
        """Style modifiers"""

        BRIGHT = DIM = RESET_ALL = ""

    class Back:  # type: ignore
        """Background colours"""

        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""


__all__: t.Tuple[str, ...] = ("Fore", "Style", "Back")
