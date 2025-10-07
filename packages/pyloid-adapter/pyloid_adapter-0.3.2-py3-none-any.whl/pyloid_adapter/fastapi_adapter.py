from fastapi import FastAPI, Request
from .base_adapter import BaseAdapter
from .context import PyloidContext
from typing import Callable

class FastAPIAdapter(BaseAdapter):
    """
    FastAPI adapter for Pyloid application integration.

    This adapter class serves as the main integration point between Pyloid applications
    and FastAPI web servers. It provides FastAPI dependency injection for Pyloid
    context and manages the server lifecycle.

    The adapter automatically configures CORS to allow all origins by default for
    seamless integration with web applications.

    The adapter supports FastAPI's dependency injection system for context injection.
    """

    def __init__(self, start: Callable[[FastAPI, str, int], None], setup_cors: Callable[[], None]):
        """
        Initialize the FastAPI adapter.

        Parameters
        ----------
        start : Callable[[FastAPI, str, int], None]
            Function that starts the server. Should handle app, host, port parameters.
        setup_cors : Callable[[], None]
            Function that sets up CORS configuration for the web framework.
        """
        super().__init__(start, setup_cors)
        
    def get_context(self, request: Request) -> PyloidContext:
        """
        Create PyloidContext from an HTTP request.

        This method extracts the window ID from the request headers and creates
        a PyloidContext instance with the appropriate Pyloid application and window.

        Parameters
        ----------
        request : Request
            The FastAPI Request object containing headers and metadata.

        Returns
        -------
        PyloidContext
            Context object containing Pyloid app and window instances.
        """
        window_id = request.headers.get("X-Pyloid-Window-Id")
        return super().get_context(window_id)