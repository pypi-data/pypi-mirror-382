# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from greenflash import Greenflash, AsyncGreenflash
from tests.utils import assert_matches_type
from greenflash.types import LogConversionResponse
from greenflash._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConversions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_log(self, client: Greenflash) -> None:
        conversion = client.conversions.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
        )
        assert_matches_type(LogConversionResponse, conversion, path=["response"])

    @parametrize
    def test_method_log_with_all_params(self, client: Greenflash) -> None:
        conversion = client.conversions.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            converted_at=parse_date("2019-12-27"),
            external_conversation_id="conv-456",
            metadata={"sku": "bar"},
            product_id="123e4567-e89b-12d3-a456-426614174001",
            project_id="123e4567-e89b-12d3-a456-426614174002",
        )
        assert_matches_type(LogConversionResponse, conversion, path=["response"])

    @parametrize
    def test_raw_response_log(self, client: Greenflash) -> None:
        response = client.conversions.with_raw_response.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversion = response.parse()
        assert_matches_type(LogConversionResponse, conversion, path=["response"])

    @parametrize
    def test_streaming_response_log(self, client: Greenflash) -> None:
        with client.conversions.with_streaming_response.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversion = response.parse()
            assert_matches_type(LogConversionResponse, conversion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConversions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_log(self, async_client: AsyncGreenflash) -> None:
        conversion = await async_client.conversions.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
        )
        assert_matches_type(LogConversionResponse, conversion, path=["response"])

    @parametrize
    async def test_method_log_with_all_params(self, async_client: AsyncGreenflash) -> None:
        conversion = await async_client.conversions.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
            conversation_id="123e4567-e89b-12d3-a456-426614174000",
            converted_at=parse_date("2019-12-27"),
            external_conversation_id="conv-456",
            metadata={"sku": "bar"},
            product_id="123e4567-e89b-12d3-a456-426614174001",
            project_id="123e4567-e89b-12d3-a456-426614174002",
        )
        assert_matches_type(LogConversionResponse, conversion, path=["response"])

    @parametrize
    async def test_raw_response_log(self, async_client: AsyncGreenflash) -> None:
        response = await async_client.conversions.with_raw_response.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversion = await response.parse()
        assert_matches_type(LogConversionResponse, conversion, path=["response"])

    @parametrize
    async def test_streaming_response_log(self, async_client: AsyncGreenflash) -> None:
        async with async_client.conversions.with_streaming_response.log(
            action="purchase",
            external_user_id="user-123",
            value="99.99",
            value_type="currency",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversion = await response.parse()
            assert_matches_type(LogConversionResponse, conversion, path=["response"])

        assert cast(Any, response.is_closed) is True
