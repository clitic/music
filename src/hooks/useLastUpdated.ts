import { useState, useEffect } from "react";
import { timeAgo } from "../utils";

export function useLastUpdated() {
  const [lastUpdated, setLastUpdated] = useState("Loading…");

  useEffect(() => {
    let cancelled = false;

    const fetchUpdate = async () => {
      try {
        const res = await fetch(
          "https://api.github.com/repos/clitic/music/commits?sha=gh-pages&per_page=1"
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        if (cancelled) return;
        if (!Array.isArray(json) || json.length === 0)
          throw new Error("No commits");
        const isoDate =
          json[0].commit?.committer?.date || json[0].commit?.author?.date;
        if (isoDate) setLastUpdated(timeAgo(isoDate));
      } catch {
        if (!cancelled) setLastUpdated("");
      }
    };

    fetchUpdate();
    const interval = setInterval(fetchUpdate, 60000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return lastUpdated;
}
