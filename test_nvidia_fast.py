import asyncio
from goatclaw.agents.base_agent import BaseAgent
from goatclaw.core.event_bus import EventBus

class ConcreteAgent(BaseAgent):
    async def execute(self, task_node, context):
        return {"status": "ok"}

async def test_fast():
    event_bus = EventBus()
    # Testing with Llama-3.1-8b which is fast to verify the API key
    agent = ConcreteAgent("TestAgent", event_bus, {"model": {"provider": "nvidia", "name": "meta/llama-3.1-8b-instruct"}})
    
    prompt = "Hi NVIDIA! This is a test. Respond with 'API Key Verified'."
    print(f"Verifying API key with model: meta/llama-3.1-8b-instruct...")
    
    response = await agent._call_llm(prompt)
    print("\n" + "="*50)
    print("NVIDIA RESPONSE:")
    print("="*50)
    print(response)
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_fast())
