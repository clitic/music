export function formatNumber(v: number): string {
  if (v >= 1e9) return (v / 1e9).toFixed(1) + "B";
  if (v >= 1e6) return (v / 1e6).toFixed(1) + "M";
  if (v >= 1e3) return (v / 1e3).toFixed(1) + "K";
  return String(v);
}

export function timeAgo(isoDate: string): string {
  const diff = Math.max(0, Date.now() - new Date(isoDate).getTime());
  const secs = Math.floor(diff / 1000);
  const mins = Math.floor(secs / 60);
  const hrs = Math.floor(mins / 60);
  const remMins = mins % 60;

  if (hrs > 0) {
    return remMins > 0 ? `${hrs}h${remMins}m ago` : `${hrs}h ago`;
  }
  if (mins > 0) return `${mins}m ago`;
  return `${secs}s ago`;
}
