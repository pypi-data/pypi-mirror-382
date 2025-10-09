import os
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .policy import PolicyEngine, PolicyConfig
from .budget import Budget
from .rate_limit import TokenBucket
from .safe_call import SafeCall

def from_env(output=None):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    timeout_s = int(os.getenv("LLM_TIMEOUT_S", "20"))
    retries = int(os.getenv("LLM_RETRIES", "2"))
    allow_shell = os.getenv("LLM_ALLOW_SHELL", "false").lower() == "true"

    # Policy via env allowlist (comma-separated). For YAML config, use LLM_SAFE_POLICY.
    url_allow = [u for u in os.getenv("LLM_URL_ALLOWLIST", "").split(",") if u]
    policy = PolicyEngine(PolicyConfig(
        allow_shell_output=allow_shell,
        outbound_url_allowlist=url_allow,
    ))

    budget = None
    if os.getenv("LLM_BUDGET_DAILY"):
        from pathlib import Path
        daily = float(os.getenv("LLM_BUDGET_DAILY"))
        path = os.getenv("LLM_BUDGET_PATH", ".llm_safecall_budget.json")
        budget = Budget(path=Path(path), daily_limit=daily)

    rate = os.getenv("LLM_RATE_PER_SEC")
    rate_limit = TokenBucket(float(rate), float(rate)) if rate else None

    if provider == "openai":
        llm = OpenAIProvider(model=model, api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == "anthropic":
        llm = AnthropicProvider(model=model, api_key=os.getenv("ANTHROPIC_API_KEY"))
    else:
        from .providers.mock_provider import MockProvider
        llm = MockProvider(model="mock-1")

    return SafeCall(llm=llm, output=output, policy=policy, timeout_s=timeout_s, retries=retries)
