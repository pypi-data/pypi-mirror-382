from enum import Enum
from itertools import chain


class ModelClass(str, Enum):
    ALIGN = "align"
    ALIGN_LIGHTNING = "align-lightning"


class ModelCore(str, Enum):
    ALIGN_20250529 = "align-20250529"
    ALIGN_LIGHTNING_20250731 = "align-lightning-20250731"

    def model_class(self) -> ModelClass:
        class_name = self.value.rsplit("-", 1)[0]
        return ModelClass(class_name)


class EvaluationType(Enum):
    ASSISTANT_RESPONSE_EVALUATION = "assistant_response_evaluation"
    TOOL_CALL_EVALUATION = "tool_call_evaluation"
    AGENT_EVALUATION = "agent_evaluation"


criteria_starts = {
    "reward": {
        EvaluationType.ASSISTANT_RESPONSE_EVALUATION: [
            "Reward responses",
            "Penalize responses",
        ],
        EvaluationType.TOOL_CALL_EVALUATION: [
            "Reward tool calls",
            "Penalize tool calls",
        ],
        EvaluationType.AGENT_EVALUATION: [
            "Reward agents",
            "Penalize agents",
        ],
    },
    "binary": {
        EvaluationType.ASSISTANT_RESPONSE_EVALUATION: [
            "Response passes if",
            "Response fails if",
        ],
        EvaluationType.TOOL_CALL_EVALUATION: [
            "Tool call passes if",
            "Tool call fails if",
        ],
        EvaluationType.AGENT_EVALUATION: [
            "Agent passes if",
            "Agent fails if",
        ],
    },
}

reward_starts = list(chain.from_iterable(criteria_starts["reward"].values()))
binary_starts = list(chain.from_iterable(criteria_starts["binary"].values()))

eval_response_error_codes = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the bad request error",
                        }
                    },
                }
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the unauthorized error",
                        }
                    },
                }
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the internal server error",
                        }
                    },
                }
            }
        },
    },
    429: {
        "description": "Too Many Requests",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the rate limiting error",
                        }
                    },
                }
            }
        },
    },
    524: {
        "description": "Request Timeout",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the gateway timeout error",
                        }
                    },
                }
            }
        },
    },
}


class InternalServerError(Exception):
    pass


class OverloadedError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class BadRequestError(Exception):
    pass
