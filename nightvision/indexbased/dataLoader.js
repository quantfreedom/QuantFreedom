import data from "./data/data.json";
var candles = data.candles;

class DataLoader {
  load(callback) {
    callback({
      indexBased: true,
      panes: [
        {
          overlays: [
            {
              name: "BTC Tether US Binance",
              type: "Candles",
              data: candles,
              settings: {},
              props: {},
            },
          ],
        },
      ],
    });
  }
}

export { DataLoader };
