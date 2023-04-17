if position != 0:
    tpl = (  # total possible loss no fees on second trade
        (
            (position / average_entry)
            * (sl_prices - average_entry)
        )
        - (
            (position / average_entry)
            * average_entry
            * static_variables_tuple.fee_pct
        )
        - (
            (position / average_entry)
            * sl_prices
            * static_variables_tuple.fee_pct
        )
        + -(account_state.equity * entry_order.size_pct)
    )

    size_value = -(
        (
            tpl * price_open_values[-1] * average_entry
            + price_open_values[-1]
            * position
            * average_entry
            - sl_prices_new * price_open_values[-1] * position
            + sl_prices_new
            * price_open_values[-1]
            * position
            * static_variables_tuple.fee_pct
            + price_open_values[-1]
            * position
            * average_entry
            * static_variables_tuple.fee_pct
        )
        / (
            average_entry
            * (
                price_open_values[-1]
                - sl_prices_new
                + price_open_values[-1] * static_variables_tuple.fee_pct
                + sl_prices_new * static_variables_tuple.fee_pct
            )
        )
    )
    position_new = position + size_value
    average_entry_new = (size_value + position) / (
        (size_value / price_open_values[-1]) + (position / average_entry_new)
    )
    sl_pcts_new = (average_entry_new - sl_prices_new) / average_entry_new 
