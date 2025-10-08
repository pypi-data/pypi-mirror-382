"""
Application Handlers.

Application Handlers are the wrappers to create an aiohttp Application \
    as subApp and can be added to the main application.
"""
from .base import BaseAppHandler

__all__ = ["BaseAppHandler"]
