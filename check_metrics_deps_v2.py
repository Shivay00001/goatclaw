import sys
import time
import os

def check_import(module_name):
    print(f"[*] START: {module_name}")
    sys.stdout.flush()
    start = time.time()
    try:
        __import__(module_name)
        print(f"[*] DONE: {module_name} in {time.time() - start:.2f}s")
    except Exception as e:
        print(f"[*] FAILED: {module_name} with {e}")
    sys.stdout.flush()

print(f"[*] PID: {os.getpid()}")
check_import("prometheus_client")
check_import("opentelemetry")
check_import("opentelemetry.trace")
check_import("opentelemetry.sdk.trace")
check_import("goatclaw.core.metrics")
print("[*] FINISHED ALL")
