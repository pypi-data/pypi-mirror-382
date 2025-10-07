# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import android_instance_list_params, android_instance_create_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ..types.android_instance import AndroidInstance
from ..types.android_instance_list_response import AndroidInstanceListResponse

__all__ = ["AndroidInstancesResource", "AsyncAndroidInstancesResource"]


class AndroidInstancesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AndroidInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/limrun-inc/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AndroidInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AndroidInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/limrun-inc/python-sdk#with_streaming_response
        """
        return AndroidInstancesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        wait: bool | Omit = omit,
        metadata: android_instance_create_params.Metadata | Omit = omit,
        spec: android_instance_create_params.Spec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AndroidInstance:
        """
        Create an Android instance

        Args:
          wait: Return after the instance is ready to connect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/android_instances",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "spec": spec,
                },
                android_instance_create_params.AndroidInstanceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"wait": wait}, android_instance_create_params.AndroidInstanceCreateParams),
            ),
            cast_to=AndroidInstance,
        )

    def list(
        self,
        *,
        label_selector: str | Omit = omit,
        region: str | Omit = omit,
        state: Literal["unknown", "creating", "ready", "terminated"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AndroidInstanceListResponse:
        """
        List Android instances belonging to given organization

        Args:
          label_selector: Labels filter to apply to Android instances to return. Expects a comma-separated
              list of key=value pairs (e.g., env=prod,region=us-west).

          region: Region where the instance is scheduled on.

          state: State filter to apply to Android instances to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/android_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "label_selector": label_selector,
                        "region": region,
                        "state": state,
                    },
                    android_instance_list_params.AndroidInstanceListParams,
                ),
            ),
            cast_to=AndroidInstanceListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete Android instance with given name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/android_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AndroidInstance:
        """
        Get Android instance with given ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v1/android_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidInstance,
        )


class AsyncAndroidInstancesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAndroidInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/limrun-inc/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAndroidInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAndroidInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/limrun-inc/python-sdk#with_streaming_response
        """
        return AsyncAndroidInstancesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        wait: bool | Omit = omit,
        metadata: android_instance_create_params.Metadata | Omit = omit,
        spec: android_instance_create_params.Spec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AndroidInstance:
        """
        Create an Android instance

        Args:
          wait: Return after the instance is ready to connect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/android_instances",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "spec": spec,
                },
                android_instance_create_params.AndroidInstanceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"wait": wait}, android_instance_create_params.AndroidInstanceCreateParams
                ),
            ),
            cast_to=AndroidInstance,
        )

    async def list(
        self,
        *,
        label_selector: str | Omit = omit,
        region: str | Omit = omit,
        state: Literal["unknown", "creating", "ready", "terminated"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AndroidInstanceListResponse:
        """
        List Android instances belonging to given organization

        Args:
          label_selector: Labels filter to apply to Android instances to return. Expects a comma-separated
              list of key=value pairs (e.g., env=prod,region=us-west).

          region: Region where the instance is scheduled on.

          state: State filter to apply to Android instances to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/android_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "label_selector": label_selector,
                        "region": region,
                        "state": state,
                    },
                    android_instance_list_params.AndroidInstanceListParams,
                ),
            ),
            cast_to=AndroidInstanceListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete Android instance with given name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/android_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AndroidInstance:
        """
        Get Android instance with given ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v1/android_instances/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidInstance,
        )


class AndroidInstancesResourceWithRawResponse:
    def __init__(self, android_instances: AndroidInstancesResource) -> None:
        self._android_instances = android_instances

        self.create = to_raw_response_wrapper(
            android_instances.create,
        )
        self.list = to_raw_response_wrapper(
            android_instances.list,
        )
        self.delete = to_raw_response_wrapper(
            android_instances.delete,
        )
        self.get = to_raw_response_wrapper(
            android_instances.get,
        )


class AsyncAndroidInstancesResourceWithRawResponse:
    def __init__(self, android_instances: AsyncAndroidInstancesResource) -> None:
        self._android_instances = android_instances

        self.create = async_to_raw_response_wrapper(
            android_instances.create,
        )
        self.list = async_to_raw_response_wrapper(
            android_instances.list,
        )
        self.delete = async_to_raw_response_wrapper(
            android_instances.delete,
        )
        self.get = async_to_raw_response_wrapper(
            android_instances.get,
        )


class AndroidInstancesResourceWithStreamingResponse:
    def __init__(self, android_instances: AndroidInstancesResource) -> None:
        self._android_instances = android_instances

        self.create = to_streamed_response_wrapper(
            android_instances.create,
        )
        self.list = to_streamed_response_wrapper(
            android_instances.list,
        )
        self.delete = to_streamed_response_wrapper(
            android_instances.delete,
        )
        self.get = to_streamed_response_wrapper(
            android_instances.get,
        )


class AsyncAndroidInstancesResourceWithStreamingResponse:
    def __init__(self, android_instances: AsyncAndroidInstancesResource) -> None:
        self._android_instances = android_instances

        self.create = async_to_streamed_response_wrapper(
            android_instances.create,
        )
        self.list = async_to_streamed_response_wrapper(
            android_instances.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            android_instances.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            android_instances.get,
        )
