from __future__ import annotations
from typing import Callable, Any, Dict, Type
from pydantic import BaseModel, ValidationError
from .policy import PolicyEngine

class ToolRunner:
    """Run tools with input/output schemas and policy checks.
    Use this for agent tool-calls to ensure arguments and results pass org policy."""
    def __init__(self, policy: PolicyEngine):
        self.policy = policy
        self._registry: Dict[str, tuple[Callable[..., Any], Type[BaseModel] | None, Type[BaseModel] | None]] = {}

    def register(self, name: str, fn: Callable[..., Any], args_schema: Type[BaseModel] | None = None, result_schema: Type[BaseModel] | None = None):
        self._registry[name] = (fn, args_schema, result_schema)

    def call(self, name: str, **kwargs) -> Any:
        if name not in self._registry:
            raise KeyError(f"Tool not found: {name}")
        fn, args_schema, result_schema = self._registry[name]

        # Validate args
        if args_schema:
            try:
                validated = args_schema(**kwargs)
            except ValidationError as e:
                raise ValueError(f"Invalid tool args for {name}: {e}") from e
            args = validated.model_dump()
        else:
            args = kwargs

        # Policy check on textual args
        for k, v in list(args.items()):
            if isinstance(v, str):
                args[k] = self.policy.pre_call(v)

        out = fn(**args)

        # Policy check and validation on result
        if isinstance(out, str):
            out = self.policy.post_call(out, schema_expected=bool(result_schema))

        if result_schema:
            out = result_schema.model_validate(out)

        return out
