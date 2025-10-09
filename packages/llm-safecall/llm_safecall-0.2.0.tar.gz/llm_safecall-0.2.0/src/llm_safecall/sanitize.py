import re
from typing import Iterable

URL_RE = re.compile(r"https?://[\w\-\.]+(?:/[\w\-\./%?#=&]*)?")

BASH_CODEBLOCK_RE = re.compile(r"```(?:bash|sh|zsh|powershell|cmd)[\s\S]*?```", re.IGNORECASE)
SHELL_COMMAND_RE = re.compile(r"\b(rm\s+-rf|curl\s+|wget\s+|Invoke-WebRequest|powershell\s+-)\b", re.IGNORECASE)

def strip_disallowed_codeblocks(text: str, allow_shell: bool) -> str:
    if allow_shell:
        return text
    return BASH_CODEBLOCK_RE.sub("[REDACTED_SHELL_BLOCK]", text)

def strip_disallowed_commands(text: str, allow_shell: bool) -> str:
    if allow_shell:
        return text
    return SHELL_COMMAND_RE.sub("[REDACTED_SHELL_CMD]", text)

def extract_urls(text: str) -> list[str]:
    return URL_RE.findall(text)

def remove_urls_not_in_allowlist(text: str, allowlist: list[str]) -> str:
    if not allowlist:
        return text
    def allowed(url: str) -> bool:
        return any(url.startswith(prefix) for prefix in allowlist)
    out = text
    for url in set(extract_urls(text)):
        if not allowed(url):
            out = out.replace(url, "[BLOCKED_URL]")
    return out
