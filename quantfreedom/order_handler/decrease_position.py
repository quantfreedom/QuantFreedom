from quantfreedom.enums import AccountState, LoggerFuncType, OrderResult, OrderStatus, StringerFuncType
from logging import getLogger

logger = getLogger("info")


class LongDecreasePosition:
    def __init__(
        self,
        market_fee_pct: float,
        exit_fee_pct: float,
    ) -> None:
        self.market_fee_pct = market_fee_pct
        self.exit_fee_pct = exit_fee_pct
        pass

    def decrease_position(
        self,
        average_entry: float,
        bar_index: int,
        dos_index: int,
        equity: float,
        exit_price: float,
        ind_set_index: int,
        order_status: int,
        position_size_asset: float,
        timestamp: int,
    ):
        pnl = position_size_asset * (exit_price - average_entry)  # math checked
        fee_open = position_size_asset * average_entry * self.market_fee_pct  # math checked
        fee_close = position_size_asset * exit_price * self.exit_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        realized_pnl = round(pnl - fees_paid, 4)  # math checked

        # Setting new equity
        equity = round(realized_pnl + equity, 4)
        logger.debug(f"\nrealized_pnl= {realized_pnl} \nequity= {equity} \nfees_paid= {fees_paid}")

        account_state = AccountState(
            # where we are at
            ind_set_index=ind_set_index,
            dos_index=dos_index,
            bar_index=bar_index,
            timestamp=timestamp,
            # account info
            available_balance=equity,
            cash_borrowed=0.0,
            cash_used=0.0,
            equity=equity,
            fees_paid=fees_paid,
            possible_loss=0.0,
            realized_pnl=realized_pnl,
            total_trades=0,
        )
        order_result = OrderResult(
            average_entry=0.0,
            can_move_sl_to_be=False,
            entry_price=0.0,
            entry_size_asset=0.0,
            entry_size_usd=0.0,
            exit_price=exit_price,
            leverage=0.0,
            liq_price=0.0,
            order_status=order_status,
            position_size_asset=0.0,
            position_size_usd=0.0,
            sl_pct=0.0,
            sl_price=0.0,
            tp_pct=0.0,
            tp_price=0.0,
        )

        return (
            account_state,
            order_result,
        )
