#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Language strings"""

# pylint: disable=W0603

import typing as t

from . import en, lt

__all__: t.Tuple[str, ...] = (
    "s",
    "set_language",
    "LANGS",
)

LANGS: t.Final[t.Dict[str, t.Any]] = {
    "en": en.STRINGS,
    "lt": lt.STRINGS,
}

g_lang: str = "en"


def set_language(lang: str) -> None:
    """Set language"""
    global g_lang
    lang = lang.lower()
    if lang in LANGS:
        g_lang = lang


def s(name: str, *args: t.Any) -> str:
    """Translate and template a string"""

    if g_lang in LANGS and name in LANGS[g_lang]:
        template: str = LANGS[g_lang][name]
    else:
        template = en.STRINGS.get(name, name)

    if args:
        try:
            return template % args
        except (TypeError, ValueError):
            return template

    return template
