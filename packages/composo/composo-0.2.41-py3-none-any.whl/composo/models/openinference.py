"""
Minimal OpenInference data model for quick span attribute mapping.

This is a simplified model that directly maps from span attributes
and can be easily converted to existing LLMInteraction format.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class OpenInferenceSpanData(BaseModel):
    """Minimal OpenInference span data model."""

    # Core span attributes
    span_kind: Optional[str] = None
    llm_system: Optional[str] = None
    llm_model_name: Optional[str] = None

    # Input/Output data (raw JSON strings)
    input_value: Optional[str] = None
    output_value: Optional[str] = None

    # Token counts
    token_count_prompt: Optional[int] = None
    token_count_completion: Optional[int] = None

    # Costs
    cost_prompt: Optional[float] = None
    cost_completion: Optional[float] = None
    cost_total: Optional[float] = None

    @classmethod
    def from_span_attributes(
        cls, attributes: Dict[str, Any]
    ) -> "OpenInferenceSpanData":
        """Create from span attributes dict."""
        return cls(
            span_kind=attributes.get("openinference.span.kind"),
            llm_system=attributes.get("llm.system"),
            llm_model_name=attributes.get("llm.model_name"),
            input_value=attributes.get("input.value"),
            output_value=attributes.get("output.value"),
            token_count_prompt=attributes.get("llm.token_count.prompt"),
            token_count_completion=attributes.get("llm.token_count.completion"),
            cost_prompt=attributes.get("llm.cost.prompt"),
            cost_completion=attributes.get("llm.cost.completion"),
            cost_total=attributes.get("llm.cost.total"),
        )
