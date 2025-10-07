"""
Span parsers for different LLM providers and tracing systems.

This module provides a flexible parser system for converting OpenTelemetry spans
into structured LLM interactions. Each parser handles a specific provider or format.
"""

from .base import BaseSpanParser
from .openai import OpenAISpanParser
from .anthropic import AnthropicSpanParser

__all__ = [
    "BaseSpanParser",
    "OpenAISpanParser",
    "AnthropicSpanParser",
]
