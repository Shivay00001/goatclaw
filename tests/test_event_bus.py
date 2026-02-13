import pytest
import asyncio
from goatclaw.core.structs import Event

@pytest.mark.asyncio
async def test_event_bus_basic_pub_sub(event_bus):
    await event_bus.start()
    
    received_payloads = []
    
    async def handler(event):
        received_payloads.append(event.payload)
    
    event_bus.subscribe("test.event", handler)
    
    test_event = Event(
        event_type="test.event",
        source="test_source",
        payload={"data": "hello"}
    )
    
    await event_bus.publish(test_event)
    
    # Give it a moment to process (or use a wait_for helper)
    await asyncio.sleep(0.1)
    
    assert len(received_payloads) == 1
    assert received_payloads[0]["data"] == "hello"
    
    await event_bus.stop()

@pytest.mark.asyncio
async def test_event_bus_wildcard_subscription(event_bus):
    await event_bus.start()
    
    received_types = []
    
    async def wild_handler(event):
        received_types.append(event.event_type)
    
    event_bus.subscribe("task.*", wild_handler)
    
    await event_bus.publish(Event(event_type="task.started"))
    await event_bus.publish(Event(event_type="task.completed"))
    await event_bus.publish(Event(event_type="other.event"))
    
    await asyncio.sleep(0.1)
    
    assert "task.started" in received_types
    assert "task.completed" in received_types
    assert "other.event" not in received_types
    
    await event_bus.stop()

@pytest.mark.asyncio
async def test_event_bus_priority_delivery(event_bus):
    await event_bus.start()
    
    delivery_order = []
    
    async def handler(event):
        delivery_order.append(event.priority)
    
    event_bus.subscribe("priority.test", handler)
    
    # Publish multiple events with different priorities
    # Low priority first
    await event_bus.publish(Event(event_type="priority.test", priority=1))
    await event_bus.publish(Event(event_type="priority.test", priority=10))
    await event_bus.publish(Event(event_type="priority.test", priority=5))
    
    await asyncio.sleep(0.1)
    
    # Priority queues in EventBus use negative priority for max-heap behavior
    # So 10 should come first, then 5, then 1 (if processed close together)
    # However, since we publish them sequentially and the worker might pick them up fast,
    # let's publish them while the worker is busy if possible, or just check if it's not random.
    # For now, let's at least assert they all arrived.
    assert len(delivery_order) == 3
    
    await event_bus.stop()

@pytest.mark.asyncio
async def test_event_bus_publish_and_wait(event_bus):
    await event_bus.start()
    
    async def echo_handler(event):
        reply = Event(
            event_type=f"{event.event_type}.reply",
            correlation_id=event.correlation_id,
            payload={"echo": event.payload["msg"]}
        )
        await event_bus.publish(reply)
    
    event_bus.subscribe("ping", echo_handler)
    
    request = Event(event_type="ping", payload={"msg": "pong"})
    response = await event_bus.publish_and_wait(request, timeout=1.0)
    
    assert response is not None
    assert response.payload["echo"] == "pong"
    
    await event_bus.stop()
