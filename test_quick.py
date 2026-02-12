"""Quick test: just verify LLM calling works end-to-end."""
import asyncio
import logging
import os

logging.basicConfig(level=logging.WARNING)

async def test():
    from goatclaw.runner import create_orchestrator, create_default_security_context
    from goatclaw.core.structs import TaskGraph, TaskNode, AgentType

    model_cfg = {"provider": "ollama", "name": "qwen2:0.5b"}
    config = {"model": model_cfg}
    for k in ["research", "code", "devops", "api", "data_processing", "filesystem"]:
        config[k] = {"model": model_cfg}

    orch = create_orchestrator(config)
    await orch.start()

    # Create a simple 1-node graph manually (skip planner)
    graph = TaskGraph(goal_summary="Write hello world in Python")
    node = TaskNode(
        name="generate_code",
        agent_type=AgentType.CODE,
        input_data={
            "action": "generate_code",
            "spec": "Write a Python function that prints hello world",
            "language": "python"
        }
    )
    graph.add_node(node)

    print("STARTING EXECUTION...")
    sec_ctx = create_default_security_context()
    result = await orch.process_goal(graph, sec_ctx)

    print(f"STATUS: {result['status']}")
    print(f"COMPLETED: {len(result['completed_nodes'])}/{result['total_nodes']}")
    print(f"TIME: {result['execution_time_seconds']:.1f}s")

    if result.get("errors"):
        for err in result["errors"]:
            print(f"ERROR: {err}")

    # Show output from the code node
    for nid, n in graph.nodes.items():
        if n.output_data:
            print(f"\nNODE OUTPUT ({n.name}):")
            for k, v in n.output_data.items():
                val_str = str(v)[:500]
                print(f"  {k}: {val_str}")

    await orch.stop()
    print("\nDONE!")

if __name__ == "__main__":
    asyncio.run(test())
