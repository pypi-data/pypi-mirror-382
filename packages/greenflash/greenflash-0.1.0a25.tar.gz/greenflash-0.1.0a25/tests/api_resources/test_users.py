# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from greenflash import Greenflash, AsyncGreenflash
from tests.utils import assert_matches_type
from greenflash.types import CreateUserResponse, UpdateUserResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Greenflash) -> None:
        user = client.users.create(
            external_user_id="user-123",
        )
        assert_matches_type(CreateUserResponse, user, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Greenflash) -> None:
        user = client.users.create(
            external_user_id="user-123",
            anonymized=False,
            email="alice@example.com",
            external_organization_id="org-456",
            metadata={"plan": "bar"},
            name="Alice Example",
            phone="+15551234567",
        )
        assert_matches_type(CreateUserResponse, user, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Greenflash) -> None:
        response = client.users.with_raw_response.create(
            external_user_id="user-123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(CreateUserResponse, user, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Greenflash) -> None:
        with client.users.with_streaming_response.create(
            external_user_id="user-123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(CreateUserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Greenflash) -> None:
        user = client.users.update(
            user_id="userId",
        )
        assert_matches_type(UpdateUserResponse, user, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Greenflash) -> None:
        user = client.users.update(
            user_id="userId",
            anonymized=True,
            email="alice.updated@example.com",
            external_organization_id="externalOrganizationId",
            metadata={"plan": "bar"},
            name="Alice Updated",
            phone="phone",
        )
        assert_matches_type(UpdateUserResponse, user, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Greenflash) -> None:
        response = client.users.with_raw_response.update(
            user_id="userId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UpdateUserResponse, user, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Greenflash) -> None:
        with client.users.with_streaming_response.update(
            user_id="userId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UpdateUserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Greenflash) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.users.with_raw_response.update(
                user_id="",
            )


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncGreenflash) -> None:
        user = await async_client.users.create(
            external_user_id="user-123",
        )
        assert_matches_type(CreateUserResponse, user, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGreenflash) -> None:
        user = await async_client.users.create(
            external_user_id="user-123",
            anonymized=False,
            email="alice@example.com",
            external_organization_id="org-456",
            metadata={"plan": "bar"},
            name="Alice Example",
            phone="+15551234567",
        )
        assert_matches_type(CreateUserResponse, user, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGreenflash) -> None:
        response = await async_client.users.with_raw_response.create(
            external_user_id="user-123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(CreateUserResponse, user, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGreenflash) -> None:
        async with async_client.users.with_streaming_response.create(
            external_user_id="user-123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(CreateUserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncGreenflash) -> None:
        user = await async_client.users.update(
            user_id="userId",
        )
        assert_matches_type(UpdateUserResponse, user, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncGreenflash) -> None:
        user = await async_client.users.update(
            user_id="userId",
            anonymized=True,
            email="alice.updated@example.com",
            external_organization_id="externalOrganizationId",
            metadata={"plan": "bar"},
            name="Alice Updated",
            phone="phone",
        )
        assert_matches_type(UpdateUserResponse, user, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncGreenflash) -> None:
        response = await async_client.users.with_raw_response.update(
            user_id="userId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UpdateUserResponse, user, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncGreenflash) -> None:
        async with async_client.users.with_streaming_response.update(
            user_id="userId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UpdateUserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncGreenflash) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.users.with_raw_response.update(
                user_id="",
            )
