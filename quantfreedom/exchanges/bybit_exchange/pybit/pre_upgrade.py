from enum import Enum


class PreUpgrade(str, Enum):
    GET_PRE_UPGRADE_ORDER_HISTORY = "/v5/pre-upgrade/order/history"
    GET_PRE_UPGRADE_TRADE_HISTORY = "/v5/pre-upgrade/execution/list"
    GET_PRE_UPGRADE_CLOSED_PNL = "/v5/pre-upgrade/position/closed-pnl"
    GET_PRE_UPGRADE_TRANSACTION_LOG = "/v5/pre-upgrade/account/transaction-log"
    GET_PRE_UPGRADE_OPTION_DELIVERY_RECORD = "/v5/pre-upgrade/asset/delivery-record"
    GET_PRE_UPGRADE_USDC_SESSION_SETTLEMENT = "/v5/pre-upgrade/asset/settlement-record"

    def __str__(self) -> str:
        return self.value
