import os
import sys
import asyncio
import logging
from unittest.mock import MagicMock

# Force test environment variables BEFORE other imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["GOATCLAW_ENV"] = "test"

# Force silent logs during tests
logging.basicConfig(level=logging.ERROR)

try:
    from tests.test_event_bus import (
        test_event_bus_basic_pub_sub,
        test_event_bus_wildcard_subscription,
        test_event_bus_publish_and_wait
    )
    from tests.test_security import (
        test_security_rate_limiting,
        test_security_permission_check,
        test_security_ip_blocking
    )
    from tests.test_validation import (
        test_validation_schema,
        test_validation_type_conversion_autofix
    )
    from tests.test_orchestration import (
        test_orchestration_sequential,
        test_orchestration_parallel,
        test_orchestration_failure_retry
    )
    from goatclaw.database import db_manager
    from goatclaw.orchestrator import Orchestrator
    from goatclaw.core.event_bus import EventBus
    from goatclaw.core.structs import SecurityContext, Event
except ImportError as e:
    print(f"FAILED TO IMPORT TESTS: {e}")
    sys.exit(1)

async def run_test(name, func, *args):
    print(f"RUNNING: {name}...")
    try:
        await func(*args)
        print(f"   [+] {name}: PASSED")
        return True
    except BaseException as e:
        print(f"   [-] {name}: FAILED")
        # If it's an AssertionError, maybe print the result if we have it
        import traceback
        traceback.print_exc()
        return False

def main():
    print("GOATCLAW UNIFIED TEST RUNNER\n")
    
    unit_tests = [
        ("EventBus Basic", test_event_bus_basic_pub_sub),
        ("EventBus Wildcards", test_event_bus_wildcard_subscription),
        ("EventBus Req-Resp", test_event_bus_publish_and_wait),
        ("Security Rate Limit", test_security_rate_limiting),
        ("Security Permissions", test_security_permission_check),
        ("Security IP Block", test_security_ip_blocking),
        ("Validation Schema", test_validation_schema),
        ("Validation Auto-fix", test_validation_type_conversion_autofix),
    ]
    
    integration_tests = [
        ("Orchestration Seq", test_orchestration_sequential),
        ("Orchestration Parallel", test_orchestration_parallel),
        ("Orchestration Retry", test_orchestration_failure_retry),
    ]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    passed = []
    failed = []

    def run_suite(suite, use_orchestrator=False):
        for name, func in suite:
            bus = EventBus(enable_persistence=False)
            try:
                if use_orchestrator:
                    orch = Orchestrator({"max_event_history": 100})
                    ctx = SecurityContext(user_id="test")
                    args = [orch, ctx]
                else:
                    args = [bus]
                
                if loop.run_until_complete(run_test(name, func, *args)):
                    passed.append(name)
                else:
                    failed.append(name)
            finally:
                try:
                    loop.run_until_complete(asyncio.wait_for(bus.stop(), timeout=1.0))
                    if use_orchestrator:
                        loop.run_until_complete(db_manager.close())
                except:
                    pass

    run_suite(unit_tests)
    run_suite(integration_tests, use_orchestrator=True)

    print(f"\nSUMMARY: {len(passed)}/{len(passed) + len(failed)} PASSED")
    if passed:
        print(f"PASSED: {', '.join(passed)}")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        sys.exit(1)
    
    print("\nALL TESTS PASSED - 10/10")

if __name__ == "__main__":
    main()
