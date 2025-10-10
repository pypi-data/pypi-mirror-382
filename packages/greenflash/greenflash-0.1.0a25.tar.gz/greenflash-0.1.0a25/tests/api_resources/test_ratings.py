# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from greenflash import Greenflash, AsyncGreenflash
from tests.utils import assert_matches_type
from greenflash.types import LogRatingResponse
from greenflash._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRatings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_log(self, client: Greenflash) -> None:
        rating = client.ratings.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
        )
        assert_matches_type(LogRatingResponse, rating, path=["response"])

    @parametrize
    def test_method_log_with_all_params(self, client: Greenflash) -> None:
        rating = client.ratings.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
            conversation_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            external_conversation_id="123e4567-e89b-12d3-a456-426614174000",
            external_message_id="externalMessageId",
            feedback="Helpful response!",
            message_id="messageId",
            rated_at=parse_date("2019-12-27"),
        )
        assert_matches_type(LogRatingResponse, rating, path=["response"])

    @parametrize
    def test_raw_response_log(self, client: Greenflash) -> None:
        response = client.ratings.with_raw_response.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rating = response.parse()
        assert_matches_type(LogRatingResponse, rating, path=["response"])

    @parametrize
    def test_streaming_response_log(self, client: Greenflash) -> None:
        with client.ratings.with_streaming_response.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rating = response.parse()
            assert_matches_type(LogRatingResponse, rating, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRatings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_log(self, async_client: AsyncGreenflash) -> None:
        rating = await async_client.ratings.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
        )
        assert_matches_type(LogRatingResponse, rating, path=["response"])

    @parametrize
    async def test_method_log_with_all_params(self, async_client: AsyncGreenflash) -> None:
        rating = await async_client.ratings.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
            conversation_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            external_conversation_id="123e4567-e89b-12d3-a456-426614174000",
            external_message_id="externalMessageId",
            feedback="Helpful response!",
            message_id="messageId",
            rated_at=parse_date("2019-12-27"),
        )
        assert_matches_type(LogRatingResponse, rating, path=["response"])

    @parametrize
    async def test_raw_response_log(self, async_client: AsyncGreenflash) -> None:
        response = await async_client.ratings.with_raw_response.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rating = await response.parse()
        assert_matches_type(LogRatingResponse, rating, path=["response"])

    @parametrize
    async def test_streaming_response_log(self, async_client: AsyncGreenflash) -> None:
        async with async_client.ratings.with_streaming_response.log(
            product_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            rating=4,
            rating_max=5,
            rating_min=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rating = await response.parse()
            assert_matches_type(LogRatingResponse, rating, path=["response"])

        assert cast(Any, response.is_closed) is True
