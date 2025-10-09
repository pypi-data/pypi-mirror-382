from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Iterable
from .errors import PolicyViolationError
from .secrets import scan as scan_secrets, redact_findings
from .sanitize import strip_disallowed_codeblocks, strip_disallowed_commands, remove_urls_not_in_allowlist

INJECTION_SIGNS = [
    "ignore previous instructions",
    "disregard prior instructions",
    "reveal the system prompt",
    "show hidden prompt",
    "exfiltrate",
    "send to http",
    "upload to",
    "base64 encode the following secrets",
]

@dataclass
class PolicyConfig:
    block_secrets: bool = True
    redact_secrets: bool = True
    allow_shell_output: bool = False
    outbound_url_allowlist: list[str] = field(default_factory=list)
    json_only_when_schema: bool = True
    max_output_chars: int = 10000
    max_input_chars: int = 20000
    forbid_injection_phrases: list[str] = field(default_factory=lambda: INJECTION_SIGNS)

class PolicyEngine:
    def __init__(self, cfg: PolicyConfig | None = None):
        self.cfg = cfg or PolicyConfig()

    def pre_call(self, prompt: str) -> str:
        # length check
        if len(prompt) > self.cfg.max_input_chars:
            raise PolicyViolationError("Prompt too long", {"max": self.cfg.max_input_chars})
        # injection heuristics
        lowered = prompt.lower()
        for phrase in self.cfg.forbid_injection_phrases:
            if phrase in lowered:
                raise PolicyViolationError("Prompt contains injection markers", {"phrase": phrase})
        # secrets scan
        findings = scan_secrets(prompt)
        if findings and self.cfg.block_secrets:
            if self.cfg.redact_secrets:
                prompt = redact_findings(prompt, findings)
            else:
                raise PolicyViolationError("Secrets detected in prompt", {"findings": [f.name for f in findings]})
        return prompt

    def post_call(self, text: str, schema_expected: bool) -> str:
        # size clamp
        if len(text) > self.cfg.max_output_chars:
            text = text[: self.cfg.max_output_chars] + "...[TRUNCATED]"
        # secrets scan
        findings = scan_secrets(text)
        if findings and self.cfg.block_secrets:
            if self.cfg.redact_secrets:
                text = redact_findings(text, findings)
            else:
                raise PolicyViolationError("Secrets detected in output", {"findings": [f.name for f in findings]})
        # code/command sanitization
        text = strip_disallowed_codeblocks(text, self.cfg.allow_shell_output)
        text = strip_disallowed_commands(text, self.cfg.allow_shell_output)
        # URL allowlist
        text = remove_urls_not_in_allowlist(text, self.cfg.outbound_url_allowlist)
        # JSON-only enforcement
        if schema_expected and self.cfg.json_only_when_schema:
            # A simple enforcement: ensure starts with { or [
            stripped = text.strip()
            if not (stripped.startswith("{") or stripped.startswith("[")):
                raise PolicyViolationError("Non-JSON output when JSON schema expected")
        return text
