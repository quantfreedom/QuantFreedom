from logging import getLogger
import numpy as np
from quantfreedom.enums import (
    DynamicOrderSettings,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    PriceGetterType,
    StaticOrderSettings,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    ZeroOrEntryType,
)
from quantfreedom.helper_funcs import long_sl_to_zero, max_price_getter, min_price_getter, sl_to_entry, sl_to_z_e_pass
from quantfreedom.order_handler.decrease_position import decrease_position
from quantfreedom.order_handler.increase_position import LongIncreasePosition, long_min_amount, long_rpa_slbcb
from quantfreedom.order_handler.leverage import LongLeverage, long_check_liq_hit, long_dynamic_lev, long_static_lev
from quantfreedom.order_handler.stop_loss import (
    LongStopLoss,
    long_c_sl_hit,
    long_cm_sl_to_be,
    long_cm_sl_to_be_pass,
    long_cm_tsl,
    long_cm_tsl_pass,
    long_sl_bcb,
    move_stop_loss,
    move_stop_loss_pass,
)
from quantfreedom.order_handler.take_profit import LongTakeProfit, long_c_tp_hit_regular, long_tp_rr

logger = getLogger("info")


class OrderHandler:
    equity: float = 0
    order_position_size_asset: float = 0
    order_average_entry: float = 0

    def __init__(
        self,
        static_os: StaticOrderSettings,
        exchange_settings: ExchangeSettings,
    ) -> None:
        if static_os.long_or_short == LongOrShortType.Long:
            # Decrease Position
            self.dec_pos_calculator = decrease_position

            self.obj_stop_loss = LongStopLoss(
                market_fee_pct=exchange_settings.market_fee_pct,
                pg_min_max_sl_bcb=static_os.pg_min_max_sl_bcb,
                price_tick_step=exchange_settings.price_tick_step,
                sl_strategy_type=static_os.sl_strategy_type,
                sl_to_be_bool=static_os.sl_to_be_bool,
                trail_sl_bool=static_os.trail_sl_bool,
                z_or_e_type=static_os.z_or_e_type,
            )
            self.obj_inc_pos = LongIncreasePosition(
                asset_tick_step=exchange_settings.asset_tick_step,
                increase_position_type=static_os.increase_position_type,
                market_fee_pct=exchange_settings.market_fee_pct,
                max_asset_size=exchange_settings.max_asset_size,
                min_asset_size=exchange_settings.min_asset_size,
                price_tick_step=exchange_settings.price_tick_step,
                sl_strategy_type=static_os.sl_strategy_type,
            )
            self.obj_leverage = LongLeverage(
                leverage_strategy_type=static_os.leverage_strategy_type,
                leverage_tick_step=exchange_settings.leverage_tick_step,
                market_fee_pct=exchange_settings.market_fee_pct,
                max_leverage=exchange_settings.max_leverage,
                min_leverage=exchange_settings.min_leverage,
                mmr_pct=exchange_settings.mmr_pct,
                price_tick_step=exchange_settings.price_tick_step,
            )

            if static_os.tp_fee_type == TakeProfitFeeType.Market:
                exit_fee_pct = exchange_settings.market_fee_pct
            else:
                exit_fee_pct = exchange_settings.limit_fee_pct

            self.obj_take_profit = LongTakeProfit(
                market_fee_pct=exchange_settings.market_fee_pct,
                price_tick_step=exchange_settings.price_tick_step,
                tp_fee_pct=exit_fee_pct,
                tp_strategy_type=static_os.tp_strategy_type,
            )

    def update_class_dos(
        self,
        dynamic_order_settings: DynamicOrderSettings,
    ):
        # take profit
        self.obj_take_profit.risk_reward = dynamic_order_settings.risk_reward

        # leverage
        self.obj_leverage.static_leverage = dynamic_order_settings.static_leverage

        # increase position
        self.obj_inc_pos.max_trades = dynamic_order_settings.max_trades
        self.obj_inc_pos.risk_account_pct_size = dynamic_order_settings.risk_account_pct_size
        self.obj_inc_pos.max_equity_risk_pct = dynamic_order_settings.max_equity_risk_pct

        # stop loss updates
        self.obj_stop_loss.sl_based_on_add_pct = dynamic_order_settings.sl_based_on_add_pct
        self.obj_stop_loss.sl_based_on_lookback = dynamic_order_settings.sl_based_on_lookback
        self.obj_stop_loss.sl_bcb_type = dynamic_order_settings.sl_bcb_type
        self.obj_stop_loss.sl_to_be_cb_type = dynamic_order_settings.sl_to_be_cb_type
        self.obj_stop_loss.sl_to_be_when_pct = dynamic_order_settings.sl_to_be_when_pct
        self.obj_stop_loss.trail_sl_bcb_type = dynamic_order_settings.trail_sl_bcb_type
        self.obj_stop_loss.trail_sl_by_pct = dynamic_order_settings.trail_sl_by_pct
        self.obj_stop_loss.trail_sl_when_pct = dynamic_order_settings.trail_sl_when_pct

    def calc_stop_loss(
        self,
        bar_index: int,
        candles: np.array,
    ):
        sl_price = self.obj_stop_loss.sl_calculator(
            bar_index=bar_index,
            candles=candles,
        )
        logger.info(f"sl price= {sl_price}")
        return sl_price

    def calculate_increase_posotion(
        self,
        account_state_equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        sl_price: float,
        total_trades: int,
    ):
        (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        ) = self.obj_inc_pos.inc_pos_calculator(
            account_state_equity=account_state_equity,
            average_entry=average_entry,
            entry_price=entry_price,
            in_position=position_size_asset > 0,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
            possible_loss=possible_loss,
            sl_price=sl_price,
            total_trades=total_trades,
        )
        logger.info(
            f"\n\
average_entry={average_entry:,}\n\
entry_price={entry_price:,}\n\
entry_size_asset={entry_size_asset:,}\n\
entry_size_usd={entry_size_usd:,}\n\
position_size_asset={position_size_asset:,}\n\
position_size_usd={position_size_usd:,}\n\
possible_loss={possible_loss:,}\n\
total_trades={total_trades:,}\n\
sl_pct={round(sl_pct*100,2):,}"
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        )

    def calculate_leverage(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
        sl_price: float,
    ):
        (
            available_balance,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        ) = self.obj_leverage.lev_calculator(
            available_balance=available_balance,
            average_entry=average_entry,
            cash_borrowed=cash_borrowed,
            cash_used=cash_used,
            entry_size_usd=entry_size_usd,
            sl_price=sl_price,
        )
        logger.info(
            f"\n\
available_balance={available_balance:,}\n\
cash_borrowed={cash_borrowed:,}\n\
cash_used={cash_used:,}\n\
leverage={leverage:,}\n\
liq_price={liq_price:,}"
        )
        return (
            available_balance,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )

    def calc_take_profit(
        self,
        average_entry: float,
        position_size_usd: float,
        possible_loss: float,
    ):
        (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        ) = self.obj_take_profit.tp_calculator(
            average_entry=average_entry,
            position_size_usd=position_size_usd,
            possible_loss=possible_loss,
        )
        logger.info(f"tp_price= {tp_price} tp_pct= {round(tp_pct * 100, 3)}")
        return (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        )