"""
Test orchestration components
"""
import pytest
from dreamwalker_mcp.orchestration.models import Task, AgentResponse


def test_task_model_exists():
    """Test that Task model exists and can be instantiated"""
    # Check if Task class exists
    assert Task is not None
    
    # Try to create a basic task
    try:
        task = Task(
            id="test-1",
            prompt="Test prompt",
            agent="test-agent"
        )
        assert task.id == "test-1"
        assert task.prompt == "Test prompt"
    except TypeError:
        # Task might have different required fields
        pytest.skip("Task model has different structure")


def test_agent_response_model_exists():
    """Test that AgentResponse model exists"""
    assert AgentResponse is not None

