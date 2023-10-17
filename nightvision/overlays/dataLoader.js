import candles from "./data/candles.json";
import entries from "./data/entries.json";
import stoploss from "./data/stop_loss.json";
import takeprofit from "./data/take_profit.json";

class DataLoader {
  load(callback, number) {
    callback({
      panes: [
        {
          overlays: [
            {
              name: "Entries",
              type: "Entries",
              data: entries.slice(0, number),
              settings: {},
              props: {},
            },
            {
              name: "Stop Loss",
              type: "StopLosses",
              data: stoploss.slice(0, number),
              settings: {},
              props: {},
            },
            {
              name: "Take Profit",
              type: "TakeProfits",
              data: takeprofit.slice(0, number),
              settings: {},
              props: {},
            },

            {
              name: "BTC Tether US Binance",
              type: "Candles",
              data: candles.slice(0, number),
              settings: {},
              props: {},
            },
          ],
        },
      ],
    });
  }

  more_candles(number) {
    return candles.slice(number - 1, number)[0];
  }
  more_entries(number) {
    return entries.slice(number - 1, number)[0];
  }
  more_sl(number) {
    return stoploss.slice(number - 1, number)[0];
  }
  more_tp(number) {
    return takeprofit.slice(number - 1, number)[0];
  }
}

export { DataLoader };
