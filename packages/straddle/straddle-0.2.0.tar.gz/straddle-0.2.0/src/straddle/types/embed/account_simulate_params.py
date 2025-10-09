# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["AccountSimulateParams"]


class AccountSimulateParams(TypedDict, total=False):
    final_status: Literal["onboarding", "active"]

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    idempotency_key: Annotated[str, PropertyInfo(alias="idempotency-key")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]
