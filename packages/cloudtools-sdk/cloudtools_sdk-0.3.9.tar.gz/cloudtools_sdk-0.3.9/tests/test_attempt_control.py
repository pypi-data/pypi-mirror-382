"""Tests for CloudTools attempt control (retry) functionality."""

import pytest
from datetime import timedelta
from cloudtools import CloudService, ServiceContext, CloudServiceError


class TestAttemptControl:
    """Test attempt control functionality."""

    def test_action_attempts_in_seconds(self):
        """Test action attempts specified as integer."""
        service = CloudService("test")
        
        @service.action(attempts=3)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that attempts metadata is stored
        assert hasattr(test_action, "__cloudtools_action_attempts__")
        assert test_action.__cloudtools_action_attempts__ == 3
        
        # Check that action is registered
        assert "test_action" in service.actions

    def test_action_attempts_with_timeout(self):
        """Test action with both attempts and timeout."""
        service = CloudService("test")
        
        @service.action(timeout=60, attempts=5)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that both metadata are stored
        assert hasattr(test_action, "__cloudtools_action_timeout__")
        assert hasattr(test_action, "__cloudtools_action_attempts__")
        assert test_action.__cloudtools_action_timeout__ == timedelta(seconds=60)
        assert test_action.__cloudtools_action_attempts__ == 5

    def test_action_without_attempts(self):
        """Test action without attempts (should not have attempts metadata)."""
        service = CloudService("test")
        
        @service.action
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that no attempts metadata is stored
        assert not hasattr(test_action, "__cloudtools_action_attempts__")

    def test_task_attempts_in_seconds(self):
        """Test task attempts specified as integer."""
        service = CloudService("test")
        
        @service.task("test_task", attempts=4)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that attempts metadata is stored
        assert hasattr(test_task, "__cloudtools_task_attempts__")
        assert test_task.__cloudtools_task_attempts__ == 4
        
        # Check that task is registered
        assert "test_task" in service.tasks

    def test_task_attempts_with_timeout(self):
        """Test task with both attempts and timeout."""
        service = CloudService("test")
        
        @service.task("test_task", timeout=300, attempts=3)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that both metadata are stored
        assert hasattr(test_task, "__cloudtools_task_timeout__")
        assert hasattr(test_task, "__cloudtools_task_attempts__")
        assert test_task.__cloudtools_task_timeout__ == timedelta(seconds=300)
        assert test_task.__cloudtools_task_attempts__ == 3

    def test_task_without_attempts(self):
        """Test task without attempts (should not have attempts metadata)."""
        service = CloudService("test")
        
        @service.task("test_task")
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that no attempts metadata is stored
        assert not hasattr(test_task, "__cloudtools_task_attempts__")

    def test_action_with_name_timeout_and_attempts(self):
        """Test action with name, timeout, and attempts."""
        service = CloudService("test")
        
        @service.action(name="custom_action", timeout=120, attempts=2)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that all metadata are stored
        assert hasattr(test_action, "__cloudtools_action_timeout__")
        assert hasattr(test_action, "__cloudtools_action_attempts__")
        assert test_action.__cloudtools_action_timeout__ == timedelta(seconds=120)
        assert test_action.__cloudtools_action_attempts__ == 2
        
        # Check that action is registered with custom name
        assert "custom_action" in service.actions
        assert "test_action" not in service.actions

    def test_task_with_name_timeout_and_attempts(self):
        """Test task with name, timeout, and attempts."""
        service = CloudService("test")
        
        @service.task("custom_task", timeout=600, attempts=3)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that all metadata are stored
        assert hasattr(test_task, "__cloudtools_task_timeout__")
        assert hasattr(test_task, "__cloudtools_task_attempts__")
        assert test_task.__cloudtools_task_timeout__ == timedelta(seconds=600)
        assert test_task.__cloudtools_task_attempts__ == 3
        
        # Check that task is registered with custom name
        assert "custom_task" in service.tasks

    def test_attempts_validation(self):
        """Test attempts validation."""
        service = CloudService("test")
        
        # Test valid attempts
        @service.action(attempts=1)
        async def single_attempt(data: str) -> str:
            return f"single: {data}"
        
        assert single_attempt.__cloudtools_action_attempts__ == 1
        
        # Test zero attempts (should be allowed)
        @service.action(attempts=0)
        async def zero_attempts(data: str) -> str:
            return f"zero: {data}"
        
        assert zero_attempts.__cloudtools_action_attempts__ == 0
        
        # Test negative attempts (should be allowed, but may not make sense)
        @service.action(attempts=-1)
        async def negative_attempts(data: str) -> str:
            return f"negative: {data}"
        
        assert negative_attempts.__cloudtools_action_attempts__ == -1

    def test_duplicate_action_registration_with_attempts(self):
        """Test that duplicate action registration still raises error."""
        service = CloudService("test")
        
        @service.action(attempts=3)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Try to register the same action again
        with pytest.raises(CloudServiceError):
            @service.action(attempts=5)
            async def test_action(data: str) -> str:
                return f"processed: {data}"

    def test_duplicate_task_registration_with_attempts(self):
        """Test that duplicate task registration still raises error."""
        service = CloudService("test")
        
        @service.task("test_task", attempts=3)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Try to register the same task again
        with pytest.raises(CloudServiceError):
            @service.task("test_task", attempts=5)
            async def test_task(payload: dict, ctx: ServiceContext) -> dict:
                return {"result": "success"}

    def test_attempts_with_http_exposure(self):
        """Test attempts with HTTP exposure."""
        service = CloudService("test")
        
        @service.task("http_task", timeout=300, attempts=3)
        @service.expose(
            path="/api/test",
            method="POST",
            auth="none",
            mode="sync"
        )
        async def http_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that attempts metadata is stored
        assert hasattr(http_task, "__cloudtools_task_attempts__")
        assert http_task.__cloudtools_task_attempts__ == 3
        
        # Check that exposure metadata is also stored
        assert hasattr(http_task, "__cloudtools_exposure_spec__")
        exposure = http_task.__cloudtools_exposure_spec__
        assert exposure.path == "/api/test"
        assert exposure.method == "POST"
        assert exposure.auth == "none"
        assert exposure.mode == "sync"

    def test_multiple_actions_with_different_attempts(self):
        """Test multiple actions with different attempt configurations."""
        service = CloudService("test")
        
        # Action with no attempts
        @service.action
        async def no_retry_action(data: str) -> str:
            return f"no_retry: {data}"
        
        # Action with 1 attempt (no retry)
        @service.action(attempts=1)
        async def single_attempt_action(data: str) -> str:
            return f"single: {data}"
        
        # Action with 3 attempts
        @service.action(attempts=3)
        async def retry_action(data: str) -> str:
            return f"retry: {data}"
        
        # Action with 5 attempts and timeout
        @service.action(timeout=60, attempts=5)
        async def complex_action(data: str) -> str:
            return f"complex: {data}"
        
        # Verify all actions are registered with correct metadata
        assert "no_retry_action" in service.actions
        assert not hasattr(service.actions["no_retry_action"], "__cloudtools_action_attempts__")
        
        assert "single_attempt_action" in service.actions
        assert service.actions["single_attempt_action"].__cloudtools_action_attempts__ == 1
        
        assert "retry_action" in service.actions
        assert service.actions["retry_action"].__cloudtools_action_attempts__ == 3
        
        assert "complex_action" in service.actions
        assert service.actions["complex_action"].__cloudtools_action_attempts__ == 5
        assert service.actions["complex_action"].__cloudtools_action_timeout__ == timedelta(seconds=60)

    def test_multiple_tasks_with_different_attempts(self):
        """Test multiple tasks with different attempt configurations."""
        service = CloudService("test")
        
        # Task with no attempts
        @service.task("no_retry_task")
        async def no_retry_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "no_retry"}
        
        # Task with 1 attempt (no retry)
        @service.task("single_attempt_task", attempts=1)
        async def single_attempt_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "single"}
        
        # Task with 3 attempts
        @service.task("retry_task", attempts=3)
        async def retry_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "retry"}
        
        # Task with 5 attempts and timeout
        @service.task("complex_task", timeout=300, attempts=5)
        async def complex_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "complex"}
        
        # Verify all tasks are registered with correct metadata
        assert "no_retry_task" in service.tasks
        assert not hasattr(service.tasks["no_retry_task"], "__cloudtools_task_attempts__")
        
        assert "single_attempt_task" in service.tasks
        assert service.tasks["single_attempt_task"].__cloudtools_task_attempts__ == 1
        
        assert "retry_task" in service.tasks
        assert service.tasks["retry_task"].__cloudtools_task_attempts__ == 3
        
        assert "complex_task" in service.tasks
        assert service.tasks["complex_task"].__cloudtools_task_attempts__ == 5
        assert service.tasks["complex_task"].__cloudtools_task_timeout__ == timedelta(seconds=300)
