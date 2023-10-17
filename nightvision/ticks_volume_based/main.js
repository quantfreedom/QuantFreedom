import "./style.css";
import { NightVision } from "night-vision";
import { DataLoader } from "./dataLoader.js";
// import sampler from "./lib/ohlcvSampler.js";
import ticks from "./tick.json";

document.querySelector("#app").innerHTML = `
<style>
body {
    background-color: #0c0d0e;
}
</style>
<div id="chart-container"></div>
`;

let chart = new NightVision("chart-container", {
  autoResize: true,
  colors: { back: "#111113", grid: "#2e2f3055" },
  config: {},
});

let dl = new DataLoader();
dl.load((data) => {
  chart.data = data; // Set the initial data
  chart.fullReset(); // Reset tre time-range
  chart.se.uploadAndExec(); // Upload & exec scripts
});

let counter = 0;
// Setup a trade data stream
function updateCandles() {
  if (!chart.hub.mainOv) return;
  let chart_data = chart.hub.mainOv.data;
  let layout = chart.layout.main;
  if (sample(chart, chart_data, counter, layout)) {
    chart.update("data"); // New candle
    // chart.scroll(); // Scroll forward
  } else {
    chart.hub.indexBased = true;
    chart.update("data");
    chart.scroll(); // Scroll forward
    chart.hub.indexBased = false;
  }

  counter++;
}

function sample(chart, chart_data, counter, layout, vol_per_candle = 1000000) {
  let last_candle = chart_data[chart_data.length - 1];
  let current_tick = ticks[counter];
  let candle_volume = last_candle[5];
  if (!last_candle) return;
  let tick_timestamp = current_tick[0];
  let tick_price = current_tick[1];
  let tick_volume = current_tick[2];
  let new_candle_volume = tick_volume + candle_volume;

  let timestamp =
    new_candle_volume < vol_per_candle ? tick_timestamp : last_candle[0];

  if (new_candle_volume < vol_per_candle) {
    // And new zero-height candle
    let add_tick_to_candle = [
      timestamp,
      tick_price,
      tick_price,
      tick_price,
      tick_price,
      new_candle_volume,
    ];
    //callback('candle-close', symbol)
    chart_data.push(add_tick_to_candle);
    return true; // Make update('range')
  } else {
    last_candle[0] = timestamp;
    last_candle[2] = Math.max(tick_price, last_candle[2]);
    last_candle[3] = Math.min(tick_price, last_candle[3]);
    last_candle[4] = tick_price;
    last_candle[5] = 0;
    return false; // Make regular('update')
  }
}
setInterval(updateCandles, 100);
// Refernce for experiments
window.chart = chart;
