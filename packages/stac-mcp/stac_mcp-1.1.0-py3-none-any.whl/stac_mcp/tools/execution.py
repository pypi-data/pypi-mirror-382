"""Tool execution logic separated from server module.

Each handler returns a list of TextContent objects to remain compatible
with existing tests. Later enhancements (JSON mode, error abstraction)
can hook here centrally.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Iterable
from typing import Any, NoReturn

from mcp.types import TextContent

from stac_mcp import server as _server
from stac_mcp.observability import instrument_tool_execution, record_tool_result_size
from stac_mcp.tools.client import STACClient
from stac_mcp.tools.estimate_data_size import handle_estimate_data_size
from stac_mcp.tools.get_aggregations import handle_get_aggregations
from stac_mcp.tools.get_collection import handle_get_collection
from stac_mcp.tools.get_conformance import handle_get_conformance
from stac_mcp.tools.get_item import handle_get_item
from stac_mcp.tools.get_queryables import handle_get_queryables
from stac_mcp.tools.get_root import handle_get_root
from stac_mcp.tools.search_collections import handle_search_collections
from stac_mcp.tools.search_items import handle_search_items
from stac_mcp.tools.transactions import (
    handle_create_collection,
    handle_create_item,
    handle_delete_collection,
    handle_delete_item,
    handle_update_collection,
    handle_update_item,
)

logger = logging.getLogger(__name__)


Handler = Callable[
    [STACClient, dict[str, Any]],
    list[TextContent] | dict[str, Any],
]


_TOOL_HANDLERS: dict[str, Handler] = {
    "search_collections": handle_search_collections,
    "get_collection": handle_get_collection,
    "search_items": handle_search_items,
    "get_item": handle_get_item,
    "estimate_data_size": handle_estimate_data_size,
    "get_root": handle_get_root,
    "get_conformance": handle_get_conformance,
    "get_queryables": handle_get_queryables,
    "get_aggregations": handle_get_aggregations,
    "create_item": handle_create_item,
    "update_item": handle_update_item,
    "delete_item": handle_delete_item,
    "create_collection": handle_create_collection,
    "update_collection": handle_update_collection,
    "delete_collection": handle_delete_collection,
}


def _raise_unknown_tool(name: str) -> NoReturn:
    """Raise a standardized error for unknown tool names."""
    _tools = list(_TOOL_HANDLERS.keys())
    msg = f"Unknown tool: {name}. Available tools: {_tools}"
    raise ValueError(msg)


def _as_text_content_list(result: Any) -> list[TextContent]:
    """Normalize arbitrary handler results into a list of TextContent."""

    def _single(value: Any) -> TextContent:
        if isinstance(value, TextContent):
            return value
        if isinstance(value, str):
            return TextContent(type="text", text=value)
        try:
            serialized = json.dumps(value, separators=(",", ":"))
        except TypeError:
            serialized = str(value)
        return TextContent(type="text", text=serialized)

    if result is None:
        return []
    if isinstance(result, TextContent):
        return [result]
    if isinstance(result, list):
        normalized: list[TextContent] = []
        for item in result:
            normalized.append(_single(item))
        return normalized
    if isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict)):
        return [_single(item) for item in result]
    return [_single(result)]


async def execute_tool(
    tool_name: str,
    handler: Handler | None = None,
    client: STACClient | None = None,
    arguments: dict[str, Any] | None = None,
):
    """Execute a tool handler with optional overrides for tests.

    Parameters mirror the comprehensive execution tests: when *handler* or
    *client* are provided they are used directly, otherwise the registered
    handler and shared client are used. The return value is always normalized
    to a ``list[TextContent]`` for compatibility with existing tooling.
    """

    # Backward compatibility: legacy callers passed only (tool_name, arguments).
    if handler is not None and not callable(handler):
        if arguments is None:
            arguments = dict(handler)
        handler = None
    if (
        client is not None
        and not isinstance(client, STACClient)
        and isinstance(client, dict)
    ):
        if arguments is None:
            arguments = dict(client)
        client = None

    arguments = dict(arguments or {})
    if handler is None:
        handler = _TOOL_HANDLERS.get(tool_name)
        if handler is None:
            _raise_unknown_tool(tool_name)
    catalog_url = arguments.get("catalog_url")
    if client is None:
        client = STACClient(catalog_url) if catalog_url else _server.stac_client

    output_format = arguments.get("output_format", "text")
    instrumented = instrument_tool_execution(
        tool_name,
        catalog_url,
        handler,
        client,
        arguments,
    )
    raw_result = instrumented.value
    if output_format == "json":
        if isinstance(raw_result, list):
            normalized = _as_text_content_list(raw_result)
            payload = {
                "mode": "text_fallback",
                "content": [item.text for item in normalized],
            }
        else:
            payload = {"mode": "json", "data": raw_result}
        payload_text = json.dumps(payload, separators=(",", ":"))
        record_tool_result_size(tool_name, len(payload_text.encode("utf-8")))
        return [TextContent(type="text", text=payload_text)]
    normalized = _as_text_content_list(raw_result)
    total_bytes = sum(len(item.text.encode("utf-8")) for item in normalized)
    record_tool_result_size(tool_name, total_bytes)
    return normalized
