# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from limrun_api import Limrun, AsyncLimrun
from tests.utils import assert_matches_type
from limrun_api.types import IosInstance, IosInstanceListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIosInstances:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Limrun) -> None:
        ios_instance = client.ios_instances.create()
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Limrun) -> None:
        ios_instance = client.ios_instances.create(
            wait=True,
            metadata={
                "display_name": "displayName",
                "labels": {"foo": "string"},
            },
            spec={
                "clues": [
                    {
                        "kind": "ClientIP",
                        "client_ip": "clientIp",
                    }
                ],
                "hard_timeout": "hardTimeout",
                "inactivity_timeout": "inactivityTimeout",
                "initial_assets": [
                    {
                        "kind": "App",
                        "source": "URL",
                        "asset_name": "assetName",
                        "url": "url",
                    }
                ],
                "region": "region",
            },
        )
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Limrun) -> None:
        response = client.ios_instances.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = response.parse()
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Limrun) -> None:
        with client.ios_instances.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = response.parse()
            assert_matches_type(IosInstance, ios_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Limrun) -> None:
        ios_instance = client.ios_instances.list()
        assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Limrun) -> None:
        ios_instance = client.ios_instances.list(
            label_selector="env=prod,version=1.2",
            region="region",
            state="unknown",
        )
        assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Limrun) -> None:
        response = client.ios_instances.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = response.parse()
        assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Limrun) -> None:
        with client.ios_instances.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = response.parse()
            assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Limrun) -> None:
        ios_instance = client.ios_instances.delete(
            "id",
        )
        assert ios_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Limrun) -> None:
        response = client.ios_instances.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = response.parse()
        assert ios_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Limrun) -> None:
        with client.ios_instances.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = response.parse()
            assert ios_instance is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Limrun) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.ios_instances.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Limrun) -> None:
        ios_instance = client.ios_instances.get(
            "id",
        )
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Limrun) -> None:
        response = client.ios_instances.with_raw_response.get(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = response.parse()
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Limrun) -> None:
        with client.ios_instances.with_streaming_response.get(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = response.parse()
            assert_matches_type(IosInstance, ios_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Limrun) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.ios_instances.with_raw_response.get(
                "",
            )


class TestAsyncIosInstances:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncLimrun) -> None:
        ios_instance = await async_client.ios_instances.create()
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLimrun) -> None:
        ios_instance = await async_client.ios_instances.create(
            wait=True,
            metadata={
                "display_name": "displayName",
                "labels": {"foo": "string"},
            },
            spec={
                "clues": [
                    {
                        "kind": "ClientIP",
                        "client_ip": "clientIp",
                    }
                ],
                "hard_timeout": "hardTimeout",
                "inactivity_timeout": "inactivityTimeout",
                "initial_assets": [
                    {
                        "kind": "App",
                        "source": "URL",
                        "asset_name": "assetName",
                        "url": "url",
                    }
                ],
                "region": "region",
            },
        )
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLimrun) -> None:
        response = await async_client.ios_instances.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = await response.parse()
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLimrun) -> None:
        async with async_client.ios_instances.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = await response.parse()
            assert_matches_type(IosInstance, ios_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLimrun) -> None:
        ios_instance = await async_client.ios_instances.list()
        assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLimrun) -> None:
        ios_instance = await async_client.ios_instances.list(
            label_selector="env=prod,version=1.2",
            region="region",
            state="unknown",
        )
        assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLimrun) -> None:
        response = await async_client.ios_instances.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = await response.parse()
        assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLimrun) -> None:
        async with async_client.ios_instances.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = await response.parse()
            assert_matches_type(IosInstanceListResponse, ios_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncLimrun) -> None:
        ios_instance = await async_client.ios_instances.delete(
            "id",
        )
        assert ios_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncLimrun) -> None:
        response = await async_client.ios_instances.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = await response.parse()
        assert ios_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncLimrun) -> None:
        async with async_client.ios_instances.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = await response.parse()
            assert ios_instance is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncLimrun) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.ios_instances.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncLimrun) -> None:
        ios_instance = await async_client.ios_instances.get(
            "id",
        )
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncLimrun) -> None:
        response = await async_client.ios_instances.with_raw_response.get(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ios_instance = await response.parse()
        assert_matches_type(IosInstance, ios_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncLimrun) -> None:
        async with async_client.ios_instances.with_streaming_response.get(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ios_instance = await response.parse()
            assert_matches_type(IosInstance, ios_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncLimrun) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.ios_instances.with_raw_response.get(
                "",
            )
