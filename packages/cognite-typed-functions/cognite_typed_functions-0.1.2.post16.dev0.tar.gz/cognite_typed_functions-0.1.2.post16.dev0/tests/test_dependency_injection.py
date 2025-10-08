"""Tests for dependency injection of client, secrets, and function_call_info.

These tests verify that the framework correctly implements dependency injection
for Cognite Function dependencies based on function signatures.
"""

from collections.abc import Mapping
from unittest.mock import Mock

import pytest
from cognite.client import CogniteClient
from pydantic import BaseModel

from cognite_typed_functions.app import CogniteApp, create_function_handle
from cognite_typed_functions.models import FunctionCallInfo


class Item(BaseModel):
    """Test item model."""

    name: str
    price: float


class ItemResponse(BaseModel):
    """Test response model."""

    id: int
    name: str
    price: float
    has_secrets: bool
    has_call_info: bool


class TestDependencyInjection:
    """Test dependency injection for route handlers."""

    @pytest.fixture
    def mock_client(self) -> CogniteClient:
        """Mock CogniteClient for testing."""
        return Mock(spec=CogniteClient)

    @pytest.fixture
    def app(self) -> CogniteApp:
        """Create test app."""
        return CogniteApp(title="Test App", version="1.0.0")

    def test_handler_with_no_dependencies(self, app: CogniteApp, mock_client: CogniteClient):
        """Test handler that doesn't declare any dependency parameters."""

        @app.get("/items/{item_id}")
        def get_item(item_id: int) -> ItemResponse:
            """Handler with no dependencies."""
            return ItemResponse(
                id=item_id,
                name="Test Item",
                price=99.99,
                has_secrets=False,
                has_call_info=False,
            )

        handle = create_function_handle(app)

        # Call the handler
        result = handle(
            client=mock_client,
            data={
                "path": "/items/123",
                "method": "GET",
            },
            secrets={"api_key": "secret123"},
            function_call_info={
                "function_id": "func123",
                "call_id": "call456",
                "schedule_id": None,
                "scheduled_time": None,
            },
        )
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["data"]["id"] == 123
        assert result["data"]["has_secrets"] is False
        assert result["data"]["has_call_info"] is False

    def test_handler_with_client_only(self, app: CogniteApp, mock_client: CogniteClient):
        """Test handler that only declares client parameter."""

        @app.get("/items/{item_id}")
        def get_item(client: CogniteClient, item_id: int) -> ItemResponse:
            """Handler with client only."""
            assert client is not None
            assert isinstance(client, Mock)
            return ItemResponse(
                id=item_id,
                name="Test Item",
                price=99.99,
                has_secrets=False,
                has_call_info=False,
            )

        handle = create_function_handle(app)

        result = handle(
            client=mock_client,
            data={
                "path": "/items/456",
                "method": "GET",
            },
            secrets={"api_key": "secret123"},
            function_call_info={
                "function_id": "func123",
                "call_id": "call456",
                "schedule_id": None,
                "scheduled_time": None,
            },
        )

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["data"]["id"] == 456

    def test_handler_with_client_and_secrets(self, app: CogniteApp, mock_client: CogniteClient):
        """Test handler that declares client and secrets."""

        @app.get("/items/{item_id}")
        def get_item(
            client: CogniteClient,
            secrets: Mapping[str, str],
            item_id: int,
        ) -> ItemResponse:
            """Handler with client and secrets."""
            assert client is not None
            assert secrets is not None
            assert "api_key" in secrets
            assert secrets["api_key"] == "secret123"
            return ItemResponse(
                id=item_id,
                name="Test Item",
                price=99.99,
                has_secrets=True,
                has_call_info=False,
            )

        handle = create_function_handle(app)

        result = handle(
            client=mock_client,
            data={
                "path": "/items/789",
                "method": "GET",
            },
            secrets={"api_key": "secret123"},
            function_call_info={
                "function_id": "func123",
                "call_id": "call456",
                "schedule_id": None,
                "scheduled_time": None,
            },
        )

        assert isinstance(result, dict)
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["success"] is True
        assert result["data"]["has_secrets"] is True

    def test_handler_with_all_dependencies(self, app: CogniteApp, mock_client: CogniteClient):
        """Test handler that declares all three dependency parameters."""

        @app.get("/items/{item_id}")
        def get_item(
            client: CogniteClient,
            secrets: Mapping[str, str],
            function_call_info: FunctionCallInfo,
            item_id: int,
        ) -> ItemResponse:
            """Handler with all dependencies."""
            assert client is not None
            assert secrets is not None
            assert function_call_info is not None
            assert function_call_info["function_id"] == "func123"
            assert function_call_info["call_id"] == "call456"
            return ItemResponse(
                id=item_id,
                name="Test Item",
                price=99.99,
                has_secrets=True,
                has_call_info=True,
            )

        handle = create_function_handle(app)

        result = handle(
            client=mock_client,
            data={
                "path": "/items/999",
                "method": "GET",
            },
            secrets={"api_key": "secret123"},
            function_call_info={
                "function_id": "func123",
                "call_id": "call456",
                "schedule_id": None,
                "scheduled_time": None,
            },
        )

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["data"]["has_secrets"] is True
        assert result["data"]["has_call_info"] is True

    def test_handler_with_client_and_function_call_info(self, app: CogniteApp, mock_client: CogniteClient):
        """Test handler with client and function_call_info but no secrets."""

        @app.get("/items/{item_id}")
        def get_item(
            client: CogniteClient,
            function_call_info: FunctionCallInfo,
            item_id: int,
        ) -> ItemResponse:
            """Handler with client and function_call_info."""
            assert client is not None
            assert function_call_info is not None
            return ItemResponse(
                id=item_id,
                name="Test Item",
                price=99.99,
                has_secrets=False,
                has_call_info=True,
            )

        handle = create_function_handle(app)

        result = handle(
            client=mock_client,
            data={
                "path": "/items/111",
                "method": "GET",
            },
            secrets={"api_key": "secret123"},
            function_call_info={
                "function_id": "func123",
                "call_id": "call456",
                "schedule_id": None,
                "scheduled_time": None,
            },
        )

        assert isinstance(result, dict)
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["success"] is True
        assert result["data"]["has_call_info"] is True

    def test_handler_parameter_order_flexibility(self, app: CogniteApp, mock_client: CogniteClient):
        """Test that dependency parameters can be declared in any order."""

        @app.post("/items")
        def create_item(
            item: Item,
            secrets: Mapping[str, str],
            client: CogniteClient,
        ) -> ItemResponse:
            """Handler with dependencies in non-standard order."""
            assert client is not None
            assert secrets is not None
            assert item.name == "Widget"
            return ItemResponse(
                id=1,
                name=item.name,
                price=item.price,
                has_secrets=True,
                has_call_info=False,
            )

        handle = create_function_handle(app)

        result = handle(
            client=mock_client,
            data={
                "path": "/items",
                "method": "POST",
                "body": {"item": {"name": "Widget", "price": 29.99}},
            },
            secrets={"api_key": "secret123"},
        )

        assert isinstance(result, dict)
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["success"] is True
        assert result["data"]["name"] == "Widget"
        assert result["data"]["has_secrets"] is True

    def test_handler_without_client_when_none_provided(self, app: CogniteApp, mock_client: CogniteClient):
        """Test that handler without client parameter works even when client is provided."""

        @app.get("/ping")
        def ping() -> dict[str, str]:
            """Simple handler with no parameters at all."""
            return {"status": "pong"}

        handle = create_function_handle(app)

        result = handle(
            client=mock_client,
            data={
                "path": "/ping",
                "method": "GET",
            },
        )

        assert isinstance(result, dict)
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["success"] is True
        assert result["data"]["status"] == "pong"

    def test_multiple_handlers_with_different_dependencies(self, app: CogniteApp, mock_client: CogniteClient):
        """Test that different handlers in the same app can have different dependencies."""

        @app.get("/public")
        def public_endpoint() -> dict[str, str]:
            """Public endpoint with no dependencies."""
            return {"type": "public"}

        @app.get("/authenticated")
        def authenticated_endpoint(client: CogniteClient) -> dict[str, str]:
            """Authenticated endpoint with client."""
            assert client is not None
            return {"type": "authenticated"}

        @app.get("/admin")
        def admin_endpoint(client: CogniteClient, secrets: Mapping[str, str]) -> dict[str, str]:
            """Admin endpoint with client and secrets."""
            assert client is not None
            assert secrets is not None
            return {"type": "admin"}

        handle = create_function_handle(app)

        # Test public endpoint
        result1 = handle(client=mock_client, data={"path": "/public", "method": "GET"})
        assert isinstance(result1, dict)
        assert result1["data"] is not None
        assert isinstance(result1["data"], dict)
        assert result1["data"]["type"] == "public"

        # Test authenticated endpoint
        result2 = handle(client=mock_client, data={"path": "/authenticated", "method": "GET"})
        assert isinstance(result2, dict)
        assert result2["data"] is not None
        assert isinstance(result2["data"], dict)
        assert result2["data"]["type"] == "authenticated"

        # Test admin endpoint
        result3 = handle(
            client=mock_client,
            data={"path": "/admin", "method": "GET"},
            secrets={"admin_key": "secret"},
        )
        assert isinstance(result3, dict)
        assert result3["data"] is not None
        assert isinstance(result3["data"], dict)
        assert result3["data"]["type"] == "admin"

    def test_none_secrets_not_injected(self, app: CogniteApp, mock_client: CogniteClient):
        """Test that None secrets are not injected even if handler declares the parameter."""
        call_count = {"count": 0}

        @app.get("/items/{item_id}")
        def get_item(client: CogniteClient, secrets: Mapping[str, str] | None, item_id: int) -> ItemResponse:
            """Handler that accepts optional secrets."""
            call_count["count"] += 1
            # When secrets is None, the parameter should be omitted if not declared
            # But if declared with Optional type, it could be None
            return ItemResponse(
                id=item_id,
                name="Test",
                price=99.99,
                has_secrets=secrets is not None,
                has_call_info=False,
            )

        handle = create_function_handle(app)

        # Call without secrets
        result = handle(
            client=mock_client,
            data={"path": "/items/123", "method": "GET"},
            secrets=None,
        )

        assert isinstance(result, dict)
        assert result["data"] is not None
        assert isinstance(result["data"], dict)
        assert result["success"] is True
        assert call_count["count"] == 1
