"""
API package initialization
"""

try:
    from .server import create_app, app
    __all__ = ["create_app", "app"]
except ImportError:
    __all__ = []
