import sys
import os
sys.path.append(os.getcwd())
print("[*] Starting test_min.py")
from goatclaw.orchestrator import Orchestrator
print("[*] Orchestrator imported")
from goatclaw.specialists import FileSystemAgent
print("[*] FileSystemAgent imported")

async def main():
    print("[*] Initializing Orchestrator...")
    orch = Orchestrator()
    print("[*] Orchestrator instance created")
    await orch.start()
    print("[*] Orchestrator started")
    await orch.stop()
    print("[*] Orchestrator stopped")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
