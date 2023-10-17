import "./style.css";
import { NightVision } from "night-vision";
import { DataLoader } from "./dataLoader.js";
import Entries from "./custom_navy_files/entries.navy";
import StopLosses from "./custom_navy_files/stop_loss.navy";
import TakeProfits from "./custom_navy_files/take_profit.navy";
import TPFilled from "./custom_navy_files/tp_filled.navy";
import SLFilled from "./custom_navy_files/sl_filled.navy";

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
  scripts: [Entries, StopLosses, TakeProfits,TPFilled,SLFilled],
});

let dl = new DataLoader();
let counter = 15;

dl.load((data) => {
  chart.data = data; // Set the initial data
  chart.fullReset(); // Reset tre time-range
  chart.se.uploadAndExec(); // Upload & exec scripts
}, counter);

counter++;
var candle_length = dl.candle_length();
function updateCandles() {
  if (counter < 100) {
    let entries = chart.hub.chart.overlays[0].data;
    entries.push(dl.more_entries(counter));

    let stoploss = chart.hub.chart.overlays[1].data;
    stoploss.push(dl.more_sl(counter));

    let takeprofit = chart.hub.chart.overlays[2].data;
    takeprofit.push(dl.more_tp(counter));

    let tp_filled = chart.hub.chart.overlays[3].data;
    tp_filled.push(dl.more_filled_tp(counter));

    let sl_filled = chart.hub.chart.overlays[4].data;
    sl_filled.push(dl.more_filled_sl(counter));

    let candles = chart.hub.chart.overlays[5].data;
    candles.push(dl.more_candles(counter));

    let rsi = chart.data.panes[1].overlays[0].data;
    rsi.push(dl.more_rsi(counter));

    chart.update("data");
    chart.scroll();
    counter++;
  }
}

setInterval(updateCandles, 200);
// Refernce for experiments
window.chart = chart;
