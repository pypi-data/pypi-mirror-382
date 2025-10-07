# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from llm_api import LlmAPI, AsyncLlmAPI
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChat:
    parametrize = pytest.mark.parametrize(
        "client", [False, True], indirect=True, ids=["loose", "strict"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_completion(self, client: LlmAPI) -> None:
        chat = client.chat.create_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="deepseek-001",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            stream=False,
        )
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_completion(self, client: LlmAPI) -> None:
        response = client.chat.with_raw_response.create_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="deepseek-001",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            stream=False,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = response.parse()
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_completion(self, client: LlmAPI) -> None:
        with client.chat.with_streaming_response.create_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="deepseek-001",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = response.parse()
            assert_matches_type(object, chat, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncChat:
    parametrize = pytest.mark.parametrize(
        "async_client",
        [False, True, {"http_client": "aiohttp"}],
        indirect=True,
        ids=["loose", "strict", "aiohttp"],
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_completion(self, async_client: AsyncLlmAPI) -> None:
        chat = await async_client.chat.create_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="deepseek-001",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            stream=False,
        )
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_completion(
        self, async_client: AsyncLlmAPI
    ) -> None:
        response = await async_client.chat.with_raw_response.create_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="deepseek-001",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            stream=False,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = await response.parse()
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_completion(
        self, async_client: AsyncLlmAPI
    ) -> None:
        async with async_client.chat.with_streaming_response.create_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="deepseek-001",
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = await response.parse()
            assert_matches_type(object, chat, path=["response"])

        assert cast(Any, response.is_closed) is True
