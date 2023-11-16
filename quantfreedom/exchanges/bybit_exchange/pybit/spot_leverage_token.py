from enum import Enum


class SpotLeverageToken(str, Enum):
    GET_LEVERAGED_TOKEN_INFO = "/v5/spot-lever-token/info"
    GET_LEVERAGED_TOKEN_MARKET = "/v5/spot-lever-token/reference"
    PURCHASE = "/v5/spot-lever-token/purchase"
    REDEEM = "/v5/spot-lever-token/redeem"
    GET_PURCHASE_REDEMPTION_RECORDS = "/v5/spot-lever-token/order-record"

    def __str__(self) -> str:
        return self.value
