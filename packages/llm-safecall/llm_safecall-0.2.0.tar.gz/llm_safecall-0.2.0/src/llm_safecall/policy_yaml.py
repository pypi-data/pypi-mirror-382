from __future__ import annotations
import yaml
from pathlib import Path
from .policy import PolicyConfig, PolicyEngine

def load_policy(path: str | Path) -> PolicyEngine:
    data = yaml.safe_load(Path(path).read_text())
    cfg = PolicyConfig(
        block_secrets = data.get("block_secrets", True),
        redact_secrets = data.get("redact_secrets", True),
        allow_shell_output = data.get("allow_shell_output", False),
        outbound_url_allowlist = data.get("outbound_url_allowlist", []) or [],
        json_only_when_schema = data.get("json_only_when_schema", True),
        max_output_chars = int(data.get("max_output_chars", 10000)),
        max_input_chars = int(data.get("max_input_chars", 20000)),
        forbid_injection_phrases = data.get("forbid_injection_phrases", None) or None,
    )
    return PolicyEngine(cfg)
