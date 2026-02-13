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

check_import("goatclaw.core.metrics")
print("[*] FINISHED")
