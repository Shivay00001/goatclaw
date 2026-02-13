import pytest
import asyncio
from goatclaw.orchestrator import Orchestrator
from goatclaw.core.structs import TaskGraph, TaskNode, AgentType, ExecutionMode, TaskStatus
from goatclaw.agents.base_agent import BaseAgent

class MockAgent(BaseAgent):
    async def execute(self, node, context):
        return {"result": f"processed {node.name}"}

@pytest.mark.asyncio
async def test_orchestration_sequential(orchestrator, security_context):
    await orchestrator.start()
    
    # Register mock code agent
    mock_agent = MockAgent("MockAgent", orchestrator.event_bus)
    orchestrator.register_agent(AgentType.CODE, mock_agent)
    
    graph = TaskGraph(goal_summary="Sequential test")
    node1 = TaskNode(name="node1", agent_type=AgentType.CODE)
    node2 = TaskNode(name="node2", agent_type=AgentType.CODE, dependencies=[node1.node_id])
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    result = await orchestrator.process_goal(graph, security_context)
    
    assert result["status"] == "success"
    assert len(result["completed_nodes"]) == 2
    assert graph.nodes[node1.node_id].status == TaskStatus.SUCCESS
    assert graph.nodes[node2.node_id].status == TaskStatus.SUCCESS
    
    await orchestrator.stop()

@pytest.mark.asyncio
async def test_orchestration_parallel(orchestrator, security_context):
    await orchestrator.start()
    
    mock_agent = MockAgent("MockAgent", orchestrator.event_bus)
    orchestrator.register_agent(AgentType.CODE, mock_agent)
    
    graph = TaskGraph(
        goal_summary="Parallel test",
        execution_mode=ExecutionMode.PARALLEL
    )
    
    # Independent nodes
    for i in range(3):
        node = TaskNode(name=f"p_node_{i}", agent_type=AgentType.CODE)
        graph.add_node(node)
    
    result = await orchestrator.process_goal(graph, security_context)
    
    assert result["status"] == "success"
    assert len(result["completed_nodes"]) == 3
    
    await orchestrator.stop()

@pytest.mark.asyncio
async def test_orchestration_failure_retry(orchestrator, security_context):
    await orchestrator.start()
    
    class FailingAgent(BaseAgent):
        def __init__(self, *args):
            super().__init__(*args)
            self.calls = 0
            
        async def execute(self, node, context):
            self.calls += 1
            print(f"[DEBUG] FailingAgent.execute call {self.calls}")
            if self.calls < 2:
                raise ValueError("Temporary failure")
            return {"result": "success after retry"}

    fail_agent = FailingAgent("FailingAgent", orchestrator.event_bus)
    orchestrator.register_agent(AgentType.CODE, fail_agent)
    
    graph = TaskGraph(goal_summary="Retry test")
    node = TaskNode(name="retry_node", agent_type=AgentType.CODE)
    node.retry_config.max_retries = 2
    node.retry_config.initial_delay_seconds = 0.1
    
    graph.add_node(node)
    
    result = await orchestrator.process_goal(graph, security_context)
    
    assert result["status"] == "success"
    assert fail_agent.calls == 2
    
    await orchestrator.stop()
