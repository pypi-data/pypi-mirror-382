# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional

import httpx

from ..types import batch_list_params, batch_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.batch_cancel_response import BatchCancelResponse
from ..types.batch_create_response import BatchCreateResponse

__all__ = ["BatchesResource", "AsyncBatchesResource"]


class BatchesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#accessing-raw-response-data-eg-headers
        """
        return BatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#with_streaming_response
        """
        return BatchesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        completion_window: str,
        endpoint: str,
        input_file_id: str,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchCreateResponse:
        """
        Creates a new batch job and submits it to a background Celery worker for
        processing.

        Args: request: The FastAPI Request object. batch_request: The Pydantic model
        containing batch configuration (file_id, endpoint, etc.). key_record: The
        validated API key record. key_log_model: Dependency for logging key usage.
        batch_model: Dependency for batch DB operations. files_model: Dependency for
        file DB validation. storage_service: Dependency for S3 interaction (passed to
        model). authorization: The 'Bearer <key>' header string (used by worker).

        Returns: BatchResponse: The initial batch record with status 'validating'.

        Raises: HTTPException: 404 If the input file is not found. HTTPException: 400 If
        file validation fails. HTTPException: 500 For internal server errors during
        submission.

        Args:
          completion_window: The time frame for the batch completion, e.g., '24h'.

          endpoint: The endpoint for the batch requests, e.g., '/v1/chat/completions'.

          input_file_id: The ID of the file to be processed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/batches",
            body=maybe_transform(
                {
                    "completion_window": completion_window,
                    "endpoint": endpoint,
                    "input_file_id": input_file_id,
                    "metadata": metadata,
                },
                batch_create_params.BatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchCreateResponse,
        )

    def retrieve(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Returns information about a specific batch job by its ID.

        Args: request: The FastAPI Request object. batch_id: The ID of the batch job.
        key_record: The validated API key record. batch_model: Dependency for batch DB
        operations. key_log_model: Dependency for logging key usage.

        Returns: dict: The batch job record.

        Raises: HTTPException: 404 If the batch is not found. HTTPException: 500 For
        errors during retrieval.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return self._get(
            f"/batches/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Returns a paginated list of batches.

        Args: request: The FastAPI Request object.

        limit: Query parameter for pagination
        size. after: Query parameter for pagination cursor. key_record: The validated
        API key record. batch_model: Dependency for batch DB operations. key_log_model:
        Dependency for logging key usage.

        Returns: dict: A dictionary containing the list of batches and pagination info.

        Raises: HTTPException: 500 For errors during list retrieval.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/batches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    batch_list_params.BatchListParams,
                ),
            ),
            cast_to=object,
        )

    def cancel(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchCancelResponse:
        """
        Initiates the cancellation of a running batch job.

        Args: request: The FastAPI Request object. batch_id: The ID of the batch job to
        cancel. key_record: The validated API key record. batch_model: Dependency for
        batch DB operations. key_log_model: Dependency for logging key usage.

        Returns: BatchCancelResponse: A response confirming the cancellation attempt.

        Raises: HTTPException: 400 If the batch is in a non-cancellable state.
        HTTPException: 404 If the batch is not found. HTTPException: 500 For internal
        server errors.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return self._post(
            f"/batches/{batch_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchCancelResponse,
        )


class AsyncBatchesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#with_streaming_response
        """
        return AsyncBatchesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        completion_window: str,
        endpoint: str,
        input_file_id: str,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchCreateResponse:
        """
        Creates a new batch job and submits it to a background Celery worker for
        processing.

        Args: request: The FastAPI Request object. batch_request: The Pydantic model
        containing batch configuration (file_id, endpoint, etc.). key_record: The
        validated API key record. key_log_model: Dependency for logging key usage.
        batch_model: Dependency for batch DB operations. files_model: Dependency for
        file DB validation. storage_service: Dependency for S3 interaction (passed to
        model). authorization: The 'Bearer <key>' header string (used by worker).

        Returns: BatchResponse: The initial batch record with status 'validating'.

        Raises: HTTPException: 404 If the input file is not found. HTTPException: 400 If
        file validation fails. HTTPException: 500 For internal server errors during
        submission.

        Args:
          completion_window: The time frame for the batch completion, e.g., '24h'.

          endpoint: The endpoint for the batch requests, e.g., '/v1/chat/completions'.

          input_file_id: The ID of the file to be processed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/batches",
            body=await async_maybe_transform(
                {
                    "completion_window": completion_window,
                    "endpoint": endpoint,
                    "input_file_id": input_file_id,
                    "metadata": metadata,
                },
                batch_create_params.BatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchCreateResponse,
        )

    async def retrieve(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Returns information about a specific batch job by its ID.

        Args: request: The FastAPI Request object. batch_id: The ID of the batch job.
        key_record: The validated API key record. batch_model: Dependency for batch DB
        operations. key_log_model: Dependency for logging key usage.

        Returns: dict: The batch job record.

        Raises: HTTPException: 404 If the batch is not found. HTTPException: 500 For
        errors during retrieval.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return await self._get(
            f"/batches/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Returns a paginated list of batches.

        Args: request: The FastAPI Request object.

        limit: Query parameter for pagination
        size. after: Query parameter for pagination cursor. key_record: The validated
        API key record. batch_model: Dependency for batch DB operations. key_log_model:
        Dependency for logging key usage.

        Returns: dict: A dictionary containing the list of batches and pagination info.

        Raises: HTTPException: 500 For errors during list retrieval.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/batches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    batch_list_params.BatchListParams,
                ),
            ),
            cast_to=object,
        )

    async def cancel(
        self,
        batch_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchCancelResponse:
        """
        Initiates the cancellation of a running batch job.

        Args: request: The FastAPI Request object. batch_id: The ID of the batch job to
        cancel. key_record: The validated API key record. batch_model: Dependency for
        batch DB operations. key_log_model: Dependency for logging key usage.

        Returns: BatchCancelResponse: A response confirming the cancellation attempt.

        Raises: HTTPException: 400 If the batch is in a non-cancellable state.
        HTTPException: 404 If the batch is not found. HTTPException: 500 For internal
        server errors.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        return await self._post(
            f"/batches/{batch_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchCancelResponse,
        )


class BatchesResourceWithRawResponse:
    def __init__(self, batches: BatchesResource) -> None:
        self._batches = batches

        self.create = to_raw_response_wrapper(
            batches.create,
        )
        self.retrieve = to_raw_response_wrapper(
            batches.retrieve,
        )
        self.list = to_raw_response_wrapper(
            batches.list,
        )
        self.cancel = to_raw_response_wrapper(
            batches.cancel,
        )


class AsyncBatchesResourceWithRawResponse:
    def __init__(self, batches: AsyncBatchesResource) -> None:
        self._batches = batches

        self.create = async_to_raw_response_wrapper(
            batches.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            batches.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            batches.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            batches.cancel,
        )


class BatchesResourceWithStreamingResponse:
    def __init__(self, batches: BatchesResource) -> None:
        self._batches = batches

        self.create = to_streamed_response_wrapper(
            batches.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            batches.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            batches.list,
        )
        self.cancel = to_streamed_response_wrapper(
            batches.cancel,
        )


class AsyncBatchesResourceWithStreamingResponse:
    def __init__(self, batches: AsyncBatchesResource) -> None:
        self._batches = batches

        self.create = async_to_streamed_response_wrapper(
            batches.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            batches.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            batches.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            batches.cancel,
        )
