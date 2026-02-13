import sys
import time

def check_import(module_name):
    print(f"[*] Importing {module_name}...", end=" ", flush=True)
    start = time.time()
    try:
        __import__(module_name)
        print(f"DONE ({time.time() - start:.2f}s)")
    except Exception as e:
        print(f"FAILED: {e}")

check_import("goatclaw.core.structs")
check_import("goatclaw.core.event_bus")
check_import("goatclaw.core.metrics")
check_import("goatclaw.core.vault")
check_import("goatclaw.core.ollama_client")
check_import("goatclaw.core.billing")
check_import("goatclaw.database")
check_import("goatclaw.task_queue")
check_import("goatclaw.vector_store")
check_import("goatclaw.agents.base_agent")
check_import("goatclaw.agents.security_agent")
check_import("goatclaw.agents.validation_agent")
check_import("goatclaw.agents.memory_agent")
check_import("goatclaw.orchestrator")
print("[*] All imports checked.")
