import asyncio
import os
from goatclaw.agents.base_agent import BaseAgent
from goatclaw.core.event_bus import EventBus

class ConcreteAgent(BaseAgent):
    async def execute(self, task_node, context):
        return {"status": "ok"}

async def test_direct():
    event_bus = EventBus()
    # Use concrete class
    agent = ConcreteAgent("TestAgent", event_bus, {"model": {"provider": "nvidia", "name": "moonshotai/kimi-k2.5"}})
    
    prompt = "Hello! Please confirm you are the Kimi K2.5 model running on NVIDIA NIM. Provide a short greeting."
    print(f"Calling NVIDIA API with model: moonshotai/kimi-k2.5...")
    
    response = await agent._call_llm(prompt)
    print("\n" + "="*50)
    print("NVIDIA KIMI RESPONSE:")
    print("="*50)
    print(response)
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_direct())
