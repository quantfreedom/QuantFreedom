import logging
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
from quantfreedom.order_handler.increase_position import long_min_amount, long_rpa_slbcb
from quantfreedom.order_handler.leverage import long_check_liq_hit, long_dynamic_lev, long_static_lev
from quantfreedom.order_handler.stop_loss import (
    long_c_sl_hit,
    long_cm_sl_to_be,
    long_cm_sl_to_be_pass,
    long_cm_tsl,
    long_cm_tsl_pass,
    long_sl_bcb,
    move_stop_loss,
    move_stop_loss_pass,
)
from quantfreedom.order_handler.take_profit import long_c_tp_hit_regular, long_tp_rr

logger = logging.getLogger("info")


class OrderHandler:
    equity: float = 0
    order_position_size_asset: float = 0
    order_average_entry: float = 0

    def __init__(
        self,
        static_os: StaticOrderSettings,
        exchange_settings: ExchangeSettings,
    ) -> None:
        """
        #########################################
        #########################################
        #########################################
                    Exchange Settings
                    Exchange Settings
                    Exchange Settings
        #########################################
        #########################################
        #########################################
        """
        self.market_fee_pct = exchange_settings.market_fee_pct
        self.leverage_tick_step = exchange_settings.leverage_tick_step
        self.price_tick_step = exchange_settings.price_tick_step
        self.asset_tick_step = exchange_settings.asset_tick_step
        self.min_asset_size = exchange_settings.min_asset_size
        self.max_asset_size = exchange_settings.max_asset_size
        self.max_leverage = exchange_settings.max_leverage
        self.min_leverage = exchange_settings.min_leverage
        self.mmr_pct = exchange_settings.mmr_pct

        """
        #########################################
        #########################################
        #########################################
                        Trading
                        Trading
                        Trading
        #########################################
        #########################################
        #########################################
        """
        if static_os.long_or_short == LongOrShortType.Long:
            # Decrease Position
            self.dec_pos_calculator = decrease_position

            """
            #########################################
            #########################################
            #########################################
                            Stop Loss
                            Stop Loss
                            Stop Loss
            #########################################
            #########################################
            #########################################
            """

            # stop loss calulator
            if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
                self.sl_calculator = long_sl_bcb
                self.checker_sl_hit = long_c_sl_hit
                if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
                    self.sl_bcb_price_getter = min_price_getter
                elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
                    self.sl_bcb_price_getter = max_price_getter

            # SL break even
            if static_os.sl_to_be_bool:
                self.checker_sl_to_be = long_cm_sl_to_be
                # setting up stop loss be zero or entry
                if static_os.z_or_e_type == ZeroOrEntryType.ZeroLoss:
                    self.zero_or_entry_calc = long_sl_to_zero
                elif static_os.z_or_e_type == ZeroOrEntryType.AverageEntry:
                    self.zero_or_entry_calc = sl_to_entry
            else:
                self.checker_sl_to_be = long_cm_sl_to_be_pass
                self.zero_or_entry_calc = sl_to_z_e_pass

            # Trailing stop loss
            if static_os.trail_sl_bool:
                self.checker_tsl = long_cm_tsl
            else:
                self.checker_tsl = long_cm_tsl_pass

            if static_os.trail_sl_bool or static_os.sl_to_be_bool:
                self.sl_mover = move_stop_loss
            else:
                self.sl_mover = move_stop_loss_pass

            """
            #########################################
            #########################################
            #########################################
                        Increase position
                        Increase position
                        Increase position
            #########################################
            #########################################
            #########################################
            """

            if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
                if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                    self.inc_pos_calculator = long_rpa_slbcb

                elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                    self.inc_pos_calculator = long_min_amount

            """
            #########################################
            #########################################
            #########################################
                            Leverage
                            Leverage
                            Leverage
            #########################################
            #########################################
            #########################################
            """

            if static_os.leverage_strategy_type == LeverageStrategyType.Dynamic:
                self.lev_calculator = long_dynamic_lev
            else:
                self.lev_calculator = long_static_lev

            self.checker_liq_hit = long_check_liq_hit
            """
            #########################################
            #########################################
            #########################################
                            Take Profit
                            Take Profit
                            Take Profit
            #########################################
            #########################################
            #########################################
            """

            if static_os.tp_strategy_type == TakeProfitStrategyType.RiskReward:
                self.tp_calculator = long_tp_rr
                self.checker_tp_hit = long_c_tp_hit_regular
            elif static_os.tp_strategy_type == TakeProfitStrategyType.Provided:
                pass
            """
            #########################################
            #########################################
            #########################################
                        Other Settings
                        Other Settings
                        Other Settings
            #########################################
            #########################################
            #########################################
            """

            if static_os.tp_fee_type == TakeProfitFeeType.Market:
                self.exit_fee_pct = exchange_settings.market_fee_pct
            else:
                self.exit_fee_pct = exchange_settings.limit_fee_pct
            """
            #########################################
            #########################################
            #########################################
                        End User Setup
                        End User Setup
                        End User Setup
            #########################################
            #########################################
            #########################################
            """

    def set_dynamic_order_settings(
        self,
        dynamic_order_settings: DynamicOrderSettings,
    ):
        self.entry_size_asset = dynamic_order_settings.entry_size_asset
        self.max_equity_risk_pct = dynamic_order_settings.max_equity_risk_pct
        self.max_trades = dynamic_order_settings.max_trades
        self.num_candles = dynamic_order_settings.num_candles
        self.risk_account_pct_size = dynamic_order_settings.risk_account_pct_size
        self.risk_reward = dynamic_order_settings.risk_reward
        self.sl_based_on_add_pct = dynamic_order_settings.sl_based_on_add_pct
        self.sl_based_on_lookback = dynamic_order_settings.sl_based_on_lookback
        self.sl_bcb_type = dynamic_order_settings.sl_bcb_type
        self.sl_to_be_cb_type = dynamic_order_settings.sl_to_be_cb_type
        self.sl_to_be_when_pct = dynamic_order_settings.sl_to_be_when_pct
        self.sl_to_be_ze_type = dynamic_order_settings.sl_to_be_ze_type
        self.static_leverage = dynamic_order_settings.static_leverage
        self.trail_sl_bcb_type = dynamic_order_settings.trail_sl_bcb_type
        self.trail_sl_by_pct = dynamic_order_settings.trail_sl_by_pct
        self.trail_sl_when_pct = dynamic_order_settings.trail_sl_when_pct

    def calc_stop_loss(
        self,
        bar_index: int,
        candles: np.array,
    ) -> float:
        return self.sl_calculator(
            bar_index=bar_index,
            candles=candles,
            price_tick_step=self.price_tick_step,
            sl_based_on_add_pct=self.sl_based_on_add_pct,
            sl_based_on_lookback=self.sl_based_on_lookback,
            sl_bcb_price_getter=self.sl_bcb_price_getter,
            sl_bcb_type=self.sl_bcb_type,
        )

    def calc_decrease_position(
        self,
        bar_index,
        dos_index,
        exit_price,
        ind_set_index,
        order_status,
        timestamp,
    ):
        self.dec_pos_calculator(
            average_entry=self.order_average_entry,
            bar_index=bar_index,
            dos_index=dos_index,
            equity=self.equity,
            exit_fee_pct=self.exit_fee_pct,
            exit_price=exit_price,
            ind_set_index=ind_set_index,
            market_fee_pct=self.market_fee_pct,
            order_status=order_status,
            position_size_asset=self.order_position_size_asset,
            timestamp=timestamp,
        )
