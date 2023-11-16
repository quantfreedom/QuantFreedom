from logging import getLogger
from quantfreedom.enums import (
    IncreasePositionType,
    RejectedOrder,
    StopLossStrategyType,
)
from quantfreedom.helper_funcs import round_size_by_tick_step

logger = getLogger("info")


class IncreasePosition:
    risk_account_pct_size: float
    max_equity_risk_pct: float
    max_trades: int

    def __init__(
        self,
        asset_tick_step: float,
        increase_position_type: IncreasePositionType,
        long_short: str,
        market_fee_pct: float,
        max_asset_size: float,
        min_asset_size: float,
        price_tick_step: float,
        sl_strategy_type: StopLossStrategyType,
    ) -> None:
        self.min_asset_size = min_asset_size
        self.asset_tick_step = asset_tick_step
        self.price_tick_step = price_tick_step
        self.max_asset_size = max_asset_size
        self.market_fee_pct = market_fee_pct

        if long_short == "long":
            self.entry_calc_p = self.long_entry_size_p
            self.entry_calc_np = self.long_entry_size_np
        else:
            self.entry_calc_p = self.short_entry_size_p
            self.entry_calc_np = self.short_entry_size_np

        if sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
            if increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                self.inc_pos_calculator = self.rpa_slbcb
            elif increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                self.inc_pos_calculator = self.min_amount_pc

    def c_too_b_s(
        self,
        entry_size_asset: float,
    ):
        """
        Check if the asset size is too big or too small
        """
        if entry_size_asset < self.min_asset_size:
            logger.warning(
                f"entry size too small entry_size_asset= {entry_size_asset} < self.min_asset_size= {self.min_asset_size}"
            )
            raise RejectedOrder
        elif entry_size_asset > self.max_asset_size:
            logger.warning(
                f"entry size too big entry_size_asset= {entry_size_asset} > self.max_asset_size= {self.max_asset_size}"
            )
            raise RejectedOrder

        logger.debug(f"Entry size is fine entry_size_asset= {entry_size_asset}")

    def c_pl_ra_ps(
        self,
        equity: float,
        possible_loss: float,
        total_trades: int,
    ):
        """
        Check if Possible loss is bigger than risk account percent size
        """
        possible_loss = int(possible_loss - equity * self.risk_account_pct_size)
        logger.debug(f"possible_loss= {possible_loss}")

        max_equity_risk = -int(equity * self.max_equity_risk_pct)
        logger.debug(f"max_equity_risk= {max_equity_risk}")
        if possible_loss < max_equity_risk:
            logger.warning(f"PL too big possible_loss= {possible_loss} max risk= {max_equity_risk}")
            raise RejectedOrder

        total_trades += 1

        logger.debug(
            f"PL is fine possible_loss= {possible_loss} max risk= {max_equity_risk} total trades= {total_trades}"
        )
        return possible_loss, total_trades

    def c_total_trades(
        self,
        average_entry: float,
        possible_loss: float,
        position_size_asset: float,
        sl_price: float,
        total_trades: int,
    ):
        """
        Checking the total trades is bigger than max trades
        """
        pnl = -abs(average_entry - sl_price) * position_size_asset  # math checked
        fee_open = position_size_asset * average_entry * self.market_fee_pct  # math checked
        fee_close = position_size_asset * sl_price * self.market_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        possible_loss = int(pnl - fees_paid)

        logger.debug(f"possible_loss= {possible_loss}")

        total_trades += 1
        if total_trades > self.max_trades:
            logger.warning(
                f"Max trades reached total trades= {total_trades} max trades= {self.max_trades} possible_loss= {possible_loss}"
            )
            raise RejectedOrder
        logger.debug(
            f"Max trades reached - total trades= {total_trades} max trades= {self.max_trades} possible_loss= {possible_loss}"
        )
        return possible_loss, total_trades

    def min_amount_pc(
        self,
        equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        sl_price: float,
        total_trades: int,
    ):
        """
        Setting your position size to the min amount the exchange will allow
        """
        if position_size_asset > 0:
            logger.debug("We are in a position")
            return self.min_amount_p(
                average_entry=average_entry,
                entry_price=entry_price,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                sl_price=sl_price,
                total_trades=total_trades,
            )
        else:
            logger.debug("Not in a position")
            return self.min_amount_np(
                entry_price=entry_price,
                sl_price=sl_price,
            )

    def min_amount_p(
        self,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        sl_price: float,
        total_trades: int,
    ):
        position_size_asset += self.min_asset_size
        entry_size_asset = self.min_asset_size
        logger.debug(f"entry_size_asset= {entry_size_asset} position_size_asset{position_size_asset}")

        entry_size_usd = round(self.min_asset_size * entry_price, 3)
        logger.debug(f"entry_size_usd = {entry_size_usd}")

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=self.price_tick_step,
        )
        logger.debug(f"average_entry {average_entry}")

        sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
        logger.debug(f"sl_pct= {round(sl_pct*100, 3)}")

        position_size_usd = round(entry_size_usd + position_size_usd, 3)
        logger.debug(f"position_size_usd= {position_size_usd}")

        possible_loss, total_trades = self.c_total_trades(
            average_entry=average_entry,
            possible_loss=possible_loss,
            total_trades=total_trades,
            position_size_asset=position_size_asset,
            sl_price=sl_price,
        )
        logger.debug(f"possible_loss= {possible_loss} total_trades= {total_trades}")

        self.c_too_b_s(entry_size_asset=entry_size_asset)
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

    def min_amount_np(
        self,
        entry_price: float,
        sl_price: float,
    ):
        entry_size_asset = position_size_asset = self.min_asset_size
        logger.debug(f"entry_size_asset={entry_size_asset} position_size_asset= {position_size_asset}")

        entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 3)
        logger.debug(f"entry_size_usd= {entry_size_usd} position_size_usd= {position_size_usd}")

        average_entry = entry_price
        logger.debug(f"average_entry {average_entry}")
        sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
        logger.debug(f"sl_pct= {round(sl_pct*100, 3)}")

        possible_loss, total_trades = self.c_total_trades(
            average_entry=average_entry,
            position_size_asset=position_size_asset,
            possible_loss=0,
            sl_price=sl_price,
            total_trades=0,
        )
        logger.debug(f"possible_loss= {possible_loss} total_trades {total_trades}")

        self.c_too_b_s(
            entry_size_asset=entry_size_asset,
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

    def long_entry_size_p(
        self,
        possible_loss: float,
        sl_price: float,
        entry_price: float,
        average_entry: float,
        position_size_usd: float,
    ):
        # math https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(n%20-%20%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Cright)%5Cright)-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%20n%5Ccdot%20m%5Cright)%20%5Cright)%3D-f?or=input

        return round(
            -(
                (
                    entry_price * average_entry * possible_loss
                    - entry_price * sl_price * position_size_usd
                    + entry_price * sl_price * self.market_fee_pct * position_size_usd
                    + entry_price * average_entry * position_size_usd
                    + entry_price * self.market_fee_pct * average_entry * position_size_usd
                )
                / (
                    average_entry
                    * (-sl_price + entry_price + sl_price * self.market_fee_pct + entry_price * self.market_fee_pct)
                )
            ),
            3,
        )

    def long_entry_size_np(
        self,
        possible_loss: float,
        sl_price: float,
        entry_price: float,
    ):
        return round(
            possible_loss
            / (sl_price / entry_price - 1 - self.market_fee_pct - sl_price * self.market_fee_pct / entry_price),
            3,
        )

    def short_entry_size_p(
        self,
        possible_loss: float,
        sl_price: float,
        entry_price: float,
        average_entry: float,
        position_size_usd: float,
    ):
        # math https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)-n%5Cright)%5Cright)-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Ccdot%20%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%20%20n%5Ccdot%20%20m%5Cright)%20%5Cright)%3D-f?or=input

        return round(
            -(
                (
                    entry_price * average_entry * possible_loss
                    - entry_price * average_entry * position_size_usd
                    + entry_price * sl_price * position_size_usd
                    + entry_price * sl_price * self.market_fee_pct * position_size_usd
                    + entry_price * self.market_fee_pct * average_entry * position_size_usd
                )
                / (
                    average_entry
                    * (sl_price - entry_price + sl_price * self.market_fee_pct + entry_price * self.market_fee_pct)
                )
            ),
            3,
        )

    def short_entry_size_np(
        self,
        possible_loss: float,
        sl_price: float,
        entry_price: float,
    ):
        return round(
            entry_price
            * possible_loss
            / (-entry_price + sl_price + entry_price * self.market_fee_pct + sl_price * self.market_fee_pct),
            3,
        )

    def rpa_slbcb(
        self,
        equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        sl_price: float,
        total_trades: int,
    ):
        """
        Risking percent of your account while also having your stop loss based open high low or close of a candle
        """
        if position_size_asset > 0:
            logger.debug("We are in a position")
            return self.rpa_slbcb_p(
                equity=equity,
                average_entry=average_entry,
                entry_price=entry_price,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
                possible_loss=possible_loss,
                sl_price=sl_price,
                total_trades=total_trades,
            )
        else:
            logger.debug("Not in a position")
            return self.rpa_slbcb_np(
                equity=equity,
                entry_price=entry_price,
                sl_price=sl_price,
            )

    def rpa_slbcb_p(
        self,
        equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
        sl_price: float,
        total_trades: int,
    ):
        possible_loss, total_trades = self.c_pl_ra_ps(
            equity=equity,
            possible_loss=possible_loss,
            total_trades=total_trades,
        )

        entry_size_usd = self.entry_calc_p(
            possible_loss=possible_loss,
            sl_price=sl_price,
            entry_price=entry_price,
            average_entry=average_entry,
            position_size_usd=position_size_usd,
        )
        logger.debug(f"entry_size_usd= {entry_size_usd}")

        entry_size_asset = round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=self.asset_tick_step,
        )
        self.c_too_b_s(entry_size_asset=entry_size_asset)

        position_size_asset = round_size_by_tick_step(
            user_num=position_size_asset + entry_size_asset,
            exchange_num=self.asset_tick_step,
        )
        logger.debug(f"position_size_asset= {position_size_asset}")

        position_size_usd = round(entry_size_usd + position_size_usd, 3)
        logger.debug(f"position_size_usd= {position_size_usd}")

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=self.price_tick_step,
        )
        logger.debug(f"average_entry= {average_entry}")

        sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
        logger.debug(f"sl_pct= {round(sl_pct * 100, 3)}")
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

    def rpa_slbcb_np(
        self,
        equity: float,
        entry_price: float,
        sl_price: float,
    ):
        possible_loss, total_trades = self.c_pl_ra_ps(
            equity=equity,
            possible_loss=0,
            total_trades=0,
        )

        entry_size_usd = position_size_usd = self.entry_calc_np(
            possible_loss=possible_loss,
            sl_price=sl_price,
            entry_price=entry_price,
        )
        logger.debug(f"entry_size_usd= {entry_size_usd}")
        entry_size_asset = position_size_asset = round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=self.asset_tick_step,
        )
        self.c_too_b_s(entry_size_asset=entry_size_asset)

        average_entry = entry_price

        sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
        logger.debug(f"sl_pct= {round(sl_pct * 100, 3)}")
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
