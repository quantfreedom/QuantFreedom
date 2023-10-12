import "./style.css";
import { NightVision } from "night-vision";
import { DataLoader } from "./dataLoader.js";

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
});

let dl = new DataLoader();
let counter = 30;

dl.load((data) => {
  chart.data = data; // Set the initial data
  chart.fullReset(); // Reset tre time-range
  chart.se.uploadAndExec(); // Upload & exec scripts
}, counter);

counter++;

// function loadMore() {
//   let data = chart.hub.mainOv.data;
//   let t0 = data[0][0];
//   if (chart.range[0] < t0) {
//     dl.loadPast(t0 - 300000, (chunk) => {
//       // Add a new chunk at the beginning
//       data.unshift(...chunk);
//       // Yo need to update "data"
//       // when the data range is changed
//       chart.update("data");
//       chart.se.uploadAndExec();
//     });
//   }
// }

// Load new data when user scrolls left
// chart.events.on("app:$range-update", loadMore);

// // Plus check for updates every second
// setInterval(loadMore, 500);

function updateCandles() {
  if (counter < 300) {
    let data = chart.hub.mainOv.data;
    data.push(dl.getMore(counter));
    // print(data);
    chart.update("data");
    chart.scroll();
    counter++;
  }
}

setInterval(updateCandles, 200);
// Refernce for experiments
window.chart = chart;
