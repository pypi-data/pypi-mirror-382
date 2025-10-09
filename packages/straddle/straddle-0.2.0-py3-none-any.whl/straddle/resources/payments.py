# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import date, datetime
from typing_extensions import Literal

import httpx

from ..types import payment_list_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, strip_not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from .._base_client import AsyncPaginator, make_request_options
from ..types.payment_summary_paged_v1 import Data

__all__ = ["PaymentsResource", "AsyncPaymentsResource"]


class PaymentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PaymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return PaymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PaymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return PaymentsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        customer_id: str | Omit = omit,
        default_page_size: int | Omit = omit,
        default_sort: Literal["created_at", "payment_date", "effective_at", "id", "amount"] | Omit = omit,
        default_sort_order: Literal["asc", "desc"] | Omit = omit,
        external_id: str | Omit = omit,
        funding_id: str | Omit = omit,
        max_amount: int | Omit = omit,
        max_created_at: Union[str, datetime] | Omit = omit,
        max_effective_at: Union[str, datetime] | Omit = omit,
        max_payment_date: Union[str, date] | Omit = omit,
        min_amount: int | Omit = omit,
        min_created_at: Union[str, datetime] | Omit = omit,
        min_effective_at: Union[str, datetime] | Omit = omit,
        min_payment_date: Union[str, date] | Omit = omit,
        page_number: int | Omit = omit,
        page_size: int | Omit = omit,
        paykey: str | Omit = omit,
        paykey_id: str | Omit = omit,
        payment_id: str | Omit = omit,
        payment_status: List[
            Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
        ]
        | Omit = omit,
        payment_type: List[Literal["charge", "payout"]] | Omit = omit,
        search_text: str | Omit = omit,
        sort_by: Literal["created_at", "payment_date", "effective_at", "id", "amount"] | Omit = omit,
        sort_order: Literal["asc", "desc"] | Omit = omit,
        status_reason: List[
            Literal[
                "insufficient_funds",
                "closed_bank_account",
                "invalid_bank_account",
                "invalid_routing",
                "disputed",
                "payment_stopped",
                "owner_deceased",
                "frozen_bank_account",
                "risk_review",
                "fraudulent",
                "duplicate_entry",
                "invalid_paykey",
                "payment_blocked",
                "amount_too_large",
                "too_many_attempts",
                "internal_system_error",
                "user_request",
                "ok",
                "other_network_return",
                "payout_refused",
            ]
        ]
        | Omit = omit,
        status_source: List[Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]]
        | Omit = omit,
        correlation_id: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPageNumberSchema[Data]:
        """
        Search for payments, including `charges` and `payouts`, using a variety of
        criteria. This endpoint supports advanced sorting and filtering options.

        Args:
          customer_id: Search using the `customer_id` of a `charge` or `payout`.

          default_sort: The field to sort the results by.

          external_id: Search using the `external_id` of a `charge` or `payout`.

          funding_id: Search using the `funding_id` of a `charge` or `payout`.

          max_amount: Search using a maximum `amount` of a `charge` or `payout`.

          max_created_at: Search using the latest `created_at` date of a `charge` or `payout`.

          max_effective_at: Search using the latest `effective_date` of a `charge` or `payout`.

          max_payment_date: Search using the latest `payment_date` of a `charge` or `payout`.

          min_amount: Search using the minimum `amount of a `charge`or`payout`.

          min_created_at: Search using the earliest `created_at` date of a `charge` or `payout`.

          min_effective_at: Search using the earliest `effective_date` of a `charge` or `payout`.

          min_payment_date: Search using the earliest ` `of a `charge` or `payout`.

          page_number: Results page number. Starts at page 1.

          page_size: Results page size. Max value: 1000

          paykey: Search using the `paykey` of a `charge` or `payout`.

          paykey_id: Search using the `paykey_id` of a `charge` or `payout`.

          payment_id: Search using the `id` of a `charge` or `payout`.

          payment_status: Search by the status of a `charge` or `payout`.

          payment_type: Search by the type of a `charge` or `payout`.

          search_text: Search using a text string associated with a `charge` or `payout`.

          sort_by: The field to sort the results by.

          status_reason: Reason for latest payment status change.

          status_source: Source of latest payment status change.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            "/v1/payments",
            page=SyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "customer_id": customer_id,
                        "default_page_size": default_page_size,
                        "default_sort": default_sort,
                        "default_sort_order": default_sort_order,
                        "external_id": external_id,
                        "funding_id": funding_id,
                        "max_amount": max_amount,
                        "max_created_at": max_created_at,
                        "max_effective_at": max_effective_at,
                        "max_payment_date": max_payment_date,
                        "min_amount": min_amount,
                        "min_created_at": min_created_at,
                        "min_effective_at": min_effective_at,
                        "min_payment_date": min_payment_date,
                        "page_number": page_number,
                        "page_size": page_size,
                        "paykey": paykey,
                        "paykey_id": paykey_id,
                        "payment_id": payment_id,
                        "payment_status": payment_status,
                        "payment_type": payment_type,
                        "search_text": search_text,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status_reason": status_reason,
                        "status_source": status_source,
                    },
                    payment_list_params.PaymentListParams,
                ),
            ),
            model=Data,
        )


class AsyncPaymentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPaymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPaymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPaymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncPaymentsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        customer_id: str | Omit = omit,
        default_page_size: int | Omit = omit,
        default_sort: Literal["created_at", "payment_date", "effective_at", "id", "amount"] | Omit = omit,
        default_sort_order: Literal["asc", "desc"] | Omit = omit,
        external_id: str | Omit = omit,
        funding_id: str | Omit = omit,
        max_amount: int | Omit = omit,
        max_created_at: Union[str, datetime] | Omit = omit,
        max_effective_at: Union[str, datetime] | Omit = omit,
        max_payment_date: Union[str, date] | Omit = omit,
        min_amount: int | Omit = omit,
        min_created_at: Union[str, datetime] | Omit = omit,
        min_effective_at: Union[str, datetime] | Omit = omit,
        min_payment_date: Union[str, date] | Omit = omit,
        page_number: int | Omit = omit,
        page_size: int | Omit = omit,
        paykey: str | Omit = omit,
        paykey_id: str | Omit = omit,
        payment_id: str | Omit = omit,
        payment_status: List[
            Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
        ]
        | Omit = omit,
        payment_type: List[Literal["charge", "payout"]] | Omit = omit,
        search_text: str | Omit = omit,
        sort_by: Literal["created_at", "payment_date", "effective_at", "id", "amount"] | Omit = omit,
        sort_order: Literal["asc", "desc"] | Omit = omit,
        status_reason: List[
            Literal[
                "insufficient_funds",
                "closed_bank_account",
                "invalid_bank_account",
                "invalid_routing",
                "disputed",
                "payment_stopped",
                "owner_deceased",
                "frozen_bank_account",
                "risk_review",
                "fraudulent",
                "duplicate_entry",
                "invalid_paykey",
                "payment_blocked",
                "amount_too_large",
                "too_many_attempts",
                "internal_system_error",
                "user_request",
                "ok",
                "other_network_return",
                "payout_refused",
            ]
        ]
        | Omit = omit,
        status_source: List[Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]]
        | Omit = omit,
        correlation_id: str | Omit = omit,
        request_id: str | Omit = omit,
        straddle_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Data, AsyncPageNumberSchema[Data]]:
        """
        Search for payments, including `charges` and `payouts`, using a variety of
        criteria. This endpoint supports advanced sorting and filtering options.

        Args:
          customer_id: Search using the `customer_id` of a `charge` or `payout`.

          default_sort: The field to sort the results by.

          external_id: Search using the `external_id` of a `charge` or `payout`.

          funding_id: Search using the `funding_id` of a `charge` or `payout`.

          max_amount: Search using a maximum `amount` of a `charge` or `payout`.

          max_created_at: Search using the latest `created_at` date of a `charge` or `payout`.

          max_effective_at: Search using the latest `effective_date` of a `charge` or `payout`.

          max_payment_date: Search using the latest `payment_date` of a `charge` or `payout`.

          min_amount: Search using the minimum `amount of a `charge`or`payout`.

          min_created_at: Search using the earliest `created_at` date of a `charge` or `payout`.

          min_effective_at: Search using the earliest `effective_date` of a `charge` or `payout`.

          min_payment_date: Search using the earliest ` `of a `charge` or `payout`.

          page_number: Results page number. Starts at page 1.

          page_size: Results page size. Max value: 1000

          paykey: Search using the `paykey` of a `charge` or `payout`.

          paykey_id: Search using the `paykey_id` of a `charge` or `payout`.

          payment_id: Search using the `id` of a `charge` or `payout`.

          payment_status: Search by the status of a `charge` or `payout`.

          payment_type: Search by the type of a `charge` or `payout`.

          search_text: Search using a text string associated with a `charge` or `payout`.

          sort_by: The field to sort the results by.

          status_reason: Reason for latest payment status change.

          status_source: Source of latest payment status change.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get_api_list(
            "/v1/payments",
            page=AsyncPageNumberSchema[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "customer_id": customer_id,
                        "default_page_size": default_page_size,
                        "default_sort": default_sort,
                        "default_sort_order": default_sort_order,
                        "external_id": external_id,
                        "funding_id": funding_id,
                        "max_amount": max_amount,
                        "max_created_at": max_created_at,
                        "max_effective_at": max_effective_at,
                        "max_payment_date": max_payment_date,
                        "min_amount": min_amount,
                        "min_created_at": min_created_at,
                        "min_effective_at": min_effective_at,
                        "min_payment_date": min_payment_date,
                        "page_number": page_number,
                        "page_size": page_size,
                        "paykey": paykey,
                        "paykey_id": paykey_id,
                        "payment_id": payment_id,
                        "payment_status": payment_status,
                        "payment_type": payment_type,
                        "search_text": search_text,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "status_reason": status_reason,
                        "status_source": status_source,
                    },
                    payment_list_params.PaymentListParams,
                ),
            ),
            model=Data,
        )


class PaymentsResourceWithRawResponse:
    def __init__(self, payments: PaymentsResource) -> None:
        self._payments = payments

        self.list = to_raw_response_wrapper(
            payments.list,
        )


class AsyncPaymentsResourceWithRawResponse:
    def __init__(self, payments: AsyncPaymentsResource) -> None:
        self._payments = payments

        self.list = async_to_raw_response_wrapper(
            payments.list,
        )


class PaymentsResourceWithStreamingResponse:
    def __init__(self, payments: PaymentsResource) -> None:
        self._payments = payments

        self.list = to_streamed_response_wrapper(
            payments.list,
        )


class AsyncPaymentsResourceWithStreamingResponse:
    def __init__(self, payments: AsyncPaymentsResource) -> None:
        self._payments = payments

        self.list = async_to_streamed_response_wrapper(
            payments.list,
        )
