from __future__ import annotations
import unicodedata


def normalize_sanskrit(raw: str) -> str:
    """Canonical derived representation; never mutate or replace the raw source."""
    return unicodedata.normalize("NFC", raw)
