# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal

import httpx

from .events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
from ...types import defend_create_workflow_params, defend_update_workflow_params
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.defend_response import DefendResponse

__all__ = ["DefendResource", "AsyncDefendResource"]


class DefendResource(SyncAPIResource):
    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DefendResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/deeprails/deeprails-python-sdk#accessing-raw-response-data-eg-headers
        """
        return DefendResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DefendResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/deeprails/deeprails-python-sdk#with_streaming_response
        """
        return DefendResourceWithStreamingResponse(self)

    def create_workflow(
        self,
        *,
        improvement_action: Optional[Literal["regenerate", "fixit"]],
        metrics: Dict[str, float],
        name: str,
        type: Literal["automatic", "custom"],
        automatic_tolerance: Literal["low", "medium", "high"] | Omit = omit,
        description: str | Omit = omit,
        max_retries: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DefendResponse:
        """
        Create a new guardrail workflow with optional guardrail thresholds and
        improvement actions.

        Args:
          improvement_action: The action used to improve outputs that fail one or guardrail metrics for the
              workflow events. May be `regenerate`, `fixit`, or null which represents “do
              nothing”. ReGen runs the user's exact input prompt with minor induced variance.
              Fixit attempts to directly address the shortcomings of the output using the
              guardrail failure rationale. Do nothing does not attempt any improvement.

          metrics: Mapping of guardrail metrics to floating point threshold values. If the workflow
              type is automatic, only the metric names are used (`automatic_tolerance`
              determines thresholds). Possible metrics are `correctness`, `completeness`,
              `instruction_adherence`, `context_adherence`, `ground_truth_adherence`, or
              `comprehensive_safety`.

          name: Name of the workflow.

          type: Type of thresholds to use for the workflow, either `automatic` or `custom`.
              Automatic thresholds are assigned internally after the user specifies a
              qualitative tolerance for the metrics, whereas custom metrics allow the user to
              set the threshold for each metric as a floating point number between 0.0 and
              1.0.

          automatic_tolerance: Hallucination tolerance for automatic workflows; may be `low`, `medium`, or
              `high`. Ignored if `type` is `custom`.

          description: Description for the workflow.

          max_retries: Max. number of improvement action retries until a given event passes the
              guardrails. Defaults to 10.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/defend",
            body=maybe_transform(
                {
                    "improvement_action": improvement_action,
                    "metrics": metrics,
                    "name": name,
                    "type": type,
                    "automatic_tolerance": automatic_tolerance,
                    "description": description,
                    "max_retries": max_retries,
                },
                defend_create_workflow_params.DefendCreateWorkflowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DefendResponse,
        )

    def retrieve_workflow(
        self,
        workflow_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DefendResponse:
        """
        Retrieve the details for a specific guardrail workflow.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_id:
            raise ValueError(f"Expected a non-empty value for `workflow_id` but received {workflow_id!r}")
        return self._get(
            f"/defend/{workflow_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DefendResponse,
        )

    def update_workflow(
        self,
        workflow_id: str,
        *,
        description: str | Omit = omit,
        name: str | Omit = omit,
        type: Literal["automatic", "custom"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DefendResponse:
        """
        Update an existing guardrail workflow.

        Args:
          description: Description for the workflow.

          name: Name of the workflow.

          type: Type of thresholds to use for the workflow, either `automatic` or `custom`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_id:
            raise ValueError(f"Expected a non-empty value for `workflow_id` but received {workflow_id!r}")
        return self._put(
            f"/defend/{workflow_id}",
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "type": type,
                },
                defend_update_workflow_params.DefendUpdateWorkflowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DefendResponse,
        )


class AsyncDefendResource(AsyncAPIResource):
    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDefendResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/deeprails/deeprails-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDefendResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDefendResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/deeprails/deeprails-python-sdk#with_streaming_response
        """
        return AsyncDefendResourceWithStreamingResponse(self)

    async def create_workflow(
        self,
        *,
        improvement_action: Optional[Literal["regenerate", "fixit"]],
        metrics: Dict[str, float],
        name: str,
        type: Literal["automatic", "custom"],
        automatic_tolerance: Literal["low", "medium", "high"] | Omit = omit,
        description: str | Omit = omit,
        max_retries: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DefendResponse:
        """
        Create a new guardrail workflow with optional guardrail thresholds and
        improvement actions.

        Args:
          improvement_action: The action used to improve outputs that fail one or guardrail metrics for the
              workflow events. May be `regenerate`, `fixit`, or null which represents “do
              nothing”. ReGen runs the user's exact input prompt with minor induced variance.
              Fixit attempts to directly address the shortcomings of the output using the
              guardrail failure rationale. Do nothing does not attempt any improvement.

          metrics: Mapping of guardrail metrics to floating point threshold values. If the workflow
              type is automatic, only the metric names are used (`automatic_tolerance`
              determines thresholds). Possible metrics are `correctness`, `completeness`,
              `instruction_adherence`, `context_adherence`, `ground_truth_adherence`, or
              `comprehensive_safety`.

          name: Name of the workflow.

          type: Type of thresholds to use for the workflow, either `automatic` or `custom`.
              Automatic thresholds are assigned internally after the user specifies a
              qualitative tolerance for the metrics, whereas custom metrics allow the user to
              set the threshold for each metric as a floating point number between 0.0 and
              1.0.

          automatic_tolerance: Hallucination tolerance for automatic workflows; may be `low`, `medium`, or
              `high`. Ignored if `type` is `custom`.

          description: Description for the workflow.

          max_retries: Max. number of improvement action retries until a given event passes the
              guardrails. Defaults to 10.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/defend",
            body=await async_maybe_transform(
                {
                    "improvement_action": improvement_action,
                    "metrics": metrics,
                    "name": name,
                    "type": type,
                    "automatic_tolerance": automatic_tolerance,
                    "description": description,
                    "max_retries": max_retries,
                },
                defend_create_workflow_params.DefendCreateWorkflowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DefendResponse,
        )

    async def retrieve_workflow(
        self,
        workflow_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DefendResponse:
        """
        Retrieve the details for a specific guardrail workflow.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_id:
            raise ValueError(f"Expected a non-empty value for `workflow_id` but received {workflow_id!r}")
        return await self._get(
            f"/defend/{workflow_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DefendResponse,
        )

    async def update_workflow(
        self,
        workflow_id: str,
        *,
        description: str | Omit = omit,
        name: str | Omit = omit,
        type: Literal["automatic", "custom"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DefendResponse:
        """
        Update an existing guardrail workflow.

        Args:
          description: Description for the workflow.

          name: Name of the workflow.

          type: Type of thresholds to use for the workflow, either `automatic` or `custom`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_id:
            raise ValueError(f"Expected a non-empty value for `workflow_id` but received {workflow_id!r}")
        return await self._put(
            f"/defend/{workflow_id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "type": type,
                },
                defend_update_workflow_params.DefendUpdateWorkflowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DefendResponse,
        )


class DefendResourceWithRawResponse:
    def __init__(self, defend: DefendResource) -> None:
        self._defend = defend

        self.create_workflow = to_raw_response_wrapper(
            defend.create_workflow,
        )
        self.retrieve_workflow = to_raw_response_wrapper(
            defend.retrieve_workflow,
        )
        self.update_workflow = to_raw_response_wrapper(
            defend.update_workflow,
        )

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._defend.events)


class AsyncDefendResourceWithRawResponse:
    def __init__(self, defend: AsyncDefendResource) -> None:
        self._defend = defend

        self.create_workflow = async_to_raw_response_wrapper(
            defend.create_workflow,
        )
        self.retrieve_workflow = async_to_raw_response_wrapper(
            defend.retrieve_workflow,
        )
        self.update_workflow = async_to_raw_response_wrapper(
            defend.update_workflow,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._defend.events)


class DefendResourceWithStreamingResponse:
    def __init__(self, defend: DefendResource) -> None:
        self._defend = defend

        self.create_workflow = to_streamed_response_wrapper(
            defend.create_workflow,
        )
        self.retrieve_workflow = to_streamed_response_wrapper(
            defend.retrieve_workflow,
        )
        self.update_workflow = to_streamed_response_wrapper(
            defend.update_workflow,
        )

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._defend.events)


class AsyncDefendResourceWithStreamingResponse:
    def __init__(self, defend: AsyncDefendResource) -> None:
        self._defend = defend

        self.create_workflow = async_to_streamed_response_wrapper(
            defend.create_workflow,
        )
        self.retrieve_workflow = async_to_streamed_response_wrapper(
            defend.retrieve_workflow,
        )
        self.update_workflow = async_to_streamed_response_wrapper(
            defend.update_workflow,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._defend.events)
