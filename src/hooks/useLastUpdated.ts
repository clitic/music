import { useState, useEffect } from "react";
import { timeAgo } from "../utils";

export function useLastUpdated() {
  const [lastUpdated, setLastUpdated] = useState("Loading…");

  useEffect(() => {
    let cancelled = false;

    const fetchUpdate = async () => {
      try {
        const res = await fetch("last-updated.json");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json: { updatedAt: string } = await res.json();
        if (!cancelled && json.updatedAt) {
          setLastUpdated(timeAgo(json.updatedAt));
        }
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
