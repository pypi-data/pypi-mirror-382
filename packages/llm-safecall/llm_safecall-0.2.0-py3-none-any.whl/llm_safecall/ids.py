import uuid, time

def new_call_id() -> str:
    return f"call_{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
