from __future__ import annotations
import argparse, sys, json
from pydantic import BaseModel, create_model
from .env import from_env
from .policy_yaml import load_policy

def main(argv=None):
    argv = argv or sys.argv[1:]
    p = argparse.ArgumentParser(prog="llm-safecall", description="Safe LLM caller")
    p.add_argument("--prompt", "-p", required=True, help="Prompt text")
    p.add_argument("--policy", help="Path to policy.yml (optional)")
    p.add_argument("--schema", help="JSON schema fields as comma list, e.g. key:str,value:int")
    p.add_argument("--fail-safe", action="store_true", help="Enable fail-safe mode (never raise)")
    args = p.parse_args(argv)

    output_model = None
    if args.schema:
        fields = {}
        for part in args.schema.split(","):
            if not part.strip():
                continue
            name, typ = [x.strip() for x in part.split(":")]
            py = {"str": (str, ...), "int": (int, ...), "float": (float, ...)}.get(typ, (str, ...))
            fields[name] = py
        output_model = create_model("CliSchema", **fields)  # type: ignore

    safe = from_env(output=output_model)
    if args.policy:
        policy = load_policy(args.policy)
        safe.policy = policy
    if args.fail_safe:
        safe.fail_safe = True
        safe.fail_safe_return = ""

    res = safe.generate(args.prompt)
    if hasattr(res, "model_dump"):
        print(json.dumps(res.model_dump(), indent=2))
    else:
        print(str(res))

if __name__ == "__main__":
    main()
