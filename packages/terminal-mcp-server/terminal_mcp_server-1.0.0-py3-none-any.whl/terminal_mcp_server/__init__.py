"""Terminal MCP Server - Smart terminal session management for AI assistants"""

__version__ = "1.0.0"
__author__ = "kanniganfan"
__license__ = "MIT"

from .server import SessionManager, TerminalMCPServer

__all__ = ["SessionManager", "TerminalMCPServer", "__version__"]

