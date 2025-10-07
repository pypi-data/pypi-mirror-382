# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from llm_api import LlmAPI, AsyncLlmAPI
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAudio:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_transcription(self, client: LlmAPI) -> None:
        audio = client.audio.create_transcription(
            file=b"raw file contents",
        )
        assert_matches_type(object, audio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_transcription_with_all_params(self, client: LlmAPI) -> None:
        audio = client.audio.create_transcription(
            file=b"raw file contents",
            model="model",
            response_format="response_format",
        )
        assert_matches_type(object, audio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_transcription(self, client: LlmAPI) -> None:
        response = client.audio.with_raw_response.create_transcription(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = response.parse()
        assert_matches_type(object, audio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_transcription(self, client: LlmAPI) -> None:
        with client.audio.with_streaming_response.create_transcription(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = response.parse()
            assert_matches_type(object, audio, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAudio:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_transcription(self, async_client: AsyncLlmAPI) -> None:
        audio = await async_client.audio.create_transcription(
            file=b"raw file contents",
        )
        assert_matches_type(object, audio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_transcription_with_all_params(self, async_client: AsyncLlmAPI) -> None:
        audio = await async_client.audio.create_transcription(
            file=b"raw file contents",
            model="model",
            response_format="response_format",
        )
        assert_matches_type(object, audio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_transcription(self, async_client: AsyncLlmAPI) -> None:
        response = await async_client.audio.with_raw_response.create_transcription(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio = await response.parse()
        assert_matches_type(object, audio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_transcription(self, async_client: AsyncLlmAPI) -> None:
        async with async_client.audio.with_streaming_response.create_transcription(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio = await response.parse()
            assert_matches_type(object, audio, path=["response"])

        assert cast(Any, response.is_closed) is True
