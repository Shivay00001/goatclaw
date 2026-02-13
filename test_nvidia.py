"""Test script for NVIDIA Kimi K2.5 API."""
import asyncio
import logging
import os
from goatclaw.runner import create_orchestrator, create_default_security_context
from goatclaw.core.structs import TaskGraph, TaskNode, AgentType

logging.basicConfig(level=logging.INFO, format="%(name)-30s | %(message)s")

async def test_nvidia():
    # Model config for NVIDIA
    # Based on "nvidia ka kimi k2.5 wala", let's try the model name
    model_cfg = {
        "provider": "nvidia",
        "name": "moonshotai/kimi-k2.5", # Corrected identifier
        "base_url": "https://integrate.api.nvidia.com/v1/chat/completions"
    }
    
    config = {"model": model_cfg}
    # Ensure all agents use this config
    for k in ["research", "code", "devops", "api", "data_processing", "filesystem"]:
        config[k] = {"model": model_cfg}

    orch = create_orchestrator(config)
    await orch.start()

    # Create a CodeAgent node - CodeAgent actually calls _call_llm for 'generate'
    graph = TaskGraph(goal_summary="NVIDIA API Test")
    node = TaskNode(
        node_id="api_test_node",
        name="api_test",
        agent_type=AgentType.CODE,
        input_data={
            "action": "generate",
            "language": "python",
            "spec": "print 'Hello from NVIDIA Kimi K2.5'"
        }
    )
    graph.add_node(node)

    print("\n[1] STARTING NVIDIA API TEST (via CodeAgent)...")
    print(f"[2] Provider: {model_cfg['provider']}, Model: {model_cfg['name']}")
    
    sec_ctx = create_default_security_context()
    
    try:
        result = await orch.process_goal(graph, sec_ctx)
        
        print(f"\n[3] EXECUTION STATUS: {result['status']}")
        
        if result.get("errors"):
            for err in result["errors"]:
                print(f"    ERROR: {err}")
        
        # Show output from the specific node
        n = graph.nodes.get("api_test_node")
        if n and n.output_data:
            print(f"\n[4] LLM RESPONSE:")
            # CodeAgent returns 'code'
            if "code" in n.output_data:
                print("-" * 40)
                print(n.output_data["code"])
                print("-" * 40)
            else:
                print(f"    Raw Output: {n.output_data}")
                    
    except Exception as e:
        print(f"\n[!] TEST CRASHED: {e}")
    finally:
        await orch.stop()
    print("\n[5] DONE!")

if __name__ == "__main__":
    asyncio.run(test_nvidia())
