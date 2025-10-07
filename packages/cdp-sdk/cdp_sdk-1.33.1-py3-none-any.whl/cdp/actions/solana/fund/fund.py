from typing import Literal

from pydantic import BaseModel

from cdp.actions.types import FundOperationResult
from cdp.actions.util import format_units
from cdp.api_clients import ApiClients
from cdp.openapi_client.models.create_payment_transfer_quote_request import (
    CreatePaymentTransferQuoteRequest,
)
from cdp.openapi_client.models.crypto_rail_address import CryptoRailAddress
from cdp.openapi_client.models.payment_method_request import PaymentMethodRequest
from cdp.openapi_client.models.transfer_source import TransferSource
from cdp.openapi_client.models.transfer_target import TransferTarget


class SolanaFundOptions(BaseModel):
    """The options for funding a Solana account."""

    # The amount of the token to fund
    amount: int

    # The token to fund
    token: Literal["sol", "usdc"]


async def fund(
    api_clients: ApiClients,
    address: str,
    fund_options: SolanaFundOptions,
) -> FundOperationResult:
    """Fund a Solana account.

    Deprecated. This function will be removed in a future version.
    Consider using our Onramp API instead. See https://docs.cdp.coinbase.com/api-reference/v2/rest-api/onramp/create-an-onramp-order.
    """
    payment_methods = await api_clients.payments.get_payment_methods()

    card_payment_method = next(
        (
            method
            for method in payment_methods
            if method.type == "card" and "source" in method.actions
        ),
        None,
    )

    if not card_payment_method:
        raise ValueError("No card found to fund account")

    decimals = 9 if fund_options.token == "sol" else 6
    amount = format_units(fund_options.amount, decimals)

    create_payment_transfer_request = CreatePaymentTransferQuoteRequest(
        source_type="payment_method",
        source=TransferSource(PaymentMethodRequest(id=card_payment_method.id)),
        target_type="crypto_rail",
        target=TransferTarget(
            CryptoRailAddress(currency=fund_options.token, network="solana", address=address)
        ),
        amount=amount,
        currency=fund_options.token,
        execute=True,
    )

    response = await api_clients.payments.create_payment_transfer_quote(
        create_payment_transfer_quote_request=create_payment_transfer_request,
    )

    return FundOperationResult(
        id=response.transfer.id,
        network=response.transfer.target.actual_instance.network,
        target_amount=response.transfer.target_amount,
        target_currency=response.transfer.target_currency,
        status=response.transfer.status,
        transaction_hash=response.transfer.transaction_hash,
    )
