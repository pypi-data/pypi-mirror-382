import hashlib
import json
import os
import pickle
from pathlib import Path
from typing import Any

class Cache:
    def __init__(self, path: str | os.PathLike | None = None):
        self.path = Path(path or ".llm_safecall_cache.pkl")
        if not self.path.exists():
            self.path.write_bytes(pickle.dumps({}))

    def key(self, prompt: str, params: dict, output_type: Any) -> str:
        spec = {
            "prompt": prompt,
            "params": params,
            "schema": getattr(output_type, "__name__", str(output_type)),
        }
        return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()

    def get(self, key: str):
        data = pickle.loads(self.path.read_bytes())
        return data.get(key)

    def set(self, key: str, value: Any) -> None:
        data = pickle.loads(self.path.read_bytes())
        data[key] = value
        self.path.write_bytes(pickle.dumps(data))
