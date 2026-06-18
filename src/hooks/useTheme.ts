import { useState, useCallback } from "react";
import type { Theme } from "../types";

const THEMES: Theme[] = ["adaptive", "light", "dark"];

function getStoredTheme(): Theme {
  return (localStorage.getItem("yt-music-theme") as Theme) || "dark";
}

function applyToDOM(t: Theme) {
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem("yt-music-theme", t);
}

// Apply theme immediately on module load (before first render) to avoid flash
applyToDOM(getStoredTheme());

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(getStoredTheme);

  const cycleTheme = useCallback(() => {
    setTheme((prev) => {
      const idx = THEMES.indexOf(prev);
      const next = THEMES[(idx + 1) % THEMES.length];
      applyToDOM(next);
      return next;
    });
  }, []);

  return { theme, cycleTheme };
}
