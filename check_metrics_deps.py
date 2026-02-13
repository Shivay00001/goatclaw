import sys
import time
import os

def check_import(module_name):
    print(f"[*] Importing {module_name}...", end=" ", flush=True)
    start = time.time()
    try:
        __import__(module_name)
        print(f"DONE ({time.time() - start:.2f}s)")
    except Exception as e:
        print(f"FAILED: {e}")

print(f"[*] ENV GOATCLAW_DEBUG_TRACING: {os.getenv('GOATCLAW_DEBUG_TRACING')}")
print(f"[*] ENV GOATCLAW_LOG_JSON: {os.getenv('GOATCLAW_LOG_JSON')}")

check_import("prometheus_client")
check_import("opentelemetry")
check_import("opentelemetry.trace")
check_import("opentelemetry.sdk.trace")
check_import("goatclaw.core.metrics")
print("[*] Granular check done.")
