import pytest
import asyncio
from goatclaw.core.event_bus import EventBus
from goatclaw.orchestrator import Orchestrator
from goatclaw.core.structs import SecurityContext, PermissionScope

@pytest.fixture
def event_bus():
    """Provides a fresh, non-persistent event bus for each test."""
    return EventBus(enable_persistence=False)

@pytest.fixture
def orchestrator():
    """Provides a configured orchestrator instance."""
    config = {
        "max_event_history": 100,
        "security": {
            "max_requests_per_hour": 1000,
            "threat_threshold": 0.9
        }
    }
    return Orchestrator(config)

@pytest.fixture
def security_context():
    """Provides a standard security context."""
    return SecurityContext(
        user_id="test_user",
        is_authenticated=True,
        allowed_scopes=[PermissionScope.READ, PermissionScope.WRITE, PermissionScope.EXECUTE]
    )

@pytest.fixture
def admin_context():
    """Provides an admin security context."""
    return SecurityContext(
        user_id="admin_user",
        is_authenticated=True,
        allowed_scopes=[PermissionScope.ADMIN]
    )
