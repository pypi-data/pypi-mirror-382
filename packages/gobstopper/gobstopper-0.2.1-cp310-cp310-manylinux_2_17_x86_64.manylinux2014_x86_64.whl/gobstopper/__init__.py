"""
Gobstopper Web Framework 🍬

Like Willy Wonka's Everlasting Gobstopper - a simple wrapper that delivers
a complete multi-course meal. Gobstopper wraps the raw power of RSGI into
a simple, Flask-like API while delivering everything you need.

A high-performance async web framework built on Granian's RSGI interface:
- 🍬 Simple wrapper around RSGI complexity
- ⚡ Flask-like API with RSGI performance
- 🔋 Complete batteries-included framework
- 🦀 Optional Rust acceleration
- 🎨 Familiar, ergonomic design

Features:
- Jinja2 templating with async support
- Intelligent background task system with DuckDB storage
- WebSocket support with room management
- Built-in security features
- Static file serving
- Middleware system
- CORS support
- Rate limiting
- Session management
"""

from .core.app import Gobstopper
from .http.request import Request
from .http.response import Response, JSONResponse, FileResponse, StreamResponse, redirect
from .http.helpers import jsonify, send_file, stream_template, abort, make_response, send_from_directory
from .http.notifications import notification, get_notifications, peek_notifications, clear_notifications
from .http.file_storage import FileStorage, secure_filename
from .http.errors import HTTPException, UnsupportedMediaType, BodyValidationError
from .http.routing import RouteHandler, use, register_converter
from .http.negotiation import negotiate, negotiate_response
from .http.sse import format_sse, SSEStream
from .websocket.connection import WebSocket
from .websocket.manager import WebSocketManager
from .tasks.queue import TaskPriority, TaskStatus, TaskInfo, TaskQueue
from .tasks.storage import TaskStorage
from .templates.engine import TemplateEngine
from .config import (
    Config,
    ServerConfig,
    SecurityConfig,
    CORSConfig,
    StaticFilesConfig,
    TemplateConfig,
    TaskConfig,
    RateLimitConfig,
    LoggingConfig,
    MetricsConfig,
)
from . import extensions as extensions  # re-export subpackage for convenience

__version__ = "0.2.1"
__author__ = "Gobstopper Framework Team"
__license__ = "MIT"

__all__ = [
    # Core
    "Gobstopper",
    "Request",
    "Response",
    "JSONResponse",
    "FileResponse",
    "StreamResponse",
    "redirect",

    # WebSocket
    "WebSocket",
    "WebSocketManager",

    # Tasks
    "TaskPriority",
    "TaskStatus",
    "TaskInfo",
    "TaskQueue",
    "TaskStorage",

    # Templates
    "TemplateEngine",

    # Configuration
    "Config",
    "ServerConfig",
    "SecurityConfig",
    "CORSConfig",
    "StaticFilesConfig",
    "TemplateConfig",
    "TaskConfig",
    "RateLimitConfig",
    "LoggingConfig",
    "MetricsConfig",

    # HTTP Helpers
    "jsonify",
    "send_file",
    "stream_template",
    "abort",
    "make_response",
    "send_from_directory",

    # File Upload
    "FileStorage",
    "secure_filename",

    # Notifications
    "notification",
    "get_notifications",
    "peek_notifications",
    "clear_notifications",

    # Errors
    "HTTPException",
    "UnsupportedMediaType",
    "BodyValidationError",

    # Routing
    "RouteHandler",
    "use",
    "register_converter",

    # Content Negotiation
    "negotiate",
    "negotiate_response",

    # Server-Sent Events
    "format_sse",
    "SSEStream",

    # Extensions
    "extensions",
]