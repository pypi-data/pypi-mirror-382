"""Tests for CloudTools timeout decorators."""

import pytest
from datetime import timedelta
from cloudtools import CloudService, ServiceContext, CloudServiceError


class TestTimeoutDecorators:
    """Test timeout decorator functionality."""

    def test_action_timeout_in_seconds(self):
        """Test action timeout specified in seconds."""
        service = CloudService("test")
        
        @service.action(timeout=60)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that timeout metadata is stored
        assert hasattr(test_action, "__cloudtools_action_timeout__")
        assert test_action.__cloudtools_action_timeout__ == timedelta(seconds=60)
        
        # Check that action is registered
        assert "test_action" in service.actions

    def test_action_timeout_with_timedelta(self):
        """Test action timeout specified with timedelta."""
        service = CloudService("test")
        
        @service.action(timeout=timedelta(minutes=5))
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that timeout metadata is stored
        assert hasattr(test_action, "__cloudtools_action_timeout__")
        assert test_action.__cloudtools_action_timeout__ == timedelta(minutes=5)

    def test_action_without_timeout(self):
        """Test action without timeout (should not have timeout metadata)."""
        service = CloudService("test")
        
        @service.action
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that no timeout metadata is stored
        assert not hasattr(test_action, "__cloudtools_action_timeout__")

    def test_task_timeout_in_seconds(self):
        """Test task timeout specified in seconds."""
        service = CloudService("test")
        
        @service.task("test_task", timeout=300)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that timeout metadata is stored
        assert hasattr(test_task, "__cloudtools_task_timeout__")
        assert test_task.__cloudtools_task_timeout__ == timedelta(seconds=300)
        
        # Check that task is registered
        assert "test_task" in service.tasks

    def test_task_timeout_with_timedelta(self):
        """Test task timeout specified with timedelta."""
        service = CloudService("test")
        
        @service.task("test_task", timeout=timedelta(minutes=10))
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that timeout metadata is stored
        assert hasattr(test_task, "__cloudtools_task_timeout__")
        assert test_task.__cloudtools_task_timeout__ == timedelta(minutes=10)

    def test_task_without_timeout(self):
        """Test task without timeout (should not have timeout metadata)."""
        service = CloudService("test")
        
        @service.task("test_task")
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that no timeout metadata is stored
        assert not hasattr(test_task, "__cloudtools_task_timeout__")

    def test_action_with_name_and_timeout(self):
        """Test action with both name and timeout."""
        service = CloudService("test")
        
        @service.action(name="custom_action", timeout=120)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that timeout metadata is stored
        assert hasattr(test_action, "__cloudtools_action_timeout__")
        assert test_action.__cloudtools_action_timeout__ == timedelta(seconds=120)
        
        # Check that action is registered with custom name
        assert "custom_action" in service.actions
        assert "test_action" not in service.actions

    def test_action_with_total_timeout(self):
        """Test action with total timeout metadata."""
        service = CloudService("test")

        @service.action(timeout=10, total_timeout=30)
        async def test_action(data: str) -> str:
            return f"processed: {data}"

        assert hasattr(test_action, "__cloudtools_action_timeout__")
        assert test_action.__cloudtools_action_timeout__ == timedelta(seconds=10)
        assert hasattr(test_action, "__cloudtools_action_total_timeout__")
        assert test_action.__cloudtools_action_total_timeout__ == timedelta(seconds=30)

    def test_action_without_total_timeout(self):
        """Actions without total timeout should not store metadata."""
        service = CloudService("test")

        @service.action(timeout=5)
        async def test_action(data: str) -> str:
            return f"processed: {data}"

        assert not hasattr(test_action, "__cloudtools_action_total_timeout__")

    def test_task_with_name_and_timeout(self):
        """Test task with both name and timeout."""
        service = CloudService("test")
        
        @service.task("custom_task", timeout=600)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Check that timeout metadata is stored
        assert hasattr(test_task, "__cloudtools_task_timeout__")
        assert test_task.__cloudtools_task_timeout__ == timedelta(seconds=600)
        
        # Check that task is registered with custom name
        assert "custom_task" in service.tasks

    def test_duplicate_action_registration_with_timeout(self):
        """Test that duplicate action registration still raises error."""
        service = CloudService("test")
        
        @service.action(timeout=60)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Try to register the same action again
        with pytest.raises(CloudServiceError):
            @service.action(timeout=120)
            async def test_action(data: str) -> str:
                return f"processed: {data}"

    def test_duplicate_task_registration_with_timeout(self):
        """Test that duplicate task registration still raises error."""
        service = CloudService("test")
        
        @service.task("test_task", timeout=300)
        async def test_task(payload: dict, ctx: ServiceContext) -> dict:
            return {"result": "success"}
        
        # Try to register the same task again
        with pytest.raises(CloudServiceError):
            @service.task("test_task", timeout=600)
            async def test_task(payload: dict, ctx: ServiceContext) -> dict:
                return {"result": "success"}

    def test_timeout_conversion_from_int(self):
        """Test that integer timeouts are converted to timedelta."""
        service = CloudService("test")
        
        @service.action(timeout=90)  # 90 seconds
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that timeout was converted to timedelta
        assert test_action.__cloudtools_action_timeout__ == timedelta(seconds=90)

    def test_timeout_preserves_timedelta(self):
        """Test that timedelta timeouts are preserved as-is."""
        service = CloudService("test")
        
        timeout_val = timedelta(hours=1, minutes=30)
        
        @service.action(timeout=timeout_val)
        async def test_action(data: str) -> str:
            return f"processed: {data}"
        
        # Check that timeout was preserved
        assert test_action.__cloudtools_action_timeout__ == timeout_val
