import uuid


def new_call_id() -> str:
    return f"call_{uuid.uuid4().hex}"
