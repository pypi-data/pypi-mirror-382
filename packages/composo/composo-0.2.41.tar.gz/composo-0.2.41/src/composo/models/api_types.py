import math
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator
from json2xml import json2xml

from .common_types import (
    ModelCore,
    reward_starts,
    binary_starts,
    criteria_starts,
    EvaluationType,
)


class LLMToolResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool call.")
    response: str = Field(..., description="Tool response")

    name: Optional[str] = Field(default=None, description="Tool name")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMToolCall(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool call.")
    name: str = Field(..., description="Tool name")
    parameters: str = Field(..., description="Tool parameters.")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMToolDefinition(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: str = Field(..., description="Tool parameters.")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMInput(BaseModel):
    role: str = Field(
        ...,
        description="Role of the message sender (e.g., user, system, assistant, tool)",
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of message (e.g., text, thinking_tokens, tool_call). This can be arbitrary but should be consistent within a trace.",
    )
    content: Union[str, LLMToolCall, LLMToolResponse] = Field(
        ..., description="Content of the LLM Input."
    )


class LLMOutput(BaseModel):
    type: Optional[str] = Field(
        default=None,
        description="Type of message (e.g., text, thinking_tokens, tool_call). This can be arbitrary but should be consistent within a trace.",
    )
    content: Union[str, LLMToolCall] = Field(..., description="Content of the message")


class LLMInteraction(BaseModel):
    input_messages: List[LLMInput] = Field(
        ...,
        description="List of input messages to the LLM invocation.",
    )
    output_messages: List[LLMOutput] = Field(
        ...,
        description="List of output messages from the LLM invocation.",
    )
    tools_available: Optional[List[LLMToolDefinition]] = Field(
        default=None,
        description="List of tools available to the agent in this interaction.",
    )


class AgentInstance(BaseModel):
    id: str = Field(..., description="Unique identifier for the agent instance.")
    name: str = Field(..., description="User defined name of the agent invoked.")
    interactions: List[Union[str, LLMInteraction]] = Field(
        ...,
        description="List of ordered LLM interactions or agent instance ids for this agent instance.",
    )

    def _dedupe_input_messages(self, agent_dict: dict) -> dict:
        """Dedupe input messages across interactions, removing duplicates from later interactions.

        This handles the common pattern where each interaction's input messages include
        the full conversation history from previous interactions. By comparing each
        interaction's input against the previous interaction's complete message sequence
        (input + output), we can remove redundant messages and keep only the new ones.

        Example:
            Interaction 1: input=[A, B], output=[C]
            Interaction 2: input=[A, B, C, D], output=[E]
            After deduplication:
            Interaction 2: input=[D], output=[E]  # A, B, C are removed as duplicates


        TODO(ryan):
        - This is still not exhaustive, as we only compare pairs, not the full history, we could hit
            an edge case where a conversation is built up interleaved between two threads. We'll leave
            this for now and see how it actually works in practice.
        """

        def msg_to_key(msg):
            """Create a normalized hashable key for a message.

            This key combines role, type, and content (all lowercased and stripped)
            to enable case-insensitive, whitespace-insensitive comparison.
            Output messages don't have a role field, so we default to 'assistant'. This allows us to compare LLMInputs with LLMOutputs.
            """
            msg_type = msg.get("type") or ""
            role = msg.get("role", "assistant")  # Output messages don't have role
            return f"{role.strip().lower()}|{msg_type.strip().lower()}|{msg['content'].strip().lower()}"

        # Iterate through interactions starting from the second one
        for i in range(1, len(agent_dict["interactions"])):
            prev_interaction = agent_dict["interactions"][i - 1]
            curr_interaction = agent_dict["interactions"][i]

            # Build the previous interaction's complete message sequence
            # This represents what the model saw and produced in the previous turn
            prev_messages = prev_interaction.get(
                "input_messages", []
            ) + prev_interaction.get("output_messages", [])
            prev_keys = [msg_to_key(msg) for msg in prev_messages]

            # Get current interaction's input messages
            # Note: We only deduplicate INPUT messages, not output messages.
            # Output messages from the current interaction are unique to this turn
            # and should never be removed. Only the input may contain redundant
            # conversation history from previous interactions.
            curr_messages = curr_interaction.get("input_messages", [])
            curr_keys = [msg_to_key(msg) for msg in curr_messages]

            # Keep only messages that are new (not in previous interaction at same position)
            # We compare by position because conversation history grows sequentially:
            # if curr_messages[0:N] matches prev_messages[0:N], those are duplicates
            kept_messages = []
            for idx, curr_key in enumerate(curr_keys):
                # Keep message if:
                # 1. Its index exceeds the previous message list length (definitely new), OR
                # 2. It doesn't match the message at the same index in previous (modified or new)
                if idx >= len(prev_keys) or curr_key != prev_keys[idx]:
                    kept_messages.append(curr_messages[idx])

            # Replace with deduplicated list
            curr_interaction["input_messages"] = kept_messages

        return agent_dict

    def _dedupe_tool_definitions(self, agent_dict: dict) -> dict:
        """Dedupe tools across interactions in-place, replacing with tool name references."""
        # Extract all unique tools and use tool name as ID
        all_tools = {}

        for interaction in agent_dict["interactions"]:
            # if there are no tools available, skip
            if interaction.get("tools_available") is None:
                continue
            tool_names = []
            for tool in interaction["tools_available"]:
                if tool["name"] not in all_tools:
                    all_tools[tool["name"]] = tool
                tool_names.append(tool["name"])

            # Replace tools_available field with a list just containing just names/IDs
            interaction["tools_available"] = tool_names

        # Add tool_definitions to the agent dict
        agent_dict["tool_definitions"] = list(all_tools.values())

        return agent_dict

    def to_xml(self) -> str:
        """
        Convert AgentInstance to XML format with various dedupe steps to make it more compact:
            1. Tools available extracted and replaced with ID references.
            2. At the AgentInstance level we also must dedupe messages throughout the list of interactions.
        """

        # when there are no LLM interactions this is just a wrapper so there is nothing to eval
        llm_interactions = [
            interaction
            for interaction in self.interactions
            if isinstance(interaction, LLMInteraction)
        ]
        if not llm_interactions:
            return None

        # Convert to dict keeping actual type unmodified.
        agent_dict = self.model_dump()

        # Exclude any interactions that are just strings (agent instance ids)
        agent_dict["interactions"] = [
            interaction.model_dump() for interaction in llm_interactions
        ]

        agent_dict = self._dedupe_tool_definitions(agent_dict)
        agent_dict = self._dedupe_input_messages(agent_dict)

        # Convert to XML
        return json2xml.Json2xml(
            agent_dict, wrapper="agent_instance", attr_type=False, pretty=True
        ).to_xml()


class MultiAgentTrace(BaseModel):
    root_agent_instance_id: str = Field(
        ...,
        description="User invoked Agent Instance ID. This is the root of the trace.",
    )
    agent_instance_by_id: dict[str, AgentInstance] = Field(
        ..., description="Mapping of ID to Agent Instance objects."
    )


class RequestBase(BaseModel):
    messages: List[dict] = Field(
        ..., description="A list of chat messages", min_length=2
    )
    system: Optional[str] = Field(
        None,
        description="System message is separate for Anthropic-style LLM calls. Optional.",
    )
    tools: Optional[List[dict]] = Field(
        None,
        description="List of tools available for the assistant to call. Optional.",
    )
    model_core: ModelCore = Field(
        default=ModelCore.ALIGN_20250529,
        description="The model core for reward evaluation. Defaults to align-20250503 if not specified.",
    )

    @field_validator("messages")
    @classmethod
    def last_message_must_be_assistant(cls, messages) -> List[dict]:
        if not messages:
            raise ValueError("Conversation must contain at least one message")

        return messages


class RewardRequest(RequestBase):
    """
    Request model for reward score evaluation of LLM responses against specified criteria.
    """

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(reward_starts),
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        if not any(value.startswith(start) for start in reward_starts):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(reward_starts)
            )
        return value


class RewardGPURequest(RewardRequest):
    """
    Request model for reward score evaluation of LLM responses against specified criteria,
    specifically for GPU-based evaluation.
    """

    explanation: str = Field(
        description="Explanation of the evaluation criteria. Optional.",
    )


class BinaryEvaluationRequest(RequestBase):
    """
    Request model for binary evaluation of LLM responses against specified criteria.
    """

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(binary_starts),
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        if not any(value.startswith(start) for start in binary_starts):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(binary_starts)
            )
        return value


class TraceRewardRequest(BaseModel):
    """
    Request model for a trace based evaluation of LLM responses against specified criteria.
    """

    trace: MultiAgentTrace = Field(
        ...,
        description="A Multi Agent Trace object representing the full trace of agent interactions.",
    )
    model_core: ModelCore = Field(
        default=ModelCore.ALIGN_20250529,
        description="The model core for reward evaluation. Defaults to align-20250503 if not specified.",
    )

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(
            criteria_starts["reward"][EvaluationType.AGENT_EVALUATION]
            + criteria_starts["binary"][EvaluationType.AGENT_EVALUATION]
        ),
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        agent_evaluation_starts = (
            criteria_starts["reward"][EvaluationType.AGENT_EVALUATION]
            + criteria_starts["binary"][EvaluationType.AGENT_EVALUATION]
        )
        if not any(value.startswith(start) for start in agent_evaluation_starts):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(agent_evaluation_starts)
            )
        return value


class ScoreResponse(BaseModel):
    """
    Response model for evaluation scores.
    """

    score: Optional[float] = Field(
        None,
        description="Evaluation score between 0 and 1. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")

    @field_validator("score")
    def validate_score(cls, value):
        if value is None:
            return value
        if math.isnan(value):
            return None
        if not 0 <= value <= 1:
            raise ValueError("Score must be between 0 and 1.")
        return value


class BinaryEvaluationResponse(BaseModel):
    """
    Response model for binary evaluation results.
    """

    passed: Optional[bool] = Field(
        default=None,
        description="Whether the evaluation passed. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")


class SummaryStatistics(BaseModel):
    median: Optional[float] = Field(default=None, description="Median score.")
    min: Optional[float] = Field(default=None, description="Minimum score.")
    max: Optional[float] = Field(default=None, description="Maximum score.")
    std: Optional[float] = Field(
        default=None, description="Standard deviation of scores."
    )


class AgentTraceResult(BaseModel):
    agent_name: str = Field(..., description="Name of the agent evaluated.")
    results_by_agent_instance_id: dict[
        str, Union[ScoreResponse, BinaryEvaluationResponse, None]
    ] = Field(
        ...,
        description="Mapping of Agent Instance ID to their respective Score Response, Binary Evaluation Response, or None depending on criteria.",
    )
    summary_statistics: Optional[SummaryStatistics] = Field(
        default=None,
        description="Summary statistics for the agent's evaluations. Only applicable for reward evaluations.",
    )


class MultiAgentTraceResponse(BaseModel):
    """
    Response model for multi-agent trace evaluations.
    """

    request_id: str = Field(
        ..., description="Unique identifier for the evaluation request."
    )
    results_by_agent_name: dict[str, AgentTraceResult] = Field(
        ..., description="Mapping of Agent Name to their respective trace results."
    )

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)
