import { useState, useEffect, useCallback, useMemo } from "react";
import type { Video, SortKey } from "../types";

const SORTERS: Record<SortKey, (a: Video, b: Video) => number> = {
  views: (a, b) => b.view_count - a.view_count,
  likes: (a, b) => b.like_count - a.like_count,
  comments: (a, b) => b.comment_count - a.comment_count,
  frequency: (a, b) => b.frequency - a.frequency,
};

export function usePlaylistData() {
  const [rawData, setRawData] = useState<Video[]>([]);
  const [currentSort, setCurrentSort] = useState<SortKey>("views");
  const [currentDataFile, setCurrentDataFile] = useState("data.json");
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const data = useMemo(
    () => [...rawData].sort(SORTERS[currentSort]),
    [rawData, currentSort]
  );

  const handleFileChange = useCallback((filename: string) => {
    setCurrentDataFile(filename);
    setCurrentIndex(-1);
    setLoading(true);
    setError(false);

    fetch(filename)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: Video[]) => {
        setRawData(d);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Load error:", err);
        setError(true);
        setLoading(false);
      });
  }, []);

  // Initial load
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { handleFileChange(currentDataFile) }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const selectSong = useCallback(
    (index: number) => {
      if (index < 0 || index >= data.length) return;
      setCurrentIndex(index);
      window.open(`https://youtu.be/${data[index].id}`, "_blank");
    },
    [data]
  );

  return {
    data,
    currentSort,
    setCurrentSort,
    currentDataFile,
    setCurrentDataFile: handleFileChange,
    currentIndex,
    selectSong,
    loading,
    error,
  };
}
