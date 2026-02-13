import pytest
import asyncio
from goatclaw.agents.security_agent import SecurityAgent
from goatclaw.core.structs import TaskNode, SecurityContext, PermissionScope, RiskLevel

@pytest.mark.asyncio
async def test_security_rate_limiting(event_bus):
    # Short limit for testing
    config = {"max_requests_per_hour": 5}
    security = SecurityAgent(event_bus, config)
    
    context = SecurityContext(user_id="test_user", origin_ip="127.0.0.1")
    
    # Consume all tokens
    for i in range(5):
        result = await security._check_rate_limit(context)
        assert result["allowed"] is True
    
    # Next one should fail
    result = await security._check_rate_limit(context)
    assert result["allowed"] is False
    assert result["reason"] == "rate_limit_exceeded"

@pytest.mark.asyncio
async def test_security_permission_check(event_bus):
    security = SecurityAgent(event_bus)
    
    # Node requires ADMIN
    node = TaskNode(
        name="admin_task",
        required_permissions=[PermissionScope.ADMIN]
    )
    
    # Context with only READ
    context = SecurityContext(
        user_id="user1", 
        allowed_scopes=[PermissionScope.READ]
    )
    
    result = await security._validate_permissions(node, context)
    assert result["valid"] is False
    assert "admin" in result["missing_permissions"]
    
    # Context with ADMIN
    admin_context = SecurityContext(
        user_id="admin1", 
        allowed_scopes=[PermissionScope.ADMIN]
    )
    result = await security._validate_permissions(node, admin_context)
    assert result["valid"] is True

@pytest.mark.asyncio
async def test_security_risk_assessment_critical(event_bus):
    security = SecurityAgent(event_bus)
    
    # Node with multiple risky factors
    node = TaskNode(
        name="risky_task",
        required_permissions=[PermissionScope.ADMIN, PermissionScope.DELETE]
    )
    
    # Unauthenticated context
    context = SecurityContext(user_id="anon", is_authenticated=False)
    
    result = await security._assess_risk(node, context)
    assert result["risk_level"] in ["high", "critical"]
    assert result["requires_approval"] is True

@pytest.mark.asyncio
async def test_security_ip_blocking(event_bus):
    security = SecurityAgent(event_bus)
    ip = "1.2.3.4"
    security.block_ip(ip)
    
    context = SecurityContext(user_id="hacker", origin_ip=ip)
    result = await security._check_rate_limit(context)
    
    assert result["allowed"] is False
    assert result["reason"] == "ip_blocked"
