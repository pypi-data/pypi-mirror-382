"""
Base parser class for converting OpenTelemetry spans to LLM interactions.
"""

from abc import ABC, abstractmethod
from typing import Optional

from opentelemetry.trace import Span

from ...models.api_types import LLMInteraction


class BaseSpanParser(ABC):
    """Abstract base class for span parsers.

    This class defines the interface that all span parsers must implement.
    Each parser is responsible for converting spans from a specific LLM provider
    or tracing system into standardized LLMInteraction objects.
    """

    def __init__(self, name: Optional[str] = None):
        """Initialize the parser.

        Args:
            name: Optional name for the parser. If not provided, uses class name.
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def can_parse(self, span: Span) -> bool:
        """Check if this parser can handle the given span.

        Args:
            span: The OpenTelemetry span to check

        Returns:
            True if this parser can handle the span, False otherwise
        """
        pass

    @abstractmethod
    def parse(self, span: Span) -> Optional[LLMInteraction]:
        """Parse span into LLMInteraction.

        Args:
            span: The OpenTelemetry span to parse

        Returns:
            Parsed LLMInteraction object, or None if parsing failed
        """
        pass
