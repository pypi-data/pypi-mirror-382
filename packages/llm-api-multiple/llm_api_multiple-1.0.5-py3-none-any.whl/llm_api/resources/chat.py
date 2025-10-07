# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Dict, List  # Standard Library Import

import httpx  # Third-Party Import

from ..types import chat_create_completion_params
from .._types import Body, Query, Headers, NotGiven, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property  # Local/Project Imports
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["ChatResource", "AsyncChatResource"]


class ChatResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#accessing-raw-response-data-eg-headers
        """
        return ChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#with_streaming_response
        """
        return ChatResourceWithStreamingResponse(self)

    def create_completion(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        stream: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Proxies an OpenAI chat completion request to the configured internal LLM
        endpoint. Handles both streaming and non-streaming responses, and logs key
        usage.

        Args: request: The FastAPI Request object. openai_payload: The request body
        containing the chat completion parameters. key_record: The validated API key
        record. key_log_model: Dependency for logging key usage.

        Returns: Union[StreamingResponse, Response]: The LLM response, potentially
        streaming.

        Raises: HTTPException: 400 If the requested model is not supported.
        HTTPException: 401 If the API key is invalid (from dependency). HTTPException:
        504 If the connection times out. HTTPException: 502 For LLM API or transport
        errors.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "stream": stream,
                },
                chat_create_completion_params.ChatCreateCompletionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=object,
        )


class AsyncChatResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#with_streaming_response
        """
        return AsyncChatResourceWithStreamingResponse(self)

    async def create_completion(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        stream: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Proxies an OpenAI chat completion request to the configured internal LLM
        endpoint. Handles both streaming and non-streaming responses, and logs key
        usage.

        Args: request: The FastAPI Request object. openai_payload: The request body
        containing the chat completion parameters. key_record: The validated API key
        record. key_log_model: Dependency for logging key usage.

        Returns: Union[StreamingResponse, Response]: The LLM response, potentially
        streaming.

        Raises: HTTPException: 400 If the requested model is not supported.
        HTTPException: 401 If the API key is invalid (from dependency). HTTPException:
        504 If the connection times out. HTTPException: 502 For LLM API or transport
        errors.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/chat/completions",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "stream": stream,
                },
                chat_create_completion_params.ChatCreateCompletionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=object,
        )


class ChatResourceWithRawResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.create_completion = to_raw_response_wrapper(
            chat.create_completion,
        )


class AsyncChatResourceWithRawResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.create_completion = async_to_raw_response_wrapper(
            chat.create_completion,
        )


class ChatResourceWithStreamingResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.create_completion = to_streamed_response_wrapper(
            chat.create_completion,
        )


class AsyncChatResourceWithStreamingResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.create_completion = async_to_streamed_response_wrapper(
            chat.create_completion,
        )
