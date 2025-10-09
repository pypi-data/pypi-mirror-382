from .errors import ModerationError

BANNED = {"bomb", "dox", "credit card number"}

def check_input(text: str) -> None:
    lowered = text.lower()
    if any(b in lowered for b in BANNED):
        raise ModerationError("Input violated moderation rules.")

def check_output(text: str) -> None:
    lowered = text.lower()
    if any(b in lowered for b in BANNED):
        raise ModerationError("Output violated moderation rules.")
