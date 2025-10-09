"""WebSocket server wrapper for MCP protocol.

This module provides a WebSocket server that wraps the Core SDK's MCP server
to handle WebSocket connections and route them to the MCP protocol handler.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Set

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class MCPWebSocketServer:
    """WebSocket server wrapper for MCP protocol handling."""

    def __init__(self, mcp_server, host: str = "0.0.0.0", port: int = 3001):
        """Initialize WebSocket server wrapper.

        Args:
            mcp_server: Core SDK MCP server instance
            host: Host to bind to
            port: Port to bind to
        """
        self.mcp_server = mcp_server
        self.host = host
        self.port = port
        self._server = None
        self._clients: Set[WebSocketServerProtocol] = set()

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a WebSocket client connection."""
        self._clients.add(websocket)
        logger.info(f"New WebSocket client connected from {websocket.remote_address}")

        try:
            async for message in websocket:
                try:
                    # Parse JSON-RPC message
                    request = json.loads(message)

                    # Handle different MCP methods
                    method = request.get("method", "")
                    params = request.get("params", {})
                    request_id = request.get("id")

                    response = await self.handle_mcp_request(method, params, request_id)

                    # Send response
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                            "data": str(e),
                        },
                        "id": None,
                    }
                    await websocket.send(json.dumps(error_response))

                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e),
                        },
                        "id": request.get("id") if "request" in locals() else None,
                    }
                    await websocket.send(json.dumps(error_response))

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket client disconnected")
        finally:
            self._clients.remove(websocket)

    async def handle_mcp_request(
        self, method: str, params: Dict[str, Any], request_id: Optional[int]
    ) -> Dict[str, Any]:
        """Handle an MCP protocol request.

        Args:
            method: MCP method name
            params: Method parameters
            request_id: JSON-RPC request ID

        Returns:
            JSON-RPC response
        """
        try:
            # Route to appropriate handler based on method
            if method == "initialize":
                result = {
                    "protocolVersion": "1.0",
                    "capabilities": {"tools": True, "resources": True, "prompts": True},
                }

            elif method == "tools/list":
                # Get tools from MCP server
                tools = []
                if hasattr(self.mcp_server, "_tools"):
                    for name, tool in self.mcp_server._tools.items():
                        tools.append(
                            {
                                "name": name,
                                "description": getattr(
                                    tool, "__doc__", f"Tool: {name}"
                                ),
                                "inputSchema": {"type": "object", "properties": {}},
                            }
                        )
                result = {"tools": tools}

            elif method == "tools/call":
                # Execute tool
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                if (
                    hasattr(self.mcp_server, "_tools")
                    and tool_name in self.mcp_server._tools
                ):
                    tool_func = self.mcp_server._tools[tool_name]
                    # Execute tool (simplified - real implementation would be more complex)
                    tool_result = await self._execute_tool(tool_func, tool_args)
                    result = {
                        "content": [{"type": "text", "text": json.dumps(tool_result)}]
                    }
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

            elif method == "resources/list":
                # Get resources from MCP server
                resources = []
                if hasattr(self.mcp_server, "_resources"):
                    for pattern, resource in self.mcp_server._resources.items():
                        resources.append(
                            {
                                "uri": pattern,
                                "name": pattern,
                                "description": getattr(
                                    resource, "__doc__", f"Resource: {pattern}"
                                ),
                            }
                        )
                result = {"resources": resources}

            elif method == "resources/read":
                # Read resource
                uri = params.get("uri")

                if hasattr(self.mcp_server, "_resources"):
                    # Find matching resource handler
                    for pattern, handler in self.mcp_server._resources.items():
                        if self._matches_pattern(uri, pattern):
                            resource_data = await self._execute_resource(handler, uri)
                            result = {
                                "contents": [
                                    {
                                        "uri": uri,
                                        "mimeType": resource_data.get(
                                            "mimeType", "text/plain"
                                        ),
                                        "text": resource_data.get("content", ""),
                                    }
                                ]
                            }
                            break
                    else:
                        raise ValueError(f"Unknown resource: {uri}")
                else:
                    raise ValueError("No resources available")

            else:
                # Unknown method
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Unknown method: {method}",
                    },
                    "id": request_id,
                }

            # Return success response
            return {"jsonrpc": "2.0", "result": result, "id": request_id}

        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error", "data": str(e)},
                "id": request_id,
            }

    async def _execute_tool(self, tool_func, args: Dict[str, Any]) -> Any:
        """Execute a tool function."""
        # Simple execution - real implementation would handle async/sync properly
        if asyncio.iscoroutinefunction(tool_func):
            return await tool_func(**args)
        else:
            return tool_func(**args)

    async def _execute_resource(self, handler, uri: str) -> Dict[str, Any]:
        """Execute a resource handler."""
        # Simple execution - real implementation would handle async/sync properly
        if asyncio.iscoroutinefunction(handler):
            return await handler(uri)
        else:
            return handler(uri)

    def _matches_pattern(self, uri: str, pattern: str) -> bool:
        """Check if URI matches a pattern."""
        # Simple pattern matching - real implementation would be more sophisticated
        if pattern.endswith("*"):
            return uri.startswith(pattern[:-1])
        return uri == pattern

    async def start(self):
        """Start the WebSocket server."""
        self._server = await websockets.serve(self.handle_client, self.host, self.port)
        logger.info(f"MCP WebSocket server started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("MCP WebSocket server stopped")
