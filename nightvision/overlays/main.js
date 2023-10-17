import "./style.css";
import { NightVision } from "night-vision";
import { DataLoader } from "./dataLoader.js";
import Entries from "./custom_navy_files/entries.navy";
import StopLosses from "./custom_navy_files/stop_loss.navy";
import TakeProfits from "./custom_navy_files/take_profit.navy";

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
  scripts: [Entries, StopLosses, TakeProfits], // Add the script
});

let dl = new DataLoader();
let counter = 2;

dl.load((data) => {
  chart.data = data; // Set the initial data
  chart.fullReset(); // Reset tre time-range
  chart.se.uploadAndExec(); // Upload & exec scripts
}, counter);

counter++;
function updateCandles() {
  if (counter < 9) {
    let stoploss = chart.hub.chart.overlays[1].data;
    let entries = chart.hub.chart.overlays[0].data;
    let takeprofit = chart.hub.chart.overlays[2].data;
    let candles = chart.hub.chart.overlays[3].data;
    entries.push(dl.more_entries(counter));
    stoploss.push(dl.more_sl(counter));
    takeprofit.push(dl.more_tp(counter));
    candles.push(dl.more_candles(counter));
    // print(data);
    chart.update("data");
    chart.scroll();
    counter++;
  }
}

setInterval(updateCandles, 400);

// Refernce for experiments
window.chart = chart;