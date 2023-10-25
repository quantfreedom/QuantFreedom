// Fixind resizing bug (when loading chart offscreen)
// define an observer instance
var observer = new IntersectionObserver(onIntersection, {
  root: null, // default is the viewport
  threshold: 0.5 // percentage of target's visible area. Triggers "onIntersection"
});

// callback is called on intersection change
function onIntersection(entries, opts) {
  if (chart) chart.update();
}

// Use the observer to observe an element
observer.observe(document.querySelector("#app"));
