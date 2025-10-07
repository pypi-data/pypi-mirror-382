"""
Synchronous Composo client

This module provides a synchronous Composo client for evaluating chat message quality.
Composo is an AI evaluation platform that can analyze chat conversations and tool calls,
and provide scores and explanations based on specified criteria.

Main features:
- Evaluate chat message quality and relevance
- Support multiple evaluation criteria (single or multiple criteria)
- Handle tool calls and system messages
- Provide retry mechanisms and error handling
"""

from typing import List, Dict, Any, Optional, Union

from ..models.api_types import (
    MultiAgentTrace,
    TraceRewardRequest,
    MultiAgentTraceResponse,
)
from ..models.common_types import ModelCore
from .base import BaseClient, REWARD_ENDPOINT, BINARY_ENDPOINT, TRACE_ENDPOINT
from .types import MessagesType, ToolsType, ResultType
from ..models import EvaluationResponse, BinaryEvaluationResponse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random,
    retry_if_exception_type,
)


class Composo(BaseClient):
    """Synchronous Composo client.

    This client is used for synchronous calls to the Composo API for message evaluation.
    Suitable for single evaluations or small batch evaluation scenarios, providing a simple and easy-to-use interface.

    Key features:
        - Synchronous API calls, easy to integrate into existing code
        - Automatic retry mechanism, improving request success rate
        - Support for context managers, automatic resource management
        - Support for multiple evaluation criteria

    Inherits from BaseClient, which provides:
        - api_key: Composo API key for authentication
        - base_url: API base URL, defaults to official platform address
        - num_retries: Number of retries on request failure, defaults to 1
        - model_core: Optional model core identifier for specifying evaluation model
        - timeout: Request timeout in seconds, defaults to 60 seconds
    """

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP client"""
        self.close()

    def _make_request(
        self, request_data: Dict[str, Any], endpoint: str
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic using tenacity (exponential backoff base 2 + jitter)"""

        @retry(
            stop=stop_after_attempt(self.num_retries),
            wait=wait_exponential(multiplier=1, min=1, max=60) + wait_random(0, 1),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        def do_request():
            return self._post(
                endpoint=endpoint,
                data=request_data,
                headers=self._build_headers(),
            )

        return do_request()

    def _evaluate_single_criterion(
        self,
        messages: MessagesType,
        single_criterion: str,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
    ) -> EvaluationResponse:
        """Evaluate a single criterion synchronously"""
        evaluation_request = self._prepare_evaluation_request(
            messages, system, tools, result, single_criterion
        )
        request_data = evaluation_request.model_dump(exclude_none=True)

        # Determine endpoint and make request
        endpoint = self._get_endpoint(evaluation_request, single_criterion)
        response_data = self._make_request(request_data, endpoint)

        # Process response using shared logic
        return self._process_evaluation_response(response_data, single_criterion)

    def evaluate(
        self,
        messages: MessagesType,
        system: Optional[str] = None,
        tools: ToolsType = None,
        result: ResultType = None,
        criteria: Optional[Union[str, List[str]]] = None,
    ) -> Union[EvaluationResponse, List[EvaluationResponse]]:
        """Evaluate messages with optional criteria.

        Args:
            messages: List of chat messages to evaluate.
                Format: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hello!"}]
            criteria: Evaluation criteria (str or list of str).
            system: Optional system message to set AI behavior and context.
            tools: Optional list of tool definitions for evaluating tool calls.
            result: Optional LLM result to append to the conversation.

        Returns:
            EvaluationResponse or list of EvaluationResponse objects.
        """

        # Convert single criteria to list if needed
        if isinstance(criteria, str):
            criteria = [criteria]

        # Always evaluate multiple criteria
        results = self._evaluate_multiple_criteria(
            messages, criteria, system, tools, result
        )

        # Return single result if only one criteria was provided
        if len(criteria) == 1:
            return results[0]
        else:
            return results

    def _evaluate_multiple_criteria(
        self,
        messages: MessagesType,
        criteria: List[str],
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
    ) -> List[EvaluationResponse]:
        """Evaluate multiple criteria sequentially"""
        results = []
        for single_criterion in criteria:
            results.append(
                self._evaluate_single_criterion(
                    messages, single_criterion, system, tools, result
                )
            )
        return results

    def _evaluate_trace(
        self,
        trace: MultiAgentTrace,
        model_core: Optional[ModelCore],
        criteria: List[str],
    ) -> List[MultiAgentTraceResponse]:
        res = []
        for criterion in criteria:
            request_info = self._prepare_trace_request(trace, criterion, model_core)
            response_data = self._make_request(
                request_info["request_data"], request_info["endpoint"]
            )
            trace_response = self._process_trace_response(response_data)
            res.append(trace_response)
        return res

    def evaluate_trace(
        self,
        trace: MultiAgentTrace,
        criteria: Union[str, List[str]],
        model_core: Optional[ModelCore] = None,
    ) -> Union[MultiAgentTraceResponse, List[MultiAgentTraceResponse]]:
        """Evaluate trace with optional criteria.

        Args:
            trace: MultiAgentTrace object to evaluate.
            criteria: Evaluation criteria (str or list of str).
            model_core: Optional model core identifier for specifying evaluation model.

        Returns:
            MultiAgentTraceResponse or list of MultiAgentTraceResponse objects.
        """

        # Convert single criteria to list if needed
        if isinstance(criteria, str):
            criteria = [criteria]

        # Use model_core from parameter, or self.model_core, or None (will use TraceRewardRequest default)
        final_model_core = model_core if model_core is not None else self.model_core

        # Always evaluate multiple criteria
        results = self._evaluate_trace(trace, final_model_core, criteria)

        # Return single result if only one criteria was provided
        if len(criteria) == 1:
            return results[0]
        else:
            return results
