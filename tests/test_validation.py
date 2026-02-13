import pytest
import asyncio
import json
from goatclaw.agents.validation_agent import ValidationAgent
from goatclaw.core.structs import TaskNode, TaskStatus

@pytest.mark.asyncio
async def test_validation_schema(event_bus):
    # Disable auto-fix to check detection logic
    validator = ValidationAgent(event_bus, {"auto_fix_enabled": False})
    
    schema = {
        "type": "object",
        "required": ["status", "result"]
    }
    
    node = TaskNode(
        name="test_node",
        validation_rule=f"schema: {json.dumps(schema)}"
    )
    
    # Valid output
    node.output_data = {"status": "ok", "result": 42}
    result = await validator.execute(node, None)
    assert result["valid"] is True
    
    # Missing field
    node.output_data = {"status": "ok"}
    result = await validator.execute(node, None)
    assert result["valid"] is False
    assert "Missing required fields" in result["message"]

@pytest.mark.asyncio
async def test_validation_range_clamping_autofix(event_bus):
    # Enable auto-fix
    validator = ValidationAgent(event_bus, {"auto_fix_enabled": True})
    
    node = TaskNode(
        name="range_test",
        validation_rule="range: min:0,max:100"
    )
    
    # Out of range
    node.output_data = 150
    result = await validator.execute(node, None)
    
    # Should be auto-fixed to 100
    assert result["valid"] is True
    assert node.output_data == 100
    assert "auto-fixed" in result["message"]

@pytest.mark.asyncio
async def test_validation_type_conversion_autofix(event_bus):
    validator = ValidationAgent(event_bus, {"auto_fix_enabled": True})
    
    node = TaskNode(
        name="type_test",
        validation_rule="type: int"
    )
    
    # String that can be converted
    node.output_data = "123"
    result = await validator.execute(node, None)
    
    assert result["valid"] is True
    assert node.output_data == 123
    assert isinstance(node.output_data, int)

@pytest.mark.asyncio
async def test_validation_custom_expression(event_bus):
    validator = ValidationAgent(event_bus)
    
    node = TaskNode(
        name="custom_test",
        validation_rule="output['score'] > 0.8"
    )
    
    node.output_data = {"score": 0.9}
    result = await validator.execute(node, None)
    assert result["valid"] is True
    
    node.output_data = {"score": 0.7}
    result = await validator.execute(node, None)
    assert result["valid"] is False
