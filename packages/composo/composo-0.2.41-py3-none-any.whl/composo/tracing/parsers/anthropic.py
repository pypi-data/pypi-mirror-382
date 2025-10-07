"""Anthropic span parser for OpenInference traces."""

import json
import logging
from typing import Optional

from anthropic.types.message import Message
from opentelemetry.trace import Span

from .base import BaseSpanParser
from .common import (
    OPENINFERENCE_SPAN_KIND,
    LLM_SYSTEM,
    ANTHROPIC_SYSTEM,
    LLM_SPAN_KIND,
    TEXT_MESSAGE_TYPE,
    TOOL_CALL_MESSAGE_TYPE,
    TEXT_CONTENT_TYPE,
    TOOL_USE_CONTENT_TYPE,
    TOOL_RESULT_CONTENT_TYPE,
    ASSISTANT_ROLE,
    USER_ROLE,
    UNKNOWN_DEFAULT,
    NULL_VALUES,
    ROLE_FIELD,
    CONTENT_FIELD,
    TYPE_FIELD,
    NAME_FIELD,
    ID_FIELD,
    INPUT_FIELD,
    DESCRIPTION_FIELD,
    INPUT_SCHEMA_FIELD,
    TOOL_USE_ID_FIELD,
)
from ...models.api_types import (
    LLMInput,
    LLMInteraction,
    LLMOutput,
    LLMToolDefinition,
    LLMToolCall,
    LLMToolResponse,
)
from ...models.openinference import OpenInferenceSpanData

logger = logging.getLogger(__name__)


class AnthropicSpanParser(BaseSpanParser):
    """Parser for Anthropic spans captured by OpenInference."""

    def __init__(self):
        super().__init__(name="Anthropic")

    def can_parse(self, span: Span) -> bool:
        """Check if this is an Anthropic LLM span."""
        if not hasattr(span, "attributes") or span.attributes is None:
            return False

        attrs = span.attributes
        return (
            attrs.get(OPENINFERENCE_SPAN_KIND) == LLM_SPAN_KIND
            and attrs.get(LLM_SYSTEM) == ANTHROPIC_SYSTEM
        )

    def parse(self, span: Span) -> Optional[LLMInteraction]:
        """Parse Anthropic span into LLMInteraction."""
        try:
            if not hasattr(span, "attributes") or span.attributes is None:
                return None

            span_data = OpenInferenceSpanData.from_span_attributes(span.attributes)
            input_messages, output_messages, tools = [], [], []

            # Parse input data
            if span_data.input_value and span_data.input_value not in NULL_VALUES:
                input_data = json.loads(span_data.input_value)

                for message in input_data.get("messages", []):
                    role = message.get(ROLE_FIELD, UNKNOWN_DEFAULT)
                    content = message.get(CONTENT_FIELD) or ""

                    # Process assistant messages with tool calls
                    if role == ASSISTANT_ROLE and isinstance(content, list):
                        content = self._process_assistant_content(content)

                    # Process tool response messages
                    elif role == USER_ROLE and isinstance(content, list):
                        content = self._process_tool_response(content)

                    input_messages.append(
                        LLMInput(role=role, content=content, type=TEXT_MESSAGE_TYPE)
                    )

                # Extract tools
                for tool in input_data.get("tools", []):
                    if isinstance(tool, dict) and NAME_FIELD in tool:
                        tools.append(
                            LLMToolDefinition(
                                name=tool.get(NAME_FIELD, UNKNOWN_DEFAULT),
                                description=tool.get(DESCRIPTION_FIELD, ""),
                                parameters=json.dumps(tool.get(INPUT_SCHEMA_FIELD, {})),
                            )
                        )

            # Parse output data
            if span_data.output_value and span_data.output_value not in NULL_VALUES:
                output_data = json.loads(span_data.output_value)
                message = Message.model_validate(output_data)

                for block in message.content:
                    if block.type == TEXT_CONTENT_TYPE:
                        output_messages.append(
                            LLMOutput(content=block.text, type=TEXT_MESSAGE_TYPE)
                        )
                    elif block.type == TOOL_USE_CONTENT_TYPE:
                        output_messages.append(
                            LLMOutput(
                                content=LLMToolCall(
                                    id=block.id,
                                    name=block.name,
                                    parameters=json.dumps(block.input),
                                ),
                                type=TOOL_CALL_MESSAGE_TYPE,
                            )
                        )

            return LLMInteraction(
                input_messages=input_messages,
                output_messages=output_messages,
                tools_available=tools or None,
            )

        except Exception as e:
            logger.error(f"Error parsing Anthropic data: {e}", exc_info=True)
            return None

    def _process_assistant_content(self, content: list) -> str | LLMToolCall:
        """Process assistant message content with potential tool calls.

        Anthropic messages can contain multiple content blocks:
        - Multiple text blocks: ["Let me help", "I need to use calculator"]
        - Text + tool calls: ["I'll calculate"] + tool_use block
        - Multiple tool calls: rare but possible

        We join text blocks with spaces to maintain semantic integrity.
        """
        processed_content = []
        for block in content:
            if isinstance(block, dict):
                if block.get(TYPE_FIELD) == TEXT_CONTENT_TYPE:
                    processed_content.append(block.get("text", ""))
                elif block.get(TYPE_FIELD) == TOOL_USE_CONTENT_TYPE:
                    processed_content.append(
                        LLMToolCall(
                            id=block.get(ID_FIELD, ""),
                            name=block.get(NAME_FIELD, UNKNOWN_DEFAULT),
                            parameters=json.dumps(block.get(INPUT_FIELD, {})),
                        )
                    )

        # Join multiple text blocks with spaces to maintain semantic integrity
        text_content = " ".join([c for c in processed_content if isinstance(c, str)])
        tool_calls = [c for c in processed_content if isinstance(c, LLMToolCall)]
        return tool_calls[0] if tool_calls else text_content

    def _process_tool_response(self, content: list) -> LLMToolResponse | str:
        """Process tool response message content."""
        for block in content:
            if (
                isinstance(block, dict)
                and block.get(TYPE_FIELD) == TOOL_RESULT_CONTENT_TYPE
            ):
                return LLMToolResponse(
                    id=block.get(TOOL_USE_ID_FIELD, ""),
                    response=block.get(CONTENT_FIELD, ""),
                    name=block.get(NAME_FIELD, ""),
                )
        return ""
