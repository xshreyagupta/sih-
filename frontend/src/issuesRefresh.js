const listeners = new Set();

export function onIssuesRefresh(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function requestIssuesRefresh() {
  listeners.forEach((fn) => {
    try {
      fn();
    } catch (err) {
      console.error("issuesRefresh listener failed:", err);
    }
  });
}
