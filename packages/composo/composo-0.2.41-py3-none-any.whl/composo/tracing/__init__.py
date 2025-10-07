"""
Composo tracing module for agent and LLM interaction tracking.
"""

from enum import Enum
from functools import wraps
from typing import Optional, Union, List, Callable, Any

from .agent_tracer import AgentTracer
from .setup import init


class Instruments(Enum):
    """Supported instrumentation types for Composo tracing."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ComposoTracer:
    """Main tracer class for initializing Composo tracing."""

    @staticmethod
    def init(instruments: Optional[Union[List[Instruments], Instruments]] = None):
        """
        Initialize Composo tracing with specified instruments.

        Args:
            instruments: List of Instruments enum values or single Instruments value.
                        Currently supports: Instruments.OPENAI, Instruments.ANTHROPIC
        """
        if instruments is None:
            return init(instrument=None)
        elif isinstance(instruments, Instruments):
            return init(instrument=instruments)
        else:
            # Handle list
            return init(instrument=instruments)


# AgentTracer is now the main class, no wrapper needed


def agent_tracer(name: Optional[str] = None, agent_id: Optional[str] = None):
    """
    Decorator for tracing agent functions.

    Args:
        name: Optional name for the agent. If not provided, will use function name.
        agent_id: Optional ID for the agent. If not provided, will generate one.

    Returns:
        Decorated function that runs within an AgentTracer context.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            agent_name = name or func.__name__
            with AgentTracer(name=agent_name, agent_id=agent_id):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Export all public components
__all__ = [
    "ComposoTracer",
    "Instruments",
    "AgentTracer",
    "agent_tracer",
]
