import candles from "./data/data.json";

class DataLoader {

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
