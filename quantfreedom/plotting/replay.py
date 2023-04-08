# def replay_trade_plotter(
#     open_prices,
#     high_prices,
#     low_prices,
#     close_prices,
#     order_records,
# ):
#     start = order_records["bar"].min() - 2
#     end = order_records["bar"].max() + 3

#     x_index = open_prices.index[start:end]
#     open_prices = open_prices[start:end]
#     high_prices = high_prices[start:end]
#     low_prices = low_prices[start:end]
#     close_prices = close_prices[start:end]

#     order_price = np.full(end - start, np.nan)
#     avg_entry = np.full(end - start, np.nan)
#     stop_loss = np.full(end - start, np.nan)
#     trailing_sl = np.full(end - start, np.nan)
#     take_profit = np.full(end - start, np.nan)

#     log_counter = 0
#     array_counter = 0
#     temp_avg_entry = 0
#     temp_stop_loss = 0
#     temp_trailing_sl = 0
#     temp_take_profit = 0

#     for i in range(start, end):
#         if (
#             log_counter <= order_records["order_id"].max()
#             and order_records["bar"][log_counter] == i
#         ):
#             if temp_avg_entry != order_records["avg_entry"][log_counter]:
#                 temp_avg_entry = order_records["avg_entry"][log_counter]
#             else:
#                 temp_avg_entry = np.nan

#             if temp_stop_loss != order_records["sl_prices"][log_counter]:
#                 temp_stop_loss = order_records["sl_prices"][log_counter]
#             else:
#                 temp_stop_loss = np.nan

#             if temp_trailing_sl != order_records["tsl_prices"][log_counter]:
#                 temp_trailing_sl = order_records["tsl_prices"][log_counter]
#             else:
#                 temp_take_profit = np.nan

#             if temp_take_profit != order_records["tp_prices"][log_counter]:
#                 temp_take_profit = order_records["tp_prices"][log_counter]
#             else:
#                 temp_take_profit = np.nan

#             if np.isnan(order_records["real_pnl"][log_counter]):
#                 order_price[array_counter] = order_records["price"][log_counter]
#                 avg_entry[array_counter] = temp_avg_entry
#                 stop_loss[array_counter] = temp_stop_loss
#                 trailing_sl[array_counter] = temp_trailing_sl
#                 take_profit[array_counter] = temp_take_profit

#             elif order_records["real_pnl"][log_counter] > 0 and (
#                 order_records["order_type"][log_counter] == OrderType.LongTP
#                 or order_records["order_type"][log_counter] == OrderType.ShortTP
#             ):
#                 order_price[array_counter] = np.nan
#                 avg_entry[array_counter] = temp_avg_entry
#                 stop_loss[array_counter] = temp_stop_loss
#                 trailing_sl[array_counter] = temp_trailing_sl
#                 take_profit[array_counter] = order_records["tp_prices"][log_counter]

#             elif order_records["real_pnl"][log_counter] > 0 and (
#                 order_records["order_type"][log_counter] == OrderType.LongTSL
#                 or order_records["order_type"][log_counter] == OrderType.ShortTSL
#             ):
#                 order_price[array_counter] = np.nan
#                 avg_entry[array_counter] = temp_avg_entry
#                 stop_loss[array_counter] = temp_stop_loss
#                 trailing_sl[array_counter] = order_records["tsl_prices"][log_counter]
#                 take_profit[array_counter] = temp_take_profit

#             elif order_records["real_pnl"][log_counter] <= 0:
#                 order_price[array_counter] = np.nan
#                 avg_entry[array_counter] = temp_avg_entry
#                 stop_loss[array_counter] = order_records["sl_prices"][log_counter]
#                 trailing_sl[array_counter] = order_records["tsl_prices"][log_counter]
#                 take_profit[array_counter] = temp_take_profit

#             temp_avg_entry = order_records["avg_entry"][log_counter]
#             temp_stop_loss = order_records["sl_prices"][log_counter]
#             temp_trailing_sl = order_records["tsl_prices"][log_counter]
#             temp_take_profit = order_records["tp_prices"][log_counter]
#             log_counter += 1
#             if (
#                 log_counter <= order_records["order_id"].max()
#                 and order_records["bar"][log_counter] == i
#             ):
#                 if temp_avg_entry != order_records["avg_entry"][log_counter]:
#                     temp_avg_entry = order_records["avg_entry"][log_counter]
#                 else:
#                     temp_avg_entry = np.nan

#                 if temp_stop_loss != order_records["sl_prices"][log_counter]:
#                     temp_stop_loss = order_records["sl_prices"][log_counter]
#                 else:
#                     temp_stop_loss = np.nan

#                 if temp_trailing_sl != order_records["tsl_prices"][log_counter]:
#                     temp_trailing_sl = order_records["tsl_prices"][log_counter]
#                 else:
#                     temp_take_profit = np.nan

#                 if temp_take_profit != order_records["tp_prices"][log_counter]:
#                     temp_take_profit = order_records["tp_prices"][log_counter]
#                 else:
#                     temp_take_profit = np.nan

#                 if np.isnan(order_records["real_pnl"][log_counter]):
#                     order_price[array_counter] = order_records["price"][log_counter]
#                     avg_entry[array_counter] = temp_avg_entry
#                     stop_loss[array_counter] = temp_stop_loss
#                     trailing_sl[array_counter] = temp_trailing_sl
#                     take_profit[array_counter] = temp_take_profit

#                 elif order_records["real_pnl"][log_counter] > 0 and (
#                     order_records["order_type"][log_counter] == OrderType.LongTP
#                     or order_records["order_type"][log_counter] == OrderType.ShortTP
#                 ):
#                     order_price[array_counter] = np.nan
#                     avg_entry[array_counter] = temp_avg_entry
#                     stop_loss[array_counter] = temp_stop_loss
#                     trailing_sl[array_counter] = temp_trailing_sl
#                     take_profit[array_counter] = order_records["tp_prices"][log_counter]

#                 elif order_records["real_pnl"][log_counter] > 0 and (
#                     order_records["order_type"][log_counter] == OrderType.LongTSL
#                     or order_records["order_type"][log_counter] == OrderType.ShortTSL
#                 ):
#                     order_price[array_counter] = np.nan
#                     avg_entry[array_counter] = temp_avg_entry
#                     stop_loss[array_counter] = temp_stop_loss
#                     trailing_sl[array_counter] = order_records["tsl_prices"][
#                         log_counter
#                     ]
#                     take_profit[array_counter] = temp_take_profit

#                 elif order_records["real_pnl"][log_counter] <= 0:
#                     order_price[array_counter] = np.nan
#                     avg_entry[array_counter] = temp_avg_entry
#                     stop_loss[array_counter] = order_records["sl_prices"][log_counter]
#                     trailing_sl[array_counter] = order_records["tsl_prices"][
#                         log_counter
#                     ]
#                     take_profit[array_counter] = temp_take_profit

#                 temp_avg_entry = order_records["avg_entry"][log_counter]
#                 temp_stop_loss = order_records["sl_prices"][log_counter]
#                 temp_trailing_sl = order_records["tsl_prices"][log_counter]
#                 temp_take_profit = order_records["tp_prices"][log_counter]
#                 log_counter += 1
#         array_counter += 1

#     play_button = {
#         "args": [
#             None,
#             {
#                 "frame": {"duration": 150, "redraw": True},
#                 "fromcurrent": True,
#                 "transition": {"duration": 0, "easing": "quadratic-in-out"},
#             },
#         ],
#         "label": "Play",
#         "method": "animate",
#     }

#     pause_button = {
#         "args": [
#             [None],
#             {
#                 "frame": {"duration": 0, "redraw": False},
#                 "mode": "immediate",
#                 "transition": {"duration": 0},
#             },
#         ],
#         "label": "Pause",
#         "method": "animate",
#     }

#     sliders_steps = [
#         {
#             "args": [
#                 [0, i],  # 0, in order to reset the image, i in order to plot frame i
#                 {
#                     "frame": {"duration": 150, "redraw": True},
#                     "mode": "immediate",
#                     "transition": {"duration": 0},
#                 },
#             ],
#             "label": i,
#             "method": "animate",
#         }
#         for i in range(order_price.size)
#     ]

#     sliders_dict = {
#         "active": 0,
#         "yanchor": "top",
#         "xanchor": "left",
#         "currentvalue": {
#             "font": {"size": 20},
#             "prefix": "candle:",
#             "visible": True,
#             "xanchor": "right",
#         },
#         "transition": {"duration": 300, "easing": "cubic-in-out"},
#         "pad": {"b": 10, "t": 50},
#         "len": 0.9,
#         "x": 0.1,
#         "y": 0,
#         "steps": sliders_steps,
#     }

#     fig = go.Figure()

#     fig.add_candlestick(
#         x=x_index,
#         open=open_prices,
#         high=high_prices,
#         low=low_prices,
#         close=close_prices,
#         name="Candles",
#     )

#     # entries
#     fig.add_scatter(
#         name="Entries",
#         x=x_index,
#         y=order_price,
#         mode="markers",
#         marker=dict(
#             color="yellow", size=10, symbol="circle", line=dict(color="black", width=2)
#         ),
#     )

#     # avg entrys
#     fig.add_scatter(
#         name="Avg Entries",
#         x=x_index,
#         y=avg_entry,
#         mode="markers",
#         marker=dict(
#             color="#57FF30", size=10, symbol="square", line=dict(color="black", width=2)
#         ),
#     )

#     # stop loss
#     fig.add_scatter(
#         name="Stop Loss",
#         x=x_index,
#         y=stop_loss,
#         mode="markers",
#         marker=dict(
#             color="red", size=10, symbol="x", line=dict(color="black", width=2)
#         ),
#     )

#     # trailing stop loss
#     fig.add_scatter(
#         name="Trailing SL",
#         x=x_index,
#         y=trailing_sl,
#         mode="markers",
#         marker=dict(
#             color="orange", size=10, symbol="x", line=dict(color="black", width=2)
#         ),
#     )

#     # take profits
#     fig.add_scatter(
#         name="Take Profits",
#         x=x_index,
#         y=take_profit,
#         mode="markers",
#         marker=dict(
#             color="#57FF30", size=10, symbol="star", line=dict(color="black", width=2)
#         ),
#     )

#     fig.update_layout(
#         xaxis=dict(title="Date", rangeslider=dict(visible=False)),
#         title="Candles over time",
#         updatemenus=[dict(type="buttons", buttons=[play_button, pause_button])],
#         sliders=[sliders_dict],
#         height=600,
#     )

#     for_loop_len = order_price.size
#     for x in range(15, 0, -1):
#         if for_loop_len % x == 0:
#             for_loop_steps = x
#             break

#     frames = []
#     print(for_loop_len)
#     print(for_loop_steps)
#     for i in range(0, for_loop_len + 1, for_loop_steps):
#         frames.append(
#             # name, I imagine, is used to bind to frame i :)
#             go.Frame(
#                 data=[
#                     go.Candlestick(
#                         x=x_index,
#                         open=open_prices[:i],
#                         high=high_prices[:i],
#                         low=low_prices[:i],
#                         close=close_prices[:i],
#                     ),
#                     go.Scatter(
#                         x=x_index,
#                         y=order_price[:i],
#                     ),
#                     go.Scatter(
#                         x=x_index,
#                         y=avg_entry[:i],
#                     ),
#                     go.Scatter(
#                         x=x_index,
#                         y=stop_loss[:i],
#                     ),
#                     go.Scatter(
#                         x=x_index,
#                         y=trailing_sl[:i],
#                     ),
#                     go.Scatter(
#                         x=x_index,
#                         y=take_profit[:i],
#                     ),
#                 ],
#                 traces=[0, 1, 2, 3, 4],
#                 name=f"{i}",
#             )
#         )
#     fig.update(frames=frames)
#     fig.show()
