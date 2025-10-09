# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LinkedBankAccountCreateParams", "BankAccount"]


class LinkedBankAccountCreateParams(TypedDict, total=False):
    account_id: Required[Optional[str]]
    """
    The unique identifier of the Straddle account to associate this bank account
    with.
    """

    bank_account: Required[BankAccount]

    description: Optional[str]
    """Optional description for the bank account."""

    metadata: Optional[Dict[str, Optional[str]]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the linked bank account in a
    structured format.
    """

    platform_id: Optional[str]
    """
    The unique identifier of the Straddle Platform to associate this bank account
    with.
    """

    purposes: Optional[List[Literal["charges", "payouts", "billing"]]]
    """The purposes for the linked bank account."""

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    idempotency_key: Annotated[str, PropertyInfo(alias="idempotency-key")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]


class BankAccount(TypedDict, total=False):
    account_holder: Required[str]
    """The name of the account holder as it appears on the bank account.

    Typically, this is the legal name of the business associated with the account.
    """

    account_number: Required[str]
    """The bank account number."""

    routing_number: Required[str]
    """The routing number of the bank account."""
