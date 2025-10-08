"""Typed Cognite Functions.

FastAPI-style framework for building type-safe Cognite Functions
with automatic OpenAPI schema generation and MCP integration.
"""

from ._version import __version__
from .app import CogniteApp, create_function_handle
from .introspection import create_introspection_app
from .logger import create_function_logger, get_function_logger
from .mcp import MCPApp, create_mcp_app
from .models import CogniteTypedError, CogniteTypedResponse, HTTPMethod
from .routing import Router, SortedRoutes, find_matching_route

__all__ = [
    "CogniteApp",
    "CogniteTypedError",
    "CogniteTypedResponse",
    "HTTPMethod",
    "MCPApp",
    "Router",
    "SortedRoutes",
    "__version__",
    "create_function_handle",
    "create_function_logger",
    "create_introspection_app",
    "create_mcp_app",
    "find_matching_route",
    "get_function_logger",
]
