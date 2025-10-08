"""
Setup script for AI Cogence MCP Server
This is a compatibility shim for older pip versions.
Modern installations should use pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="ai-cogence-mcp-server",
    packages=find_packages(),
    include_package_data=True,
)

