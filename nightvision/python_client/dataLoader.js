import candles from "./data/candles.json";

class DataLoader {
  // constructor() {
  //   this.URL = "https://api1.binance.com/api/v3/klines";
  //   this.SYM = "BTCUSDT";
  //   this.TF = "1m"; // See binance api definitions

  //   this.loading = false;
  // }

  load(callback, number) {
    callback({
      panes: [
        {
          overlays: [
            {
              name: "BTC Tether US Binance",
              type: "Candles",
              data: candles.slice(0, number),
            },
          ],
        },
      ],
    });
  }

  async loadPast(number, callback) {
    callback(candles.slice(number, number + 30000));
  }
  getMore(number) {
     return candles.slice(number - 1, number)[0];
  }
}

export { DataLoader };
