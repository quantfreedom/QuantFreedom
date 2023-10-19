from numba.experimental import jitclass

from nb_quantfreedom.nb_enums import OrderResult, OrderStatus


class nb_DecreasePosition:
    def __init__(self) -> None:
        pass

    def decrease_position(
        self,
        average_entry: float,
        bar_index: int,
        dos_index: int,
        equity: float,
        exit_fee_pct: float,
        exit_price: float,
        indicator_settings_index: int,
        market_fee_pct: float,
        order_status: int,
        position_size_asset: float,
        timestamp: int,
    ):
        pass


@jitclass()
class nb_Long_DP(nb_DecreasePosition):
    def decrease_position(
        self,
        average_entry: float,
        bar_index: int,
        dos_index: int,
        equity: float,
        exit_fee_pct: float,
        exit_price: float,
        indicator_settings_index: int,
        market_fee_pct: float,
        order_status: int,
        position_size_asset: float,
        timestamp: int,
    ):
        pnl = position_size_asset * (exit_price - average_entry)  # math checked
        fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
        fee_close = position_size_asset * exit_price * exit_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        realized_pnl = round(pnl - fees_paid, 4)  # math checked

        # Setting new equity
        equity = round(realized_pnl + equity, 4)
        print(
            f"\n\
realized_pnl={realized_pnl}\n\
order_status= {OrderStatus._fields[order_status]}\n\
available_balance={equity}\n\
equity={equity}"
        )
        return OrderResult(  # where we are at
            # where we are at
            indicator_settings_index=indicator_settings_index,
            dos_index=dos_index,
            bar_index=bar_index,
            timestamp=timestamp,
            # account info
            equity=equity,
            available_balance=equity,
            cash_borrowed=0.0,
            cash_used=0.0,
            # order info
            average_entry=0.0,
            can_move_sl_to_be=True,
            fees_paid=fees_paid,
            leverage=0.0,
            liq_price=0.0,
            order_status=order_status,
            possible_loss=0.0,
            entry_size_asset=0.0,
            entry_size_usd=0.0,
            entry_price=0.0,
            exit_price=exit_price,
            position_size_asset=0.0,
            position_size_usd=0.0,
            realized_pnl=realized_pnl,
            sl_pct=0.0,
            sl_price=0.0,
            total_trades=0,
            tp_pct=0.0,
            tp_price=0.0,
        )
