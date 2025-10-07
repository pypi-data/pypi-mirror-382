# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import asset_get_params, asset_list_params, asset_get_or_create_params
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
from ..types.asset import Asset
from .._base_client import make_request_options
from ..types.asset_list_response import AssetListResponse
from ..types.asset_get_or_create_response import AssetGetOrCreateResponse

__all__ = ["AssetsResource", "AsyncAssetsResource"]


class AssetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/limrun-inc/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/limrun-inc/python-sdk#with_streaming_response
        """
        return AssetsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        include_download_url: bool | Omit = omit,
        include_upload_url: bool | Omit = omit,
        name_filter: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AssetListResponse:
        """List organization's all assets with given filters.

        If none given, return all
        assets.

        Args:
          include_download_url: Toggles whether a download URL should be included in the response

          include_upload_url: Toggles whether an upload URL should be included in the response

          name_filter: Query by file name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/assets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_download_url": include_download_url,
                        "include_upload_url": include_upload_url,
                        "name_filter": name_filter,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            cast_to=AssetListResponse,
        )

    def get(
        self,
        asset_id: str,
        *,
        include_download_url: bool | Omit = omit,
        include_upload_url: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Asset:
        """
        Get the asset with given ID.

        Args:
          include_download_url: Toggles whether a download URL should be included in the response

          include_upload_url: Toggles whether an upload URL should be included in the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        return self._get(
            f"/v1/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_download_url": include_download_url,
                        "include_upload_url": include_upload_url,
                    },
                    asset_get_params.AssetGetParams,
                ),
            ),
            cast_to=Asset,
        )

    def get_or_create(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AssetGetOrCreateResponse:
        """Creates an asset and returns upload and download URLs.

        If there is a
        corresponding file uploaded in the storage with given name, its MD5 is returned
        so you can check if a re-upload is necessary. If no MD5 is returned, then there
        is no corresponding file in the storage so downloading it directly or using it
        in instances will fail until you use the returned upload URL to submit the file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/v1/assets",
            body=maybe_transform({"name": name}, asset_get_or_create_params.AssetGetOrCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetGetOrCreateResponse,
        )


class AsyncAssetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/limrun-inc/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/limrun-inc/python-sdk#with_streaming_response
        """
        return AsyncAssetsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        include_download_url: bool | Omit = omit,
        include_upload_url: bool | Omit = omit,
        name_filter: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AssetListResponse:
        """List organization's all assets with given filters.

        If none given, return all
        assets.

        Args:
          include_download_url: Toggles whether a download URL should be included in the response

          include_upload_url: Toggles whether an upload URL should be included in the response

          name_filter: Query by file name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/assets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include_download_url": include_download_url,
                        "include_upload_url": include_upload_url,
                        "name_filter": name_filter,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            cast_to=AssetListResponse,
        )

    async def get(
        self,
        asset_id: str,
        *,
        include_download_url: bool | Omit = omit,
        include_upload_url: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Asset:
        """
        Get the asset with given ID.

        Args:
          include_download_url: Toggles whether a download URL should be included in the response

          include_upload_url: Toggles whether an upload URL should be included in the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        return await self._get(
            f"/v1/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include_download_url": include_download_url,
                        "include_upload_url": include_upload_url,
                    },
                    asset_get_params.AssetGetParams,
                ),
            ),
            cast_to=Asset,
        )

    async def get_or_create(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AssetGetOrCreateResponse:
        """Creates an asset and returns upload and download URLs.

        If there is a
        corresponding file uploaded in the storage with given name, its MD5 is returned
        so you can check if a re-upload is necessary. If no MD5 is returned, then there
        is no corresponding file in the storage so downloading it directly or using it
        in instances will fail until you use the returned upload URL to submit the file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/v1/assets",
            body=await async_maybe_transform({"name": name}, asset_get_or_create_params.AssetGetOrCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetGetOrCreateResponse,
        )


class AssetsResourceWithRawResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_raw_response_wrapper(
            assets.list,
        )
        self.get = to_raw_response_wrapper(
            assets.get,
        )
        self.get_or_create = to_raw_response_wrapper(
            assets.get_or_create,
        )


class AsyncAssetsResourceWithRawResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_raw_response_wrapper(
            assets.list,
        )
        self.get = async_to_raw_response_wrapper(
            assets.get,
        )
        self.get_or_create = async_to_raw_response_wrapper(
            assets.get_or_create,
        )


class AssetsResourceWithStreamingResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_streamed_response_wrapper(
            assets.list,
        )
        self.get = to_streamed_response_wrapper(
            assets.get,
        )
        self.get_or_create = to_streamed_response_wrapper(
            assets.get_or_create,
        )


class AsyncAssetsResourceWithStreamingResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_streamed_response_wrapper(
            assets.list,
        )
        self.get = async_to_streamed_response_wrapper(
            assets.get,
        )
        self.get_or_create = async_to_streamed_response_wrapper(
            assets.get_or_create,
        )
