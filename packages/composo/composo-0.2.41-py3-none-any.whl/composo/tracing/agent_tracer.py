import contextvars
import json
import uuid
from collections import OrderedDict
from functools import wraps
from typing import Callable, List, Optional, Union

from openai.types.chat.chat_completion import ChatCompletion
from opentelemetry import context, trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import Span

from ..models.api_types import (
    AgentInstance,
    LLMInteraction,
    MultiAgentTrace,
)
from .parsers import OpenAISpanParser, AnthropicSpanParser

# Constants
INTERACTION_TYPE_LLM = "INTERACTION_TYPE_LLM_INTERACTION"
INTERACTION_TYPE_AGENT = "INTERACTION_TYPE_AGENT_INTERACTION"
INTERACTION_TYPE = "INTERACTION_TYPE"
AgentInstanceId = str


class AgentTracer:
    """Context manager for capturing and segmenting trace spans into agent instances"""

    _active_segmenter: contextvars.ContextVar[Optional["AgentTracer"]] = (
        contextvars.ContextVar("active_segmenter", default=None)
    )

    def __init__(self, name: Optional[str] = None, agent_id: Optional[str] = None):
        # Core identifiers
        self.agent_name = name or f"agent_{uuid.uuid4().hex[:8]}"
        self.agent_id = agent_id or str(uuid.uuid4())
        self.id = self.agent_id  # Alias for compatibility

        # Span tracking - use OrderedDict to merge spans dict and sequence list
        self.spans: OrderedDict[str, Span] = OrderedDict()

        # Hierarchy tracking
        self.parent_segmenter = self.get_active()
        self.child_segmenters: List["AgentTracer"] = []

        # Context management
        self._token = None
        self._span_token = None
        self.current_span = None

    def __enter__(self):
        """Start the segmenter context"""
        self._token = self._active_segmenter.set(self)

        # Create agent span manually to control when it ends
        tracer = trace.get_tracer(__name__)
        self.current_span = tracer.start_span(
            name=f"agent-{self.agent_name}",
            context=context.get_current(),
            attributes={
                "agent.id": self.agent_id,
                INTERACTION_TYPE: INTERACTION_TYPE_AGENT,
            },
        )

        # Set as current span
        self._span_token = context.attach(trace.set_span_in_context(self.current_span))

        # Register with parent
        if self.parent_segmenter:
            self.parent_segmenter.add_span_details(self.current_span)
            self.parent_segmenter.child_segmenters.append(self)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the segmenter context"""
        if self.current_span:
            # Set attributes for debugging before ending the span
            self.current_span.set_attribute(
                "segmenter.interaction_span_ids", json.dumps(list(self.spans.keys()))
            )
            self.current_span.set_attribute(
                "segmenter.interaction_count", len(self.spans)
            )
            self.current_span.set_attribute("segmenter.agent_id", self.agent_id)
            self.current_span.set_attribute("segmenter.agent_name", self.agent_name)

            # End the span manually
            self.current_span.end()

            # Detach from context
            if hasattr(self, "_span_token"):
                context.detach(self._span_token)

        if self._token:
            self._active_segmenter.reset(self._token)

    def add_span_details(self, span: Span):
        """Store span details when span ends"""
        span_id = format(span.get_span_context().span_id, "032x")
        # OrderedDict automatically maintains insertion order
        self.spans[span_id] = span

    def get_raw_spans(self) -> List[Span]:
        """Get the raw spans captured during this segmenter's lifetime"""
        return list(self.spans.values())

    def get_agent_instance(self) -> AgentInstance:
        """Build agent instance from captured spans"""
        interactions: List[Union[LLMInteraction, AgentInstanceId]] = []

        # Use OrderedDict keys() to iterate in insertion order
        for span_id in self.spans.keys():
            span = self.spans[span_id]

            # Check if span has attributes (skip NonRecordingSpan)
            if not hasattr(span, "attributes") or span.attributes is None:
                continue

            interaction_type = span.attributes.get(INTERACTION_TYPE, "unknown")

            if interaction_type == INTERACTION_TYPE_LLM:
                # Handle LLM interaction using appropriate parser based on span attributes
                llm_system = span.attributes.get("llm.system")

                # Parser mapping based on LLM system
                parser_map = {
                    "openai": OpenAISpanParser,
                    "anthropic": AnthropicSpanParser,
                }

                parser_class = parser_map.get(llm_system)
                if parser_class:
                    parser = parser_class()
                    if parser.can_parse(span):
                        llm_interaction = parser.parse(span)
                        if llm_interaction:
                            interactions.append(llm_interaction)
            elif interaction_type == INTERACTION_TYPE_AGENT:
                # Handle child agent
                agent_id = span.attributes.get("agent.id", "unknown")
                interactions.append(agent_id)

        return AgentInstance(
            id=self.agent_id, name=self.agent_name, interactions=interactions
        )

    def get_multi_agent_trace(self) -> MultiAgentTrace:
        """Create multi-agent trace with all agent instances"""
        agent_instances = {}

        def collect_instances(segmenter: "AgentTracer"):
            instance = segmenter.get_agent_instance()
            agent_instances[instance.id] = instance
            for child in segmenter.child_segmenters:
                collect_instances(child)

        collect_instances(self)

        return MultiAgentTrace(
            root_agent_instance_id=self.agent_id,
            agent_instance_by_id=agent_instances,
        )

    @property
    def trace(self) -> MultiAgentTrace:
        """Property to get multi-agent trace - convenience wrapper for get_multi_agent_trace()"""
        return self.get_multi_agent_trace()

    @classmethod
    def get_active(cls) -> Optional["AgentTracer"]:
        """Get the currently active segmenter"""
        return cls._active_segmenter.get()


def agent_tracer(name: Optional[str] = None) -> Callable:
    """Decorator to wrap a function with an AgentTracer context.

    Usage:
        @agent_tracer(name="my_agent")
        def my_function():
            # function code here
            pass

    Args:
        name: Optional name for the agent. If not provided, uses function name.

    Returns:
        Decorated function that runs within an AgentTracer context.
    """

    def decorator(func: Callable) -> Callable:
        agent_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            with AgentTracer(name=agent_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


class GlobalSpanProcessor(SpanProcessor):
    """Span processor that captures spans for active AgentTracer instances"""

    def on_start(self, span: Span, parent_context: Optional[Context] = None):
        """Mark LLM spans when started"""
        active = AgentTracer.get_active()
        if active and self._is_llm_span(span):
            span.set_attribute(INTERACTION_TYPE, INTERACTION_TYPE_LLM)

    def on_end(self, span: Span):
        """Capture LLM spans when ended"""
        active = AgentTracer.get_active()
        if active and span.attributes.get(INTERACTION_TYPE) == INTERACTION_TYPE_LLM:
            active.add_span_details(span)

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True

    @staticmethod
    def _is_llm_span(span: Span) -> bool:
        """Check if this is an LLM span that can be parsed by available parsers"""
        if not span.attributes:
            return False

        # Check if this is an LLM span based on span kind and system
        span_kind = span.attributes.get("openinference.span.kind")
        llm_system = span.attributes.get("llm.system")

        return span_kind == "LLM" and llm_system in ["openai", "anthropic"]
