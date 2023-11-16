import logging


def _opposite_side(side):
    if side == "Buy":
        return "Sell"
    else:
        return "Buy"


class Helpers:
    def __init__(self, session):
        self.logger = logging.getLogger(__name__)
        self.session = session

    def close_position(self, category, symbol) -> list:
        """Market close the positions on a certain symbol.

        Required args:
            category (string): Product type: linear,inverse
            symbol (string): Symbol name

        Returns:
            Request results as list.

        Additional information:
        """

        positions = self.session.get_positions(category=category, symbol=symbol)
        positions = positions["result"]["list"]

        responses = []
        for position in positions:
            if position["side"] and float(position["size"]) != 0:
                response = self.session.place_order(
                    category=category,
                    symbol=symbol,
                    side=_opposite_side(position["side"]),
                    qty=position["size"],
                    orderType="Market",
                    positionIdx=position["positionIdx"],
                )
                responses.append(response)

        if not responses:
            self.logger.error("Tried to close_position; no position detected.")

        return responses
