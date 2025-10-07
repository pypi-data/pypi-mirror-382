# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["EntryPostParams"]


class EntryPostParams(TypedDict, total=False):
    amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="amountUsdCents")]]
    """The amount of the ledger entry in cents.

    Positive for charges, negative for payments.
    """

    entry_category: Required[Annotated[Literal["charge", "payment", "adjustment"], PropertyInfo(alias="entryCategory")]]

    line_item_id: Required[Annotated[str, PropertyInfo(alias="lineItemId")]]
    """The line item ID associated with the ledger entry."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """The order ID associated with the ledger entry."""

    description: str
    """The description of the ledger entry."""

    entry_type: Annotated[
        Union[
            Literal[
                "insurance-payment",
                "institution-payment",
                "patient-payment",
                "write-off",
                "institution-discount",
                "contracted-payer-adjustment",
                "patient-pay-adjustment",
                "charge",
                "payment",
                "adjustment",
            ],
            object,
        ],
        PropertyInfo(alias="entryType"),
    ]
    """The type of ledger entry."""

    metadata: Dict[str, object]
    """Any optional metadata to associate with the ledger entry."""

    payment_source: Annotated[str, PropertyInfo(alias="paymentSource")]
    """The source of the payment, e.g. payer ID, patient ID, etc."""

    posted_at: Annotated[str, PropertyInfo(alias="postedAt")]
    """The date and time the ledger entry was posted."""

    idempotency_key: Annotated[str, PropertyInfo(alias="idempotency-key")]
