import "./style.css";
import { NightVision } from "night-vision";
import { DataLoader } from "./dataLoader.js";
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
  if (sample(chart_data, counter)) {
    chart.update("data"); // New candle
    // chart.scroll(); // Scroll forward
  } else {
    chart.update("data");
    // chart.scroll(); // Scroll forward
  }

  counter++;
}

function sample(chart_data, counter, tf = 60000) {
  let last_candle = chart_data[chart_data.length - 1];
  let current_tick = ticks[counter];
  if (!last_candle) return;
  let tick_timestamp = current_tick[0];
  let tick_volume = current_tick[2];
  let tick_price = current_tick[1];
  let time_next = last_candle[0] + tf;

  if (tick_timestamp < time_next) {
    // And new zero-height candle
    let add_tick_to_candle = [
      last_candle[0],
      tick_price,
      tick_price,
      tick_price,
      tick_price,
      tick_volume,
    ];
    //callback('candle-close', symbol)
    chart_data.push(add_tick_to_candle);
    return true; // Make update('range')
  } else {
    last_candle[0] = time_next
    last_candle[2] = Math.max(tick_price, last_candle[2]);
    last_candle[3] = Math.min(tick_price, last_candle[3]);
    last_candle[4] = tick_price;
    last_candle[5] += tick_volume;
    return false; // Make regular('update')
  }
}
setInterval(updateCandles, 100);
// Refernce for experiments
window.chart = chart;
