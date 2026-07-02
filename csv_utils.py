"""Shared CSV writing helpers."""

FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(value) -> str:
    """Prefix values that spreadsheet apps would interpret as formulas."""
    s = "" if value is None else str(value)
    return "'" + s if s.startswith(FORMULA_TRIGGERS) else s
