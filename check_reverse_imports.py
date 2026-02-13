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

check_import("goatclaw.core.metrics")
check_import("goatclaw.core.event_bus")
print("[*] Reverse order check done.")
