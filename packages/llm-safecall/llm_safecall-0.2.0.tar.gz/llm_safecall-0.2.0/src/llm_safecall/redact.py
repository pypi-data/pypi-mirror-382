import re
from typing import Iterable

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\s-]?){7,}")

def redact_text(text: str, fields: Iterable[str]) -> str:
    out = text
    if "email" in fields:
        out = EMAIL_RE.sub("[REDACTED_EMAIL]", out)
    if "phone" in fields:
        out = PHONE_RE.sub("[REDACTED_PHONE]", out)
    return out
