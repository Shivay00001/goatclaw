import asyncio
import os
import sys
import json

# Force test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["GOATCLAW_ENV"] = "test"

from tests.test_validation import test_validation_schema
from goatclaw.core.event_bus import EventBus

async def debug_validation():
    bus = EventBus(enable_persistence=False)
    print("RUNNING Validation Schema...")
    try:
        await test_validation_schema(bus)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bus.stop()

if __name__ == "__main__":
    asyncio.run(debug_validation())
