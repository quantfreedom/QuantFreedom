import data from "./data/data.json";

var entries = data.entries;
var candles = data.candles;

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
              name: "BTC Tether US Binance",
              type: "Candles",
              data: candles.slice(0, number),
              settings: {},
              props: {},
            },
          ],
        },
        // {
        //   settings: {},
        //   overlays: [
        //     {
        //       name: "Rsi",
        //       type: "Spline",
        //       data: rsi.slice(0, number),
        //     },
        //   ],
        // },
      ],
    });
  }
  candle_length() {
    return candles.length;
  }
  more_candles(number) {
    return candles.slice(number - 1, number)[0];
  }
  more_entries(number) {
    return entries.slice(number - 1, number)[0];
  }
  // more_sl(number) {
  //   return stoplosses.slice(number - 1, number)[0];
  // }
  // more_tp(number) {
  //   return takeprofits.slice(number - 1, number)[0];
  // }
  // more_filled_sl(number) {
  //   return sl_filled.slice(number - 1, number)[0];
  // }
  // more_filled_tp(number) {
  //   return tp_filled.slice(number - 1, number)[0];
  // }
  // more_rsi(number) {
  //   return rsi.slice(number - 1, number)[0];
  // }
}

export { DataLoader };
