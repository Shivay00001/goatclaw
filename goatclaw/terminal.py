"""
GOATCLAW Interactive Terminal
Interactive shell for goal execution with smart LLM provider detection.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Optional, Dict, Tuple


logger = logging.getLogger("goatclaw.terminal")

# ANSI colors
class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


BANNER = f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════╗
║               G O A T C L A W                    ║
║         Multi-Agent Task Orchestrator            ║
╚══════════════════════════════════════════════════╝{C.RESET}
"""

CONFIG_PATH_LOCAL = os.path.join(os.getcwd(), ".goatclaw.json")
CONFIG_PATH_HOME = os.path.join(os.path.expanduser("~"), ".goatclaw.json")


def _load_config() -> Dict:
    for p in [CONFIG_PATH_LOCAL, CONFIG_PATH_HOME]:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def _save_config(config: Dict):
    path = CONFIG_PATH_LOCAL
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def _check_ollama() -> Tuple[bool, list]:
    """Check if Ollama is running and return available models."""
    import urllib.request
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                data = json.loads(resp.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                return True, models
    except Exception:
        pass
    return False, []


def _check_api_keys() -> Dict[str, str]:
    """Check for available API keys from env and config."""
    found = {}

    # Environment variables
    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    for provider, env_var in env_map.items():
        key = os.getenv(env_var)
        if key:
            found[provider] = key

    # Config file
    config = _load_config()
    for provider, key in config.get("api_keys", {}).items():
        if key and provider not in found:
            found[provider] = key

    return found


def _mask_key(key: str) -> str:
    if len(key) > 12:
        return key[:6] + "..." + key[-4:]
    return "***"


def _print_status(label: str, value: str, ok: bool = True):
    icon = f"{C.GREEN}●{C.RESET}" if ok else f"{C.RED}○{C.RESET}"
    print(f"  {icon} {label:20s} {value}")


def _setup_provider() -> Optional[Dict]:
    """
    Interactive provider setup flow:
    1. Check for existing API keys
    2. Check for Ollama
    3. If nothing found, prompt user
    
    Returns model config dict or None if user quits.
    """
    print(f"\n{C.BOLD}[System Check]{C.RESET} Detecting LLM providers...\n")

    # Check API keys
    api_keys = _check_api_keys()
    for provider, key in api_keys.items():
        _print_status(provider.capitalize(), f"API key found ({_mask_key(key)})", ok=True)

    # Check Ollama
    ollama_running, ollama_models = _check_ollama()

    if ollama_running:
        _print_status("Ollama (local)", f"Running — {len(ollama_models)} model(s)", ok=True)
        if ollama_models:
            print(f"  {C.DIM}  Models: {', '.join(ollama_models)}{C.RESET}")
    else:
        _print_status("Ollama (local)", "Not running", ok=False)

    print()

    # If we have something, let user pick
    if api_keys or (ollama_running and ollama_models):
        return _pick_provider(api_keys, ollama_running, ollama_models)

    # Nothing found — guide user
    print(f"{C.YELLOW}No LLM provider detected.{C.RESET} You need at least one:\n")
    print(f"  {C.BOLD}Option 1:{C.RESET} Enter a cloud API key (OpenAI, Anthropic, etc.)")
    print(f"  {C.BOLD}Option 2:{C.RESET} Start Ollama for local models\n")

    while True:
        choice = input(f"{C.CYAN}Choose [1=API Key / 2=Ollama / q=Quit]: {C.RESET}").strip().lower()

        if choice == "1" or choice == "api":
            return _prompt_api_key()
        elif choice == "2" or choice == "ollama":
            return _guide_ollama()
        elif choice in ("q", "quit", "exit"):
            return None
        else:
            print(f"  {C.DIM}Enter 1, 2, or q{C.RESET}")


def _pick_provider(api_keys: Dict, ollama_running: bool, ollama_models: list) -> Optional[Dict]:
    """Let user pick from available providers."""
    options = []

    if ollama_running and ollama_models:
        for model in ollama_models:
            options.append(("ollama", model))

    for provider in api_keys:
        defaults = {
            "openai": "gpt-4",
            "anthropic": "claude-sonnet-4-20250514",
            "deepseek": "deepseek-chat",
            "groq": "llama-3.1-8b-instant",
        }
        options.append((provider, defaults.get(provider, "default")))

    if len(options) == 1:
        # Auto-select the only option
        provider, model = options[0]
        print(f"  {C.GREEN}Auto-selected:{C.RESET} {provider} / {model}")
        return {"provider": provider, "name": model}

    print(f"  {C.BOLD}Available providers:{C.RESET}")
    for i, (provider, model) in enumerate(options, 1):
        tag = "(local)" if provider == "ollama" else "(cloud)"
        print(f"    {C.CYAN}{i}{C.RESET}. {provider:12s} {model:30s} {C.DIM}{tag}{C.RESET}")

    while True:
        choice = input(f"\n  {C.CYAN}Select provider [1-{len(options)}]: {C.RESET}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            provider, model = options[int(choice) - 1]
            return {"provider": provider, "name": model}
        print(f"  {C.DIM}Enter a number 1-{len(options)}{C.RESET}")


def _prompt_api_key() -> Optional[Dict]:
    """Prompt user to enter an API key."""
    print(f"\n  {C.BOLD}Supported providers:{C.RESET}")
    providers = [
        ("openai", "OPENAI_API_KEY", "gpt-4"),
        ("anthropic", "ANTHROPIC_API_KEY", "claude-sonnet-4-20250514"),
        ("deepseek", "DEEPSEEK_API_KEY", "deepseek-chat"),
        ("groq", "GROQ_API_KEY", "llama-3.1-8b-instant"),
    ]
    for i, (name, env, _) in enumerate(providers, 1):
        print(f"    {C.CYAN}{i}{C.RESET}. {name:12s} (env: {env})")

    while True:
        choice = input(f"\n  {C.CYAN}Select provider [1-{len(providers)}]: {C.RESET}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(providers):
            break
        print(f"  {C.DIM}Enter a number{C.RESET}")

    provider, env_var, default_model = providers[int(choice) - 1]

    key = input(f"  {C.CYAN}Enter {provider} API key: {C.RESET}").strip()
    if not key:
        print(f"  {C.RED}No key entered.{C.RESET}")
        return None

    # Save to config
    config = _load_config()
    config.setdefault("api_keys", {})[provider] = key
    config.setdefault("model", {})["provider"] = provider
    config["model"]["name"] = default_model
    _save_config(config)

    print(f"  {C.GREEN}✓{C.RESET} Key saved to .goatclaw.json")
    print(f"  {C.DIM}(You can also set env: {env_var}={key[:8]}...){C.RESET}")

    return {"provider": provider, "name": default_model}


def _guide_ollama() -> Optional[Dict]:
    """Guide user to start Ollama."""
    print(f"""
  {C.BOLD}To use Ollama (free, local, private):{C.RESET}

  {C.CYAN}1.{C.RESET} Install Ollama:  {C.BOLD}https://ollama.com{C.RESET}
  {C.CYAN}2.{C.RESET} Start the server: {C.BOLD}ollama serve{C.RESET}
  {C.CYAN}3.{C.RESET} Pull a model:     {C.BOLD}ollama pull qwen2:0.5b{C.RESET}  (small, fast)
     {C.DIM}or:               ollama pull llama3.2   (better, needs 13GB RAM){C.RESET}
""")

    print(f"  {C.YELLOW}Waiting for Ollama to start...{C.RESET}")
    print(f"  {C.DIM}(Start 'ollama serve' in another terminal, then come back here){C.RESET}")
    print(f"  {C.DIM}Press Ctrl+C to cancel{C.RESET}\n")

    try:
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while True:
            running, models = _check_ollama()
            if running:
                print(f"\r  {C.GREEN}✓ Ollama detected!{C.RESET}                    ")
                if models:
                    print(f"    Models: {', '.join(models)}")
                    # Pick first available
                    model = models[0]
                    print(f"  {C.GREEN}Using: {model}{C.RESET}")
                    return {"provider": "ollama", "name": model}
                else:
                    print(f"\n  {C.YELLOW}No models found.{C.RESET} Pull one:")
                    print(f"    {C.BOLD}ollama pull qwen2:0.5b{C.RESET}")
                    input(f"\n  {C.CYAN}Press Enter after pulling a model...{C.RESET}")
                    _, models = _check_ollama()
                    if models:
                        return {"provider": "ollama", "name": models[0]}
                    print(f"  {C.RED}Still no models. Exiting.{C.RESET}")
                    return None
            
            sys.stdout.write(f"\r  {spinner[i % len(spinner)]} Checking Ollama... ")
            sys.stdout.flush()
            i += 1
            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n  {C.DIM}Cancelled.{C.RESET}")
        return None


async def interactive_loop(model_config: Dict):
    """Main interactive execution loop."""
    from goatclaw.runner import create_orchestrator, create_default_security_context
    from goatclaw.agents.planner_agent import PlannerAgent
    from goatclaw.core.structs import ExecutionMode

    provider = model_config["provider"]
    model_name = model_config["name"]

    # Build orchestrator config
    config = {"model": model_config}
    for k in ["research", "code", "devops", "api", "data_processing", "filesystem"]:
        config[k] = {"model": model_config}

    orch = create_orchestrator(config)
    planner = PlannerAgent(orch.event_bus, config.get("research"))
    sec_ctx = create_default_security_context()

    # Start orchestrator
    await orch.start()

    tag = f"{C.DIM}({provider}/{model_name}){C.RESET}"
    print(f"\n{C.GREEN}{C.BOLD}  ✓ System Ready{C.RESET} {tag}")
    print(f"  {C.DIM}Type a goal to execute, or 'help' for commands.{C.RESET}")
    print(f"  {C.DIM}Type 'quit' or Ctrl+C to exit.{C.RESET}\n")

    try:
        while True:
            try:
                goal = input(f"{C.CYAN}{C.BOLD}goatclaw ▸ {C.RESET}").strip()
            except EOFError:
                break

            if not goal:
                continue

            cmd = goal.lower()

            if cmd in ("quit", "exit", "q"):
                break

            elif cmd == "help":
                print(f"""
  {C.BOLD}Commands:{C.RESET}
    {C.CYAN}help{C.RESET}          Show this help
    {C.CYAN}status{C.RESET}        Show system status
    {C.CYAN}provider{C.RESET}      Switch LLM provider
    {C.CYAN}quit{C.RESET}          Exit goatclaw

  {C.BOLD}Usage:{C.RESET}
    Just type any goal and press Enter:
    {C.DIM}goatclaw ▸ Write a Python script to sort a list
    goatclaw ▸ Research best practices for REST API design
    goatclaw ▸ Analyze the differences between React and Vue{C.RESET}
""")
                continue

            elif cmd == "status":
                health = orch.get_health()
                print(f"\n  {C.BOLD}System Status{C.RESET}")
                print(f"  Provider:  {provider} / {model_name}")
                print(f"  Uptime:    {health.uptime_seconds:.0f}s")
                print(f"  Agents:    {health.active_agents}")
                print(f"  Tasks run: {health.total_tasks_executed}")
                if provider == "ollama":
                    running, models = _check_ollama()
                    status = f"{C.GREEN}Running{C.RESET}" if running else f"{C.RED}Stopped{C.RESET}"
                    print(f"  Ollama:    {status}")
                print()
                continue

            elif cmd == "provider":
                new_cfg = _setup_provider()
                if new_cfg:
                    model_config = new_cfg
                    provider = new_cfg["provider"]
                    model_name = new_cfg["name"]
                    # Update all agents
                    for agent in orch.agents.values():
                        agent.config["model"] = new_cfg
                    print(f"  {C.GREEN}✓ Switched to {provider}/{model_name}{C.RESET}\n")
                continue

            # Execute goal
            print(f"\n  {C.BOLD}Planning...{C.RESET}", end="", flush=True)
            start = time.time()

            try:
                graph = await planner.plan(goal, sec_ctx)
                elapsed = time.time() - start
                print(f" {C.GREEN}done{C.RESET} ({elapsed:.1f}s)")

                node_count = len(graph.nodes)
                print(f"  {C.BOLD}Executing {node_count} task(s)...{C.RESET}\n")

                for i, (nid, node) in enumerate(graph.nodes.items(), 1):
                    print(f"  {C.DIM}[{i}/{node_count}]{C.RESET} {node.name or nid} "
                          f"{C.DIM}({node.agent_type.value}){C.RESET}", end="", flush=True)

                result = await orch.process_goal(graph, sec_ctx)
                total_time = time.time() - start

                print(f"\n\n  {C.BOLD}{'─' * 50}{C.RESET}")

                status_color = C.GREEN if result["status"] == "success" else C.YELLOW
                print(f"  {status_color}{C.BOLD}Status:{C.RESET} {result['status'].upper()}")
                print(f"  {C.BOLD}Completed:{C.RESET} {len(result['completed_nodes'])}/{result['total_nodes']}")
                print(f"  {C.BOLD}Time:{C.RESET} {total_time:.1f}s")

                if result.get("errors"):
                    print(f"\n  {C.RED}Errors:{C.RESET}")
                    for err in result["errors"]:
                        print(f"    • {err['node_id']}: {err['error'][:100]}")

                # Show node outputs
                for nid, node in graph.nodes.items():
                    if node.output_data:
                        print(f"\n  {C.CYAN}{C.BOLD}→ {node.name or nid}{C.RESET}")
                        for k, v in node.output_data.items():
                            val = str(v)
                            if len(val) > 500:
                                val = val[:500] + "..."
                            if "\n" in val:
                                print(f"    {C.BOLD}{k}:{C.RESET}")
                                for line in val.split("\n")[:20]:
                                    print(f"      {line}")
                            else:
                                print(f"    {C.BOLD}{k}:{C.RESET} {val}")

                print(f"  {C.BOLD}{'─' * 50}{C.RESET}\n")

            except KeyboardInterrupt:
                print(f"\n  {C.YELLOW}Interrupted.{C.RESET}\n")
            except Exception as e:
                print(f"\n  {C.RED}Error: {e}{C.RESET}\n")
                logger.exception("Execution error")

    except KeyboardInterrupt:
        pass

    print(f"\n  {C.DIM}Shutting down...{C.RESET}")
    await orch.stop()
    print(f"  {C.GREEN}Goodbye!{C.RESET}\n")


def run_interactive():
    """Main entry point for interactive terminal."""
    print(BANNER)

    # Setup provider
    model_config = _setup_provider()
    if not model_config:
        print(f"\n  {C.DIM}No provider configured. Exiting.{C.RESET}\n")
        return

    # Save as default
    config = _load_config()
    config["model"] = model_config
    _save_config(config)

    # Start interactive loop
    logging.basicConfig(
        level=logging.WARNING,
        format="%(name)-30s | %(message)s",
    )
    asyncio.run(interactive_loop(model_config))


if __name__ == "__main__":
    run_interactive()
