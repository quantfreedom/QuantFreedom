import data from "./data/data.json";

var entries = data.entries
var stoplosses = data.stoplosses
var takeprofits = data.takeprofits
var candles = data.candles

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
              data: stoplosses.slice(0, number),
              settings: {},
              props: {},
            },
            {
              name: "Take Profit",
              type: "TakeProfits",
              data: takeprofits.slice(0, number),
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
    return stoplosses.slice(number - 1, number)[0];
  }
  more_tp(number) {
    return takeprofits.slice(number - 1, number)[0];
  }
}

export { DataLoader };
