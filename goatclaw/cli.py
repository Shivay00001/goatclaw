"""
GOATCLAW CLI
Command-line interface for the multi-agent orchestration system.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from goatclaw.runner import run_demo, run_parallel_demo
from goatclaw.worker import Worker
from goatclaw.orchestrator import Orchestrator
from goatclaw.core.structs import TaskGraph, TaskNode, AgentType, ExecutionMode
from goatclaw.init_db import init_db

CONFIG_PATHS = [
    os.path.join(os.getcwd(), ".goatclaw.json"),
    os.path.join(os.path.expanduser("~"), ".goatclaw.json"),
]


def get_config_path():
    """Get the active config file path (prefer local, else home)."""
    for p in CONFIG_PATHS:
        if os.path.exists(p):
            return p
    return CONFIG_PATHS[0]  # default: local dir


def load_config():
    """Load config from file."""
    path = get_config_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save config to file."""
    path = get_config_path()
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"[OK] Config saved to {path}")


def setup_cli_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )


async def start_worker(worker_id: str):
    print(f"[*] Starting GOATCLAW Worker: {worker_id}")
    worker = Worker(worker_id=worker_id)
    await worker.setup()
    await worker.run()


async def submit_simple_goal(goal: str, distributed: bool, provider: str = None,
                              model: str = None):
    from goatclaw.agents.planner_agent import PlannerAgent
    from goatclaw.runner import create_orchestrator, create_default_security_context

    print(f"\n{'='*60}")
    print(f"  GOATCLAW — Goal Execution")
    print(f"{'='*60}")
    print(f"  Goal: {goal}")

    # Build config with model settings
    config = {"distributed": distributed}

    # Resolve provider/model from CLI args > config file > auto-detect
    file_config = load_config()
    effective_provider = provider or file_config.get("model", {}).get("provider", "")
    effective_model = model or file_config.get("model", {}).get("name", "")

    if effective_provider or effective_model:
        model_cfg = {}
        if effective_provider:
            model_cfg["provider"] = effective_provider
        if effective_model:
            model_cfg["name"] = effective_model
        config["model"] = model_cfg

        # Pass model config to all agents
        for agent_key in ["research", "code", "devops", "api", "data_processing", "filesystem"]:
            config[agent_key] = {"model": model_cfg}

    if effective_provider:
        print(f"  Provider: {effective_provider}")
    if effective_model:
        print(f"  Model: {effective_model}")
    print(f"{'='*60}\n")

    # Create orchestrator with model config
    orch = create_orchestrator(config)
    planner = PlannerAgent(orch.event_bus, config.get("research"))

    await orch.start()

    try:
        sec_ctx = create_default_security_context()

        # 1. Plan the goal
        print("[*] Planning task graph...")
        graph = await planner.plan(goal, sec_ctx)

        if distributed:
            graph.execution_mode = ExecutionMode.DISTRIBUTED

        # 2. Execute the plan
        print(f"[*] Executing {len(graph.nodes)} planned nodes...")
        result = await orch.process_goal(graph, sec_ctx)

        print(f"\n{'='*60}")
        print("  EXECUTION RESULTS")
        print(f"{'='*60}")
        print(f"  Status:          {result['status'].upper()}")
        print(f"  Completed:       {len(result['completed_nodes'])}/{result['total_nodes']}")
        print(f"  Time:            {result['execution_time_seconds']:.2f}s")

        if result.get("errors"):
            print(f"\n  [!] Errors:")
            for err in result["errors"]:
                print(f"    - {err['node_id']}: {err['error']}")

        # Show execution log
        print(f"\n  Node Details:")
        for log in result.get("execution_log", []):
            icon = "[OK]" if log["status"] == "success" else "[FAIL]"
            dur = f"{log.get('duration_ms', 0):.0f}ms" if log.get("duration_ms") else "-"
            print(f"    {icon} {log['node_id']:20s} {log['agent_type']:18s} ({dur})")

        print(f"{'='*60}\n")

    finally:
        await orch.stop()


def handle_config(args):
    """Handle config subcommands."""
    if args.config_action == "show":
        config = load_config()
        if not config:
            print("[INFO] No config file found. Using defaults (auto-detect Ollama).")
            print(f"  Config locations checked:")
            for p in CONFIG_PATHS:
                print(f"    - {p}")
        else:
            print(f"[CONFIG] {get_config_path()}")
            print(json.dumps(config, indent=2))

    elif args.config_action == "set-provider":
        config = load_config()
        config.setdefault("model", {})["provider"] = args.provider
        if args.model_name:
            config["model"]["name"] = args.model_name
        save_config(config)
        print(f"[OK] Provider set to: {args.provider}")

    elif args.config_action == "set-key":
        config = load_config()
        config.setdefault("api_keys", {})[args.provider] = args.key
        save_config(config)
        print(f"[OK] API key stored for: {args.provider}")
        print(f"  (Alternatively, set env var: {args.provider.upper()}_API_KEY)")

    elif args.config_action == "set-model":
        config = load_config()
        config.setdefault("model", {})["name"] = args.model_name
        save_config(config)
        print(f"[OK] Model set to: {args.model_name}")

    elif args.config_action == "detect":
        from goatclaw.agents.base_agent import BaseAgent
        print("[*] Detecting available LLM providers...\n")

        # Check Ollama
        if BaseAgent._detect_ollama():
            print("  [FOUND] Ollama (local) — http://localhost:11434")
            try:
                import urllib.request, json as jn
                req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = jn.loads(resp.read())
                    models = [m.get("name", "?") for m in data.get("models", [])]
                    print(f"           Models: {', '.join(models) if models else 'none pulled'}")
            except Exception:
                pass
        else:
            print("  [MISS] Ollama — not running")

        # Check env vars
        for provider, env_var in [
            ("openai", "OPENAI_API_KEY"),
            ("anthropic", "ANTHROPIC_API_KEY"),
            ("deepseek", "DEEPSEEK_API_KEY"),
            ("groq", "GROQ_API_KEY"),
        ]:
            key = os.getenv(env_var)
            if key:
                masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                print(f"  [FOUND] {provider:12s} — env:{env_var} ({masked})")
            else:
                print(f"  [MISS]  {provider:12s} — env:{env_var} not set")

        # Check config file
        config = load_config()
        if config.get("api_keys"):
            print(f"\n  Config file keys ({get_config_path()}):")
            for p, k in config["api_keys"].items():
                masked = k[:8] + "..." + k[-4:] if len(k) > 12 else "***"
                print(f"    [FOUND] {p}: {masked}")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="GOATCLAW — Multi-Agent Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  goatclaw demo                              Run the demo pipeline
  goatclaw run "Summarize Python async"      Execute a goal
  goatclaw run "Build a REST API" --provider ollama --model llama3
  goatclaw config detect                     Detect available LLM providers
  goatclaw config set-key openai sk-xxx      Store API key
  goatclaw config set-provider ollama        Set default provider
        """
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Demo
    demo_parser = subparsers.add_parser("demo", help="Run the core system demo")
    demo_parser.add_argument("--parallel", action="store_true", help="Parallel execution demo")

    # Run Goal
    goal_parser = subparsers.add_parser("run", help="Execute a goal")
    goal_parser.add_argument("goal", type=str, help="The goal to achieve")
    goal_parser.add_argument("--distributed", action="store_true", help="Distributed mode")
    goal_parser.add_argument("--provider", "-p", type=str, default=None,
                             help="LLM provider (ollama, openai, anthropic, deepseek, groq)")
    goal_parser.add_argument("--model", "-m", type=str, default=None,
                             help="Model name (e.g., llama3, gpt-4, claude-sonnet-4-20250514)")

    # Worker
    worker_parser = subparsers.add_parser("worker", help="Start a distributed worker")
    worker_parser.add_argument("--id", type=str, default=None, help="Worker ID")

    # Chaos
    subparsers.add_parser("chaos", help="Run resilience chaos testing")

    # Init DB
    subparsers.add_parser("init", help="Initialize the database")

    # Config
    config_parser = subparsers.add_parser("config", help="Configure GOATCLAW")
    config_sub = config_parser.add_subparsers(dest="config_action")

    config_sub.add_parser("show", help="Show current configuration")
    config_sub.add_parser("detect", help="Detect available LLM providers")

    set_provider = config_sub.add_parser("set-provider", help="Set default LLM provider")
    set_provider.add_argument("provider", type=str, help="Provider name")
    set_provider.add_argument("--model-name", type=str, default=None, help="Model name")

    set_model = config_sub.add_parser("set-model", help="Set default model")
    set_model.add_argument("model_name", type=str, help="Model name")

    set_key = config_sub.add_parser("set-key", help="Store an API key")
    set_key.add_argument("provider", type=str, help="Provider (openai, anthropic, etc.)")
    set_key.add_argument("key", type=str, help="API key value")

    # Interactive terminal (start)
    subparsers.add_parser("start", help="Launch interactive terminal (default)")

    args = parser.parse_args()

    # Only set up heavy logging for non-interactive commands
    if args.command and args.command not in ("start", None):
        setup_cli_logging(args.verbose if hasattr(args, 'verbose') and args.verbose else False)

    if args.command == "demo":
        setup_cli_logging(args.verbose)
        if args.parallel:
            asyncio.run(run_parallel_demo())
        else:
            asyncio.run(run_demo())

    elif args.command == "worker":
        setup_cli_logging(args.verbose)
        asyncio.run(start_worker(args.id))

    elif args.command == "chaos":
        from chaos_runner import ChaosRunner
        runner = ChaosRunner()
        asyncio.run(runner.start())

    elif args.command == "run":
        setup_cli_logging(args.verbose)
        asyncio.run(submit_simple_goal(
            args.goal, args.distributed,
            provider=args.provider, model=args.model
        ))

    elif args.command == "init":
        asyncio.run(init_db())

    elif args.command == "config":
        if not args.config_action:
            config_parser.print_help()
        else:
            handle_config(args)

    elif args.command == "start" or args.command is None:
        # Default: launch interactive terminal
        from goatclaw.terminal import run_interactive
        run_interactive()


if __name__ == "__main__":
    main()

