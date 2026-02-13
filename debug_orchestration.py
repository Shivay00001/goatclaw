import asyncio
import os
import sys

# Force test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["GOATCLAW_ENV"] = "test"

from tests.test_orchestration import test_orchestration_sequential, test_orchestration_parallel
from goatclaw.orchestrator import Orchestrator
from goatclaw.core.structs import SecurityContext

async def debug_orchestration():
    orchestrator = Orchestrator({"max_event_history": 100})
    context = SecurityContext(user_id="test")
    
    print("RUNNING Orchestration Sequential...")
    try:
        await test_orchestration_sequential(orchestrator, context)
        print("✅ Sequential PASSED")
    except Exception as e:
        print(f"❌ Sequential FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\nRUNNING Orchestration Parallel...")
    try:
        await test_orchestration_parallel(orchestrator, context)
        print("✅ Parallel PASSED")
    except Exception as e:
        print(f"❌ Parallel FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_orchestration())
