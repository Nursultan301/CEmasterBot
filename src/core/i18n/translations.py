from __future__ import annotations

import gettext
from functools import lru_cache
from pathlib import Path
from typing import Callable

Translator = Callable[[str], str]

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
DOMAIN = "message"
DEFAULT_LANG = "ru"


def normalize_lang(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LANG
    lang = lang.lower().strip()
    if lang.startswith("ru"):
        return "ru"
    if lang.startswith("ky") or lang.startswith("kg"):
        return "ky"
    if lang.startswith("en"):
        return "en"
    return DEFAULT_LANG


@lru_cache(maxsize=32)
def _get_gettext(lang: str) -> gettext.NullTranslations:
    """
    Возвращает compiled gettext translations (из .mo).
    fallback=True -> если перевода нет, вернёт исходную строку.
    """
    return gettext.translation(
        domain=DOMAIN,
        localedir=str(LOCALES_DIR),
        languages=[lang],
        fallback=True,
    )


def get_translator(lang: str | None) -> Translator:
    lang_norm = normalize_lang(lang)
    gt = _get_gettext(lang_norm).gettext

    def _(msgid: str) -> str:
        return gt(msgid)

    return _


def btn_variants(key: str) -> set[str]:
    return {
        get_translator("ru")(key),
        get_translator("ky")(key),
        get_translator("en")(key),
    }
