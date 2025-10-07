"""
Data models for Composo SDK
"""

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from .requests import RequestBase, RewardRequest, BinaryEvaluationRequest
from .responses import ScoreResponse, BinaryEvaluationResponse
from .client_models import EvaluationRequest, EvaluationResponse
from .openinference import (
    OpenInferenceSpanData,
)

__all__ = [
    "ChatCompletionMessageParam",
    "RequestBase",
    "RewardRequest",
    "BinaryEvaluationRequest",
    "ScoreResponse",
    "BinaryEvaluationResponse",
    "EvaluationRequest",
    "EvaluationResponse",
    # OpenInference models
    "OpenInferenceSpanData",
]
