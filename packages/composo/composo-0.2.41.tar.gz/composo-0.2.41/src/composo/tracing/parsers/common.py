"""Common constants for span parsers."""

# OpenInference attribute keys
OPENINFERENCE_SPAN_KIND = "openinference.span.kind"
LLM_SYSTEM = "llm.system"

# System names
ANTHROPIC_SYSTEM = "anthropic"
OPENAI_SYSTEM = "openai"

# Span kinds
LLM_SPAN_KIND = "LLM"

# Message types
TEXT_MESSAGE_TYPE = "text"
TOOL_CALL_MESSAGE_TYPE = "tool_call"

# Content types
TEXT_CONTENT_TYPE = "text"
TOOL_USE_CONTENT_TYPE = "tool_use"
TOOL_RESULT_CONTENT_TYPE = "tool_result"

# Role names
ASSISTANT_ROLE = "assistant"
USER_ROLE = "user"
SYSTEM_ROLE = "system"
TOOL_ROLE = "tool"

# Default values
UNKNOWN_DEFAULT = "unknown"

# Null value checks
NULL_VALUES = (None, "null", "")

# Field names
ROLE_FIELD = "role"
CONTENT_FIELD = "content"
TYPE_FIELD = "type"
NAME_FIELD = "name"
ID_FIELD = "id"
INPUT_FIELD = "input"
DESCRIPTION_FIELD = "description"
INPUT_SCHEMA_FIELD = "input_schema"
TOOL_USE_ID_FIELD = "tool_use_id"
FUNCTION_FIELD = "function"
TOOL_CALLS_FIELD = "tool_calls"
TOOL_CALL_ID_FIELD = "tool_call_id"
ARGUMENTS_FIELD = "arguments"
PARAMETERS_FIELD = "parameters"
