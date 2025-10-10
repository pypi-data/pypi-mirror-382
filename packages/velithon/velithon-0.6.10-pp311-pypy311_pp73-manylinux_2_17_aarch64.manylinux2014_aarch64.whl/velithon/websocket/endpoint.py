"""WebSocket endpoint handling for Velithon framework.

This module provides WebSocket endpoint functionality including route
handling, connection management, and WebSocket-specific operations.
"""

from __future__ import annotations

import typing

from velithon.datastructures import Protocol, Scope
from velithon.websocket.connection import WebSocket, WebSocketDisconnect


class WebSocketEndpoint:
    """Base class for WebSocket endpoints."""

    def __init__(self, scope: Scope, protocol: Protocol) -> None:
        """Initialize the WebSocketEndpoint with the given scope and protocol.

        Args:
            scope (Scope): The connection scope, must be of protocol 'websocket'.
            protocol (Protocol): The protocol instance for the connection.

        """
        assert scope.proto == 'websocket'
        self.scope = scope
        self.protocol = protocol

    async def __call__(self, websocket: WebSocket) -> None:
        """Handle the WebSocket connection."""
        await self.on_connect(websocket)

        try:
            await websocket.accept()
            await self.on_connect_complete(websocket)

            # Keep connection alive and handle messages
            while True:
                try:
                    await self.receive_and_process(websocket)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    await self.on_error(websocket, e)
                    break

        except Exception as e:
            await self.on_error(websocket, e)
        finally:
            await self.on_disconnect(websocket)

    async def receive_and_process(self, websocket: WebSocket) -> None:
        """Receive and process a message from the WebSocket."""
        # This can be overridden by subclasses for custom message handling
        message = await websocket.receive_text()
        await self.on_receive(websocket, message)

    async def on_connect(self, websocket: WebSocket) -> None:
        """Handle client connection to the WebSocket."""
        pass

    async def on_connect_complete(self, websocket: WebSocket) -> None:
        """Call after the WebSocket connection is accepted."""
        pass

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        """Handle when a message is received from the WebSocket."""
        pass

    async def on_disconnect(self, websocket: WebSocket) -> None:
        """Call when the WebSocket connection is closed."""
        pass

    async def on_error(self, websocket: WebSocket, error: Exception) -> None:
        """Call when an error occurs in the WebSocket connection."""
        pass


def websocket_response(
    func: typing.Callable[[WebSocket], typing.Awaitable[None]],
) -> typing.Callable[[Scope, Protocol], typing.Awaitable[None]]:
    """Convert a WebSocket handler function into a WebSocket application.

    Args:
        func: A function that takes a WebSocket and returns None

    Returns:
        A WebSocket application function

    """

    async def app(scope: Scope, protocol: Protocol) -> None:
        websocket = WebSocket(scope, protocol)
        await func(websocket)

    return app


class WebSocketRoute:
    """WebSocket route for handling WebSocket connections."""

    def __init__(
        self,
        path: str,
        endpoint: typing.Callable[[WebSocket], typing.Awaitable[None]]
        | type[WebSocketEndpoint],
        name: str | None = None,
    ) -> None:
        """Initialize a WebSocketRoute with the given path, endpoint, and optional name.

        Args:
            path (str): The route path for the WebSocket connection.
            endpoint (Callable or type): The handler function or class for the WebSocket.
            name (str, optional): The name of the route. Defaults to the endpoint's name or 'websocket'.

        """  # noqa: E501
        self.path = path
        self.endpoint = endpoint
        self.name = name or getattr(endpoint, '__name__', 'websocket')

        # Prepare the application
        if isinstance(endpoint, type) and issubclass(endpoint, WebSocketEndpoint):
            # Class-based endpoint
            async def app(scope: Scope, protocol: Protocol) -> None:
                websocket = WebSocket(scope, protocol)
                endpoint_instance = endpoint(scope, protocol)
                await endpoint_instance(websocket)

            self.app = app
        else:
            # Function-based endpoint
            self.app = websocket_response(endpoint)

    def matches(self, scope: Scope) -> bool:
        """Check if this route matches the given scope."""
        return scope.proto == 'websocket' and scope.path == self.path

    async def handle(self, scope: Scope, protocol: Protocol) -> None:
        """Handle the WebSocket connection."""
        await self.app(scope, protocol)
