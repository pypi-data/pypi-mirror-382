"""OpenAI span parser for OpenInference traces."""

import json
import logging
from typing import Optional

from openai.types.chat.chat_completion import ChatCompletion
from opentelemetry.trace import Span

from .base import BaseSpanParser
from .common import (
    OPENINFERENCE_SPAN_KIND,
    LLM_SYSTEM,
    OPENAI_SYSTEM,
    LLM_SPAN_KIND,
    TEXT_MESSAGE_TYPE,
    TOOL_CALL_MESSAGE_TYPE,
    ASSISTANT_ROLE,
    USER_ROLE,
    SYSTEM_ROLE,
    TOOL_ROLE,
    UNKNOWN_DEFAULT,
    NULL_VALUES,
    ROLE_FIELD,
    CONTENT_FIELD,
    NAME_FIELD,
    ID_FIELD,
    DESCRIPTION_FIELD,
    FUNCTION_FIELD,
    TOOL_CALLS_FIELD,
    TOOL_CALL_ID_FIELD,
    ARGUMENTS_FIELD,
    PARAMETERS_FIELD,
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


class OpenAISpanParser(BaseSpanParser):
    """Parser for OpenAI spans captured by OpenInference."""

    def __init__(self):
        super().__init__(name="OpenAI")

    def can_parse(self, span: Span) -> bool:
        """Check if this is an OpenAI LLM span."""
        if not hasattr(span, "attributes") or span.attributes is None:
            return False

        attrs = span.attributes
        return (
            attrs.get(OPENINFERENCE_SPAN_KIND) == LLM_SPAN_KIND
            and attrs.get(LLM_SYSTEM) == OPENAI_SYSTEM
        )

    def parse(self, span: Span) -> Optional[LLMInteraction]:
        """Parse OpenAI span into LLMInteraction."""
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

                    # Handle assistant messages with tool calls
                    if role == ASSISTANT_ROLE and TOOL_CALLS_FIELD in message:
                        tool_calls = message.get(TOOL_CALLS_FIELD, [])
                        if tool_calls:
                            llm_tool_calls = []
                            for tc in tool_calls:
                                llm_tool_calls.append(
                                    LLMToolCall(
                                        id=tc.get(ID_FIELD, ""),
                                        name=tc.get(FUNCTION_FIELD, {}).get(
                                            NAME_FIELD, UNKNOWN_DEFAULT
                                        ),
                                        parameters=tc.get(FUNCTION_FIELD, {}).get(
                                            ARGUMENTS_FIELD, "{}"
                                        ),
                                    )
                                )
                            content = llm_tool_calls[0] if llm_tool_calls else ""

                    # Handle tool response messages
                    elif role == TOOL_ROLE:
                        tool_call_id = message.get(TOOL_CALL_ID_FIELD, "")
                        tool_name = message.get(NAME_FIELD, "")
                        llm_tool_response = LLMToolResponse(
                            id=tool_call_id, response=content, name=tool_name
                        )
                        content = llm_tool_response

                    input_messages.append(
                        LLMInput(role=role, content=content, type=TEXT_MESSAGE_TYPE)
                    )

                # Extract tools
                for tool in input_data.get("tools", []):
                    if isinstance(tool, dict) and FUNCTION_FIELD in tool:
                        func = tool[FUNCTION_FIELD]
                        tools.append(
                            LLMToolDefinition(
                                name=func.get(NAME_FIELD, UNKNOWN_DEFAULT),
                                description=func.get(DESCRIPTION_FIELD, ""),
                                parameters=json.dumps(func.get(PARAMETERS_FIELD, {})),
                            )
                        )

            # Parse output data
            if span_data.output_value and span_data.output_value not in NULL_VALUES:
                output_data = json.loads(span_data.output_value)
                chat_completion = ChatCompletion.model_validate(output_data)

                for choice in chat_completion.choices:
                    if choice.message:
                        # Handle text content
                        if choice.message.content:
                            output_messages.append(
                                LLMOutput(
                                    content=choice.message.content,
                                    type=TEXT_MESSAGE_TYPE,
                                )
                            )

                        # Handle tool calls
                        if choice.message.tool_calls:
                            for tool_call in choice.message.tool_calls:
                                llm_tool_call = LLMToolCall(
                                    id=tool_call.id,
                                    name=tool_call.function.name,
                                    parameters=tool_call.function.arguments,
                                )
                                output_messages.append(
                                    LLMOutput(
                                        content=llm_tool_call,
                                        type=TOOL_CALL_MESSAGE_TYPE,
                                    )
                                )

            return LLMInteraction(
                input_messages=input_messages,
                output_messages=output_messages,
                tools_available=tools or None,
            )

        except Exception as e:
            logger.error(f"Error parsing OpenAI data: {e}", exc_info=True)
            return None
