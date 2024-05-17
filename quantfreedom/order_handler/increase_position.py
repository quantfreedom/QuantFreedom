from logging import getLogger
from quantfreedom.core.enums import (
    IncreasePositionType,
    RejectedOrder,
    StopLossStrategyType,
)
from quantfreedom.helpers.helper_funcs import round_size_by_tick_step

logger = getLogger()


class IncreasePosition:
    account_pct_risk_per_trade: float
    max_equity_risk_pct: float
    max_trades: int

    def __init__(
        self,
        asset_tick_step: float,
        increase_position_type: IncreasePositionType,  # type: ignore
        long_short: str,
        market_fee_pct: float,
        max_asset_size: float,
        min_asset_size: float,
        price_tick_step: float,
        sl_strategy_type: StopLossStrategyType,  # type: ignore
    ) -> None:
        """
        Summary
        -------
        Creates and sets the increase position class settings

        Parameters
        ----------
        asset_tick_step : float
            asset_tick_step
        increase_position_type : IncreasePositionType
            How you want to process increasing your position
        long_short : str
            long or short
        market_fee_pct : float
            market_fee_pct
        max_asset_size : float
            max_asset_size
        min_asset_size : float
            min_asset_size
        price_tick_step : float
            price_tick_step
        sl_strategy_type : StopLossStrategyType
            how you want to process creating your stop loss
        """
        self.min_asset_size = min_asset_size
        self.asset_tick_step = asset_tick_step
        self.price_tick_step = price_tick_step
        self.max_asset_size = max_asset_size
        self.market_fee_pct = market_fee_pct

        if long_short == "long":
            self.entry_calc_p = self.long_entry_size_p
            self.entry_calc_np = self.long_entry_size_np
        elif long_short.lower() == "short":
            self.entry_calc_p = self.short_entry_size_p
            self.entry_calc_np = self.short_entry_size_np
        else:
            raise Exception("long or short are the only options for long_short")

        if sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
            if increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                self.inc_pos_calculator = self.rpa_slbcb
            elif increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                self.inc_pos_calculator = self.min_asset_amount

    def c_too_b_s(
        self,
        entry_size_asset: float,
    ) -> None:
        """
        Summary
        -------
        Check if the asset size is too big or too small

        Parameters
        ----------
        entry_size_asset : float
            entry size of the asset

        """
        if entry_size_asset < self.min_asset_size:
            msg = f"entry size too small entry_size_asset= {entry_size_asset} < self.min_asset_size= {self.min_asset_size}"
            logger.warning(msg)
            RejectedOrder.msg = msg
            raise RejectedOrder
        elif entry_size_asset > self.max_asset_size:
            msg = (
                f"entry size too big entry_size_asset= {entry_size_asset} > self.max_asset_size= {self.max_asset_size}"
            )
            logger.warning(msg)
            RejectedOrder.msg = msg
            raise RejectedOrder

        logger.debug(f"Entry size is fine entry_size_asset= {entry_size_asset}")

    def c_pl_ra_ps(
        self,
        equity: float,
        total_trades: int,
    ) -> tuple[int, int]:
        """
        Summary
        -------
        Creates possible loss then checks if it is bigger than risk account percent size then returns the new possible loss and total trades

        Parameters
        ----------
        equity : float
            equity
        total_possible_loss : float
            total_possible_loss
        total_trades : int
            total_trades

        Returns
        -------
        int, int
            total_possible_loss, total_trades
        """
        total_trades += 1

        if total_trades > self.max_trades:
            msg = f"Max trades reached - total trades= {total_trades} max trades= {self.max_trades}"
            logger.warning(msg)
            RejectedOrder.msg = msg
            raise RejectedOrder

        possible_loss = -int(equity * self.account_pct_risk_per_trade)

        total_possible_loss = int(total_trades * possible_loss)

        logger.debug(
            f"""
total trades= {total_trades}
max trades= {self.max_trades}
possible_loss= {possible_loss}
total_possible_loss= {total_possible_loss}"""
        )
        return total_possible_loss, total_trades

    def c_total_trades(
        self,
        average_entry: float,
        position_size_asset: float,
        sl_price: float,
        total_trades: int,
    ) -> tuple[int, int]:
        """
        Summary
        -------
        Creates possible loss then adds 1 to total trades then checks if total trades is bigger than max trades

        Parameters
        ----------
        average_entry : float
            average_entry
        total_possible_loss : float
            total_possible_loss
        position_size_asset : float
            position_size_asset
        sl_price : float
            sl_price
        total_trades : int
            total_trades

        Returns
        -------
        tuple[int, int]
            total_possible_loss, total_trades
        """
        total_trades += 1

        if total_trades > self.max_trades:

            msg = f"""
Max trades reached
Total trades= {total_trades}
max trades= {self.max_trades}
possible_loss= {possible_loss}
total_possible_loss= {total_possible_loss}"""
            logger.warning(msg)
            RejectedOrder.msg = msg
            raise RejectedOrder

        pnl = -abs(average_entry - sl_price) * position_size_asset  # math checked
        fee_open = position_size_asset * average_entry * self.market_fee_pct  # math checked
        fee_close = position_size_asset * sl_price * self.market_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        possible_loss = -int(pnl - fees_paid)
        total_possible_loss = int(total_trades * possible_loss)

        logger.debug(
            f"""
Total trades= {total_trades}
max trades= {self.max_trades}
possible_loss= {possible_loss}
total_possible_loss= {total_possible_loss}"""
        )
        return total_possible_loss, total_trades

    def min_asset_amount(
        self,
        average_entry: float,
        entry_price: float,
        equity: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
        total_trades: int,
    ) -> tuple[float, float, float, float, float, float, int, int, float]:
        """
        Summary
        -------
        Check if we are in a position or not and sending you to the correct function to handle that

        Parameters
        ----------
        average_entry : float
            average_entry
        entry_price : float
            entry_price
        equity : float
            equity
        position_size_asset : float
            position_size_asset
        position_size_usd : float
            position_size_usd
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price
        total_trades : int
            total_trades

        Returns
        -------
        float, float, float, float, float, float, int, int, float
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct
        """
        if position_size_asset > 0:
            logger.debug("We are in a position")
            return self.min_amount_p(
                average_entry=average_entry,
                entry_price=entry_price,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
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
        sl_price: float,
        total_trades: int,
    ) -> tuple[float, float, float, float, float, float, int, int, float]:
        """
        Summary
        -------
        Setting the entry size to the minimum amount plus what ever position size we are already in

        Parameters
        ----------
        average_entry : float
            average_entry
        entry_price : float
            entry_price
        position_size_asset : float
            position_size_asset
        position_size_usd : float
            position_size_usd
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price
        total_trades : int
            total_trades

        Returns
        -------
        tuple[float, float, float, float, float, float, int, int, float]
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct
        """
        position_size_asset += self.min_asset_size
        entry_size_asset = self.min_asset_size
        logger.debug(f"entry_size_asset= {entry_size_asset} position_size_asset{position_size_asset}")

        entry_size_usd = round(self.min_asset_size * entry_price, 2)
        logger.debug(f"entry_size_usd = {entry_size_usd}")

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=self.price_tick_step,
        )
        logger.debug(f"average_entry {average_entry}")

        sl_pct = round(abs(average_entry - sl_price) / average_entry, 2)
        logger.debug(f"sl_pct= {round(sl_pct*100, 2)}")

        position_size_usd = round(entry_size_usd + position_size_usd, 2)
        logger.debug(f"position_size_usd= {position_size_usd}")

        total_possible_loss, total_trades = self.c_total_trades(
            average_entry=average_entry,
            total_possible_loss=total_possible_loss,
            total_trades=total_trades,
            position_size_asset=position_size_asset,
            sl_price=sl_price,
        )
        logger.debug(f"total_possible_loss= {total_possible_loss} total_trades= {total_trades}")

        self.c_too_b_s(entry_size_asset=entry_size_asset)
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct,
        )

    def min_amount_np(
        self,
        entry_price: float,
        sl_price: float,
    ) -> tuple[float, float, float, float, float, float, int, int, float]:
        """
        Summary
        -------
        Setting the entry size to the minimum amount

        Parameters
        ----------
        entry_price : float
            entry_price
        sl_price : float
            sl_price

        Returns
        -------
        tuple[float, float, float, float, float, float, int, int, float]
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct
        """
        entry_size_asset = position_size_asset = self.min_asset_size
        logger.debug(f"entry_size_asset={entry_size_asset} position_size_asset= {position_size_asset}")

        entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 2)
        logger.debug(f"entry_size_usd= {entry_size_usd} position_size_usd= {position_size_usd}")

        average_entry = entry_price
        logger.debug(f"average_entry {average_entry}")
        sl_pct = round(abs(average_entry - sl_price) / average_entry, 2)
        logger.debug(f"sl_pct= {round(sl_pct*100, 2)}")

        total_possible_loss, total_trades = self.c_total_trades(
            average_entry=average_entry,
            position_size_asset=position_size_asset,
            total_possible_loss=0,
            sl_price=sl_price,
            total_trades=0,
        )
        logger.debug(f"total_possible_loss= {total_possible_loss} total_trades {total_trades}")

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
            total_possible_loss,
            total_trades,
            sl_pct,
        )

    def long_entry_size_p(
        self,
        average_entry: float,
        entry_price: float,
        position_size_usd: float,
        sl_price: float,
        total_possible_loss: float,
    ) -> float:
        """
        Summary
        -------
        Formula to calulcate the long entry size when we are in a position and have our stop loss type set to stop loss based on candle body

        how to calculate pnl https://www.bybithelp.com/en-US/s/article/Profit-Loss-calculations-USDT-Contract

        math for the formula https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(n%20-%20%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Cright)%5Cright)-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%20n%5Ccdot%20m%5Cright)%20%5Cright)%3D-f?or=input

        Parameters
        ----------
        average_entry : float
            average_entry
        entry_price : float
            entry_price
        position_size_usd : float
            position_size_usd
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price

        Returns
        -------
        float
            entry_size_usd
        """

        entry_size = round(
            -(
                (
                    entry_price * average_entry * total_possible_loss
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
        return entry_size

    def long_entry_size_np(
        self,
        entry_price: float,
        sl_price: float,
        total_possible_loss: float,
    ) -> float:
        """
        Summary
        -------
        Formula to calulcate the long entry size when we are not in a position and have our stop loss type set to stop loss based on candle body

        how to calculate pnl https://www.bybithelp.com/en-US/s/article/Profit-Loss-calculations-USDT-Contract

        math for the formula https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%5Cleft(x%20-%20e%5Cright)%5Cright)-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20e%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20x%5Ccdot%20m%5Cright)%20%5Cright)%3Dp?or=input

        Parameters
        ----------
        entry_price : float
            entry_price
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price

        Returns
        -------
        float
            entry_size_usd
        """
        price_mult_loss = entry_price * -total_possible_loss
        div_by = -sl_price + entry_price + entry_price * self.market_fee_pct + self.market_fee_pct * sl_price
        entry_size_usd = round(price_mult_loss / div_by, 2)
        return entry_size_usd

    def short_entry_size_p(
        self,
        average_entry: float,
        entry_price: float,
        position_size_usd: float,
        sl_price: float,
        total_possible_loss: float,
    ) -> float:
        """
        Summary
        -------
        Formula to calulcate the short entry size when we are in a position and have our stop loss type set to stop loss based on candle body

        how to calculate pnl https://www.bybithelp.com/en-US/s/article/Profit-Loss-calculations-USDT-Contract

        math for the formula https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)-n%5Cright)%5Cright)-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Ccdot%20%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%20%20n%5Ccdot%20%20m%5Cright)%20%5Cright)%3D-f?or=input

        Parameters
        ----------
        average_entry : float
            average_entry
        entry_price : float
            entry_price
        position_size_usd : float
            position_size_usd
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price

        Returns
        -------
        float
            entry_size_usd
        """
        entry_size_usd = round(
            -(
                (
                    entry_price * average_entry * total_possible_loss
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
        return entry_size_usd

    def short_entry_size_np(
        self,
        sl_price: float,
        entry_price: float,
        total_possible_loss: float,
    ) -> float:
        """
        Summary
        -------
        Formula to calulcate the short entry size when we are not in a position and have our stop loss type set to stop loss based on candle body

        how to calculate pnl https://www.bybithelp.com/en-US/s/article/Profit-Loss-calculations-USDT-Contract

        math for the formula https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%5Cleft(e%20-%20x%5Cright)%5Cright)-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20e%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20x%5Ccdot%20m%5Cright)%20%5Cright)%3Dp?or=input

        Parameters
        ----------
        entry_price : float
            entry_price
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price

        Returns
        -------
        float
            entry_size_usd
        """
        price_mult_loss = entry_price * -total_possible_loss
        div_by = -entry_price + sl_price + entry_price * self.market_fee_pct + self.market_fee_pct * sl_price
        entry_size_usd = round(price_mult_loss / div_by, 2)
        return entry_size_usd

    def rpa_slbcb(
        self,
        equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
        total_trades: int,
    ) -> tuple[float, float, float, float, float, float, int, int, float]:
        """
        Summary
        -------
        Check if we are in a position or not and sending you to the correct function to handle that

        Parameters
        ----------
        average_entry : float
            average_entry
        entry_price : float
            entry_price
        equity : float
            equity
        position_size_asset : float
            position_size_asset
        position_size_usd : float
            position_size_usd
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price
        total_trades : int
            total_trades

        Returns
        -------
        float, float, float, float, float, float, int, int, float
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct
        """
        if position_size_asset > 0:
            logger.debug("We are in a position")
            return self.rpa_slbcb_p(
                equity=equity,
                average_entry=average_entry,
                entry_price=entry_price,
                position_size_asset=position_size_asset,
                position_size_usd=position_size_usd,
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
        average_entry: float,
        entry_price: float,
        equity: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
        total_trades: int,
    ) -> tuple[float, float, float, float, float, float, int, int, float]:
        """
        Summary
        -------
        In a position - Risking a percent of your account while also having your stop loss type set to stop loss based on candle body

        Parameters
        ----------
        average_entry : float
            average_entry
        entry_price : float
            entry_price
        equity : float
            equity
        position_size_asset : float
            position_size_asset
        position_size_usd : float
            position_size_usd
        total_possible_loss : float
            total_possible_loss
        sl_price : float
            sl_price
        total_trades : int
            total_trades

        Returns
        -------
        float, float, float, float, float, float, int, int, float
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct
        """
        total_possible_loss, total_trades = self.c_pl_ra_ps(
            equity=equity,
            total_trades=total_trades,
        )

        entry_size_usd = self.entry_calc_p(
            total_possible_loss=total_possible_loss,
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

        position_size_usd = round(entry_size_usd + position_size_usd, 2)
        logger.debug(f"position_size_usd= {position_size_usd}")

        average_entry = (entry_size_usd + position_size_usd) / (
            (entry_size_usd / entry_price) + (position_size_usd / average_entry)
        )
        average_entry = round_size_by_tick_step(
            user_num=average_entry,
            exchange_num=self.price_tick_step,
        )
        logger.debug(f"average_entry= {average_entry}")

        sl_pct = round(abs(average_entry - sl_price) / average_entry, 2)
        logger.debug(f"sl_pct= {round(sl_pct * 100, 2)}")
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct,
        )

    def rpa_slbcb_np(
        self,
        equity: float,
        entry_price: float,
        sl_price: float,
    ) -> tuple[float, float, float, float, float, float, int, int, float]:
        """
        Summary
        -------
        Not in a position - Risking a percent of your account while also having your stop loss type set to stop loss based on candle body

        Parameters
        ----------
        equity : float
            equity
        entry_price : float
            entry_price
        sl_price : float
            sl_price

        Returns
        -------
        tuple[float, float, float, float, float, float, int, int, float]
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct
        """
        total_possible_loss, total_trades = self.c_pl_ra_ps(
            equity=equity,
            total_trades=0,
        )

        entry_size_usd = position_size_usd = self.entry_calc_np(
            sl_price=sl_price,
            entry_price=entry_price,
            total_possible_loss=total_possible_loss,
        )
        logger.debug(f"entry_size_usd= {entry_size_usd}")
        entry_size_asset = position_size_asset = round_size_by_tick_step(
            user_num=entry_size_usd / entry_price,
            exchange_num=self.asset_tick_step,
        )
        self.c_too_b_s(entry_size_asset=entry_size_asset)

        average_entry = entry_price

        sl_pct = round(abs(average_entry - sl_price) / average_entry, 2)
        logger.debug(f"sl_pct= {round(sl_pct * 100, 2)}")
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct,
        )
