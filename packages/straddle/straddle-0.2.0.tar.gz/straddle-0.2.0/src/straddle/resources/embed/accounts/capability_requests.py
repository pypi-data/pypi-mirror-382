# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from ...._base_client import AsyncPaginator, make_request_options
from ....types.embed.accounts import capability_request_list_params, capability_request_create_params
from ....types.embed.accounts.capability_request_paged_v1 import Data, CapabilityRequestPagedV1

__all__ = ["CapabilityRequestsResource", "AsyncCapabilityRequestsResource"]


class CapabilityRequestsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CapabilityRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return CapabilityRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CapabilityRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return CapabilityRequestsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        businesses: capability_request_create_params.Businesses | Omit = omit,
        charges: capability_request_create_params.Charges | Omit = omit,
        individuals: capability_request_create_params.Individuals | Omit = omit,
        internet: capability_request_create_params.Internet | Omit = omit,
        payouts: capability_request_create_params.Payouts | Omit = omit,
        signed_agreement: capability_request_create_params.SignedAgreement | Omit = omit,
        correlation_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        request_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CapabilityRequestPagedV1:
        """Submits a request to enable a specific capability for an account.

        Use this
        endpoint to request additional features or services for an account.

        Args:
          businesses: Allows the account to accept payments from businesses.

          charges: The charges capability settings for the account.

          individuals: Allows the account to accept payments from individuals.

          internet: Allows the account to accept payments authorized via the internet or mobile
              applications.

          payouts: The payouts capability settings for the account.

          signed_agreement: Allows the account to accept payments authorized by signed agreements or
              contracts.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "idempotency-key": idempotency_key,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/accounts/{account_id}/capability_requests",
            body=maybe_transform(
                {
                    "businesses": businesses,
                    "charges": charges,
                    "individuals": individuals,
                    "internet": internet,
                    "payouts": payouts,
                    "signed_agreement": signed_agreement,
                },
                capability_request_create_params.CapabilityRequestCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CapabilityRequestPagedV1,
        )

    def list(
        self,
        account_id: str,
        *,
        category: Literal["payment_type", "customer_type", "consent_type"] | Omit = omit,
        page_number: int | Omit = omit,
        page_size: int | Omit = omit,
        sort_by: str | Omit = omit,
        sort_order: Literal["asc", "desc"] | Omit = omit,
        status: Literal["active", "inactive", "in_review", "rejected"] | Omit = omit,
        type: Literal["charges", "payouts", "individuals", "businesses", "signed_agreement", "internet"] | Omit = omit,
        correlation_id: str | Omit = omit,
        request_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPageNumberSchema[Data]:
        """Retrieves a list of capability requests associated with an account.

        The requests
        are returned sorted by creation date, with the most recent requests appearing
        first. This endpoint supports advanced sorting and filtering options.

        Args:
          category: Filter capability requests by category.

          page_number: Results page number. Starts at page 1.

          page_size: Page size.Max value: 1000

          sort_by: Sort By.

          sort_order: Sort Order.

          status: Filter capability requests by their current status.

          type: Filter capability requests by the specific type of capability.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            f"/v1/accounts/{account_id}/capability_requests",
            page=SyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "category": category,
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status": status,
                        "type": type,
                    },
                    capability_request_list_params.CapabilityRequestListParams,
                ),
            ),
            model=Data,
        )


class AsyncCapabilityRequestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCapabilityRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCapabilityRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCapabilityRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncCapabilityRequestsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        businesses: capability_request_create_params.Businesses | Omit = omit,
        charges: capability_request_create_params.Charges | Omit = omit,
        individuals: capability_request_create_params.Individuals | Omit = omit,
        internet: capability_request_create_params.Internet | Omit = omit,
        payouts: capability_request_create_params.Payouts | Omit = omit,
        signed_agreement: capability_request_create_params.SignedAgreement | Omit = omit,
        correlation_id: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        request_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CapabilityRequestPagedV1:
        """Submits a request to enable a specific capability for an account.

        Use this
        endpoint to request additional features or services for an account.

        Args:
          businesses: Allows the account to accept payments from businesses.

          charges: The charges capability settings for the account.

          individuals: Allows the account to accept payments from individuals.

          internet: Allows the account to accept payments authorized via the internet or mobile
              applications.

          payouts: The payouts capability settings for the account.

          signed_agreement: Allows the account to accept payments authorized by signed agreements or
              contracts.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "idempotency-key": idempotency_key,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/accounts/{account_id}/capability_requests",
            body=await async_maybe_transform(
                {
                    "businesses": businesses,
                    "charges": charges,
                    "individuals": individuals,
                    "internet": internet,
                    "payouts": payouts,
                    "signed_agreement": signed_agreement,
                },
                capability_request_create_params.CapabilityRequestCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CapabilityRequestPagedV1,
        )

    def list(
        self,
        account_id: str,
        *,
        category: Literal["payment_type", "customer_type", "consent_type"] | Omit = omit,
        page_number: int | Omit = omit,
        page_size: int | Omit = omit,
        sort_by: str | Omit = omit,
        sort_order: Literal["asc", "desc"] | Omit = omit,
        status: Literal["active", "inactive", "in_review", "rejected"] | Omit = omit,
        type: Literal["charges", "payouts", "individuals", "businesses", "signed_agreement", "internet"] | Omit = omit,
        correlation_id: str | Omit = omit,
        request_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Data, AsyncPageNumberSchema[Data]]:
        """Retrieves a list of capability requests associated with an account.

        The requests
        are returned sorted by creation date, with the most recent requests appearing
        first. This endpoint supports advanced sorting and filtering options.

        Args:
          category: Filter capability requests by category.

          page_number: Results page number. Starts at page 1.

          page_size: Page size.Max value: 1000

          sort_by: Sort By.

          sort_order: Sort Order.

          status: Filter capability requests by their current status.

          type: Filter capability requests by the specific type of capability.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "correlation-id": correlation_id,
                    "request-id": request_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            f"/v1/accounts/{account_id}/capability_requests",
            page=AsyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "category": category,
                        "page_number": page_number,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status": status,
                        "type": type,
                    },
                    capability_request_list_params.CapabilityRequestListParams,
                ),
            ),
            model=Data,
        )


class CapabilityRequestsResourceWithRawResponse:
    def __init__(self, capability_requests: CapabilityRequestsResource) -> None:
        self._capability_requests = capability_requests

        self.create = to_raw_response_wrapper(
            capability_requests.create,
        )
        self.list = to_raw_response_wrapper(
            capability_requests.list,
        )


class AsyncCapabilityRequestsResourceWithRawResponse:
    def __init__(self, capability_requests: AsyncCapabilityRequestsResource) -> None:
        self._capability_requests = capability_requests

        self.create = async_to_raw_response_wrapper(
            capability_requests.create,
        )
        self.list = async_to_raw_response_wrapper(
            capability_requests.list,
        )


class CapabilityRequestsResourceWithStreamingResponse:
    def __init__(self, capability_requests: CapabilityRequestsResource) -> None:
        self._capability_requests = capability_requests

        self.create = to_streamed_response_wrapper(
            capability_requests.create,
        )
        self.list = to_streamed_response_wrapper(
            capability_requests.list,
        )


class AsyncCapabilityRequestsResourceWithStreamingResponse:
    def __init__(self, capability_requests: AsyncCapabilityRequestsResource) -> None:
        self._capability_requests = capability_requests

        self.create = async_to_streamed_response_wrapper(
            capability_requests.create,
        )
        self.list = async_to_streamed_response_wrapper(
            capability_requests.list,
        )
