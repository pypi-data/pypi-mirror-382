from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from .agent_tracer import GlobalSpanProcessor
from typing import List, Union, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)


def init(
    instrument: Optional[Union[List["Instruments"], "Instruments"]] = None,
) -> TracerProvider:
    """
    Initialize Composo tracing with OpenTelemetry and optional auto-instrumentation.

    Checks for existing tracer provider and integrates with it instead of overriding.
    This method is idempotent - calling it multiple times will not duplicate setup.

    Args:
        instrument: List of Instruments enum values or single Instruments value.
                   Currently supports: Instruments.OPENAI, Instruments.ANTHROPIC
                   Pass None to skip instrumentation.

    Returns:
        TracerProvider: The configured tracer provider
    """
    # Reuse existing SDK tracer provider if present; otherwise create one
    existing_provider = trace.get_tracer_provider()
    if isinstance(existing_provider, TracerProvider):
        logger.info("Using existing tracer provider")
        tracer_provider = existing_provider
    else:
        logger.info("Creating new tracer provider")
        resource = Resource.create()
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

    # Check if GlobalSpanProcessor is already added to avoid duplicates
    existing_processors = [
        p
        for p in tracer_provider._active_span_processor._span_processors
        if isinstance(p, GlobalSpanProcessor)
    ]

    if not existing_processors:
        # Add our span processor to the tracer provider
        tracer_provider.add_span_processor(GlobalSpanProcessor())
        logger.info("Added GlobalSpanProcessor to tracer provider")
    else:
        logger.info("GlobalSpanProcessor already exists, skipping addition")

    # Handle instrumentation
    if instrument is not None:
        # Convert enum values to strings
        if isinstance(instrument, list):
            instrument_names = [inst.value for inst in instrument]
        else:
            instrument_names = instrument.value
        _setup_instrumentation(instrument_names, tracer_provider)

    return tracer_provider


def _setup_instrumentation(
    instrument: Union[List[str], str], tracer_provider: TracerProvider
):
    """
    Setup auto-instrumentation for specified modules.

    Args:
        instrument: List of modules to instrument or single module string
        tracer_provider: The tracer provider to use for instrumentation
    """
    # Convert single string to list
    if isinstance(instrument, str):
        instrument = [instrument]

    for module in instrument:
        if module.lower() == "openai":
            _instrument_openai(tracer_provider)
        elif module.lower() == "anthropic":
            _instrument_anthropic(tracer_provider)
        else:
            logger.warning(f"Instrumentation for '{module}' is not supported yet")


def _instrument_openai(tracer_provider: TracerProvider):
    """Setup OpenAI instrumentation using openinference."""
    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor

        # Check if already instrumented
        if not OpenAIInstrumentor().is_instrumented_by_opentelemetry:
            OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
            logger.info("OpenAI instrumentation setup successful")
        else:
            logger.info("OpenAI is already instrumented")

    except ImportError:
        logger.error(
            "OpenAI instrumentation failed: openinference-instrumentation-openai not found. "
            "Install with: pip install openinference-instrumentation-openai"
        )
        raise
    except Exception as e:
        logger.error(f"OpenAI instrumentation failed: {e}")
        raise


def _instrument_anthropic(tracer_provider: TracerProvider):
    """Setup Anthropic instrumentation using openinference."""
    try:
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        # Check if already instrumented
        if not AnthropicInstrumentor().is_instrumented_by_opentelemetry:
            AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)
            logger.info("Anthropic instrumentation setup successful")
        else:
            logger.info("Anthropic is already instrumented")

    except ImportError:
        logger.error(
            "Anthropic instrumentation failed: openinference-instrumentation-anthropic not found. "
            "Install with: pip install openinference-instrumentation-anthropic"
        )
        raise
    except Exception as e:
        logger.error(f"Anthropic instrumentation failed: {e}")
        raise
