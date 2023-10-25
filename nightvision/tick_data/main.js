import "./style.css";
import { NightVision } from "night-vision";
import { DataLoader } from "./lib/dataLoader.js";
import wsx from "./lib/wsx.js";
import sampler from "./lib/ohlcvSampler.js";
import ticks from "./data/ticks.json";

document.querySelector("#app").innerHTML = `
<style>
body {
    background-color: #0c0d0e;
}
</style>
<div id="chart-container"></div>
`;
let chart = new NightVision("chart-container", {
  // data,
  autoResize: true,
  colors: { back: "#111113", grid: "#2e2f3055" },
  config: {},
});
let dl = new DataLoader();

// // Load the first piece of the data
dl.load((data) => {
  chart.data = data; // Set the initial data
  chart.fullReset(); // Reset tre time-range
  chart.se.uploadAndExec(); // Upload & exec scripts
});

// function loadMore() {
//   let data = chart.hub.mainOv.data;
//   let t0 = data[0][0];
//   if (chart.range[0] < t0) {
//     dl.loadMore(t0 - 1, (chunk) => {
//       // Add a new chunk at the beginning
//       data.unshift(...chunk);
//       // Yo need to update "data"
//       // when the data range is changed
//       chart.update("data");
//       chart.se.uploadAndExec();
//     });
//   }
// }

// Send an update to the script engine
// async function update() {
//   await chart.se.updateData();
//   var delay; // Floating update rate
//   if (chart.hub.mainOv.dataSubset.length < 1000) {
//     delay = 10;
//   } else {
//     delay = 1000;
//   }
//   setTimeout(update, delay);
// }

// // Load new data when user scrolls left
// chart.events.on("app:$range-update", loadMore);

// // Plus check for updates every second
// setInterval(loadMore, 500);

// TA + chart update loop
// setTimeout(update, 0);
// var count = 0
// for (count = 0; count < 1000; count++) {
//   setTimeout(function() {
//     let data = chart.hub.mainOv.data;
//     let tick = ticks[count];
//     let trade = {
//       price: tick[1],
//       volume: tick[1] * tick[2],
//       timestamp: tick[0],
//     };
//     if (sampler(data, trade)) {
//       chart.update("data"); // New candle
//       chart.scroll(); // Scroll forward
//     }
//   }, 1000);
// }

async function test() {
  for (let count = 0; count < 1000; count++) {
    let data = chart.hub.mainOv.data;
    let tick = ticks[count];
    let trade = {
      price: tick[1],
      volume: tick[1] * tick[2],
      timestamp: tick[0],
    };
    if (sampler(data, trade)) {
      chart.update("data"); // New candle
      chart.scroll(); // Scroll forward
    }
    await delay(10000);
    console.log("hi");
  }
}

test();
window.chart = chart;
