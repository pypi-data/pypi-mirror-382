"""
Common Pyloid context classes for server adapters.

This module provides common data structures and utilities for handling Pyloid
context across different web frameworks.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pyloid import Pyloid
    from pyloid.browser_window import BrowserWindow


class PyloidContext:
    """
    Context class for Pyloid application integration.

    This class encapsulates the Pyloid application instance and the current browser
    window context, making them easily accessible within web framework handlers.

    Attributes
    ----------
    pyloid : Pyloid
        The main Pyloid application instance.
    window : BrowserWindow
        The current browser window instance associated with the request.
    """

    def __init__(self, pyloid: Optional["Pyloid"] = None, window: Optional["BrowserWindow"] = None):
        """
        Initialize PyloidContext with Pyloid application and window instances.

        Parameters
        ----------
        pyloid : Pyloid, optional
            The Pyloid application instance. Defaults to None.
        window : BrowserWindow, optional
            The browser window instance. Defaults to None.
        """
        self.pyloid: Optional["Pyloid"] = pyloid
        self.window: Optional["BrowserWindow"] = window
