# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ..types import image_generate_params
from .._types import Body, Query, Headers, NotGiven, not_given
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

__all__ = ["ImagesResource", "AsyncImagesResource"]


class ImagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#accessing-raw-response-data-eg-headers
        """
        return ImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#with_streaming_response
        """
        return ImagesResourceWithStreamingResponse(self)

    def generate(
        self,
        *,
        body: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Proxies an OpenAI image generation request to the configured internal LLM
        endpoint. Supports polling for SDM-3.5 and direct generation for SDXL. Logs
        usage and returns the image content.

        Args: request: The FastAPI Request object. openai_payload: The request body
        containing the image generation parameters (OpenAI format). key_record: The
        validated API key record. key_log_model: Dependency for logging key usage.

        Returns: Response: The generated image file content.

        Raises: HTTPException: 400 If the requested model is not supported.
        HTTPException: 504 If the polling process times out. HTTPException: 502 For LLM
        API, transport, or polling errors.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/images/generations",
            body=maybe_transform(body, image_generate_params.ImageGenerateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncImagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncImagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/kishan20-00/llm_api-python#with_streaming_response
        """
        return AsyncImagesResourceWithStreamingResponse(self)

    async def generate(
        self,
        *,
        body: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Proxies an OpenAI image generation request to the configured internal LLM
        endpoint. Supports polling for SDM-3.5 and direct generation for SDXL. Logs
        usage and returns the image content.

        Args: request: The FastAPI Request object. openai_payload: The request body
        containing the image generation parameters (OpenAI format). key_record: The
        validated API key record. key_log_model: Dependency for logging key usage.

        Returns: Response: The generated image file content.

        Raises: HTTPException: 400 If the requested model is not supported.
        HTTPException: 504 If the polling process times out. HTTPException: 502 For LLM
        API, transport, or polling errors.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/images/generations",
            body=await async_maybe_transform(body, image_generate_params.ImageGenerateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ImagesResourceWithRawResponse:
    def __init__(self, images: ImagesResource) -> None:
        self._images = images

        self.generate = to_raw_response_wrapper(
            images.generate,
        )


class AsyncImagesResourceWithRawResponse:
    def __init__(self, images: AsyncImagesResource) -> None:
        self._images = images

        self.generate = async_to_raw_response_wrapper(
            images.generate,
        )


class ImagesResourceWithStreamingResponse:
    def __init__(self, images: ImagesResource) -> None:
        self._images = images

        self.generate = to_streamed_response_wrapper(
            images.generate,
        )


class AsyncImagesResourceWithStreamingResponse:
    def __init__(self, images: AsyncImagesResource) -> None:
        self._images = images

        self.generate = async_to_streamed_response_wrapper(
            images.generate,
        )
