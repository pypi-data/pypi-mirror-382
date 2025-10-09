"""
Terminal MCP Server - Setup for PyPI distribution
"""
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="terminal-mcp-server",
    version="1.0.1",
    description="Smart terminal session management for AI assistants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kanniganfan/terminal-mcp",
    author="kanniganfan",
    author_email="cao673100060@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="mcp, terminal, ai, cursor, automation, async",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "psutil>=5.9.6",
    ],
    entry_points={
        "console_scripts": [
            "terminal-mcp-server=terminal_mcp_server.server:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/kanniganfan/terminal-mcp/issues",
        "Source": "https://github.com/kanniganfan/terminal-mcp",
    },
)

