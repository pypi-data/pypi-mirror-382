"""Base middleware classes and utilities for the Velithon framework."""

from __future__ import annotations

import typing
from abc import ABC, abstractmethod

from velithon.datastructures import Protocol, Scope


class BaseHTTPMiddleware(ABC):
    """Base class for HTTP-only middleware that provides common functionality.

    This class handles the common pattern of:
    1. Checking if the request is HTTP
    2. Passing through non-HTTP requests unchanged
    3. Providing abstract methods for HTTP-specific processing
    """

    def __init__(self, app: typing.Callable[[Scope, Protocol], typing.Awaitable[None]]):
        """Initialize the middleware with the given RSGI application.

        Args:
            app: The next RSGI application in the middleware chain.

        """
        self.app = app

    async def __call__(self, scope: Scope, protocol: Protocol) -> None:
        """Handle incoming requests and delegate to HTTP-specific processing if applicable.

        Args:
            scope: The request scope containing protocol and request information.
            protocol: The protocol handler for the request.

        """  # noqa: E501
        if scope.proto != 'http':
            return await self.app(scope, protocol)

        return await self.process_http_request(scope, protocol)

    @abstractmethod
    async def process_http_request(self, scope: Scope, protocol: Protocol) -> None:
        """Process an HTTP request. Must be implemented by subclasses.

        Args:
            scope: The request scope
            protocol: The protocol handler

        """
        raise NotImplementedError()


class PassThroughMiddleware(BaseHTTPMiddleware):
    """Base class for middleware that processes requests but always calls the next app.

    This is useful for middleware that needs to:
    - Modify request/response headers
    - Log requests
    - Perform authentication checks that don't block requests
    """

    async def process_http_request(self, scope: Scope, protocol: Protocol) -> None:
        """Process the HTTP request and always call the next app."""
        await self.before_request(scope, protocol)
        await self.app(scope, protocol)
        await self.after_request(scope, protocol)

    async def before_request(self, scope: Scope, protocol: Protocol) -> None:
        """Call before the request is processed by the next app."""
        pass

    async def after_request(self, scope: Scope, protocol: Protocol) -> None:
        """Call after the request is processed by the next app."""
        pass


class ConditionalMiddleware(BaseHTTPMiddleware):
    """Base class for middleware that may short-circuit request processing.

    This is useful for middleware that needs to:
    - Return early responses (auth failures, CORS preflight, etc.)
    - Conditionally process requests
    """

    async def process_http_request(self, scope: Scope, protocol: Protocol) -> None:
        """Process the HTTP request and conditionally call the next app.

        Args:
            scope: The request scope
            protocol: The protocol handler

        """
        should_continue = await self.should_process_request(scope, protocol)
        if should_continue:
            await self.app(scope, protocol)

    @abstractmethod
    async def should_process_request(self, scope: Scope, protocol: Protocol) -> bool:
        """Determine if the request should continue to the next app.

        Returns:
            True if the request should continue, False if it was handled

        """
        raise NotImplementedError()


class ProtocolWrapperMiddleware(BaseHTTPMiddleware):
    """Base class for middleware that wraps the protocol to intercept responses.

    This is useful for middleware that needs to:
    - Modify response data
    - Set additional headers based on response
    - Handle session cookies
    """

    async def process_http_request(self, scope: Scope, protocol: Protocol) -> None:
        """Process the HTTP request and wrap the protocol for response interception."""
        wrapped_protocol = self.create_wrapped_protocol(scope, protocol)
        await self.app(scope, wrapped_protocol)

    @abstractmethod
    def create_wrapped_protocol(self, scope: Scope, protocol: Protocol) -> Protocol:
        """Create a wrapped protocol that intercepts response methods.

        Args:
            scope: The request scope
            protocol: The original protocol

        Returns:
            A wrapped protocol instance

        """
        raise NotImplementedError()
