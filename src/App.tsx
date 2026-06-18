import { Header } from "./components/Header";
import { TabBar } from "./components/TabBar";
import { SortDropdown } from "./components/SortDropdown";
import { PlaylistItem } from "./components/PlaylistItem";
import { useTheme } from "./hooks/useTheme";
import { usePlaylistData } from "./hooks/usePlaylistData";
import { useLastUpdated } from "./hooks/useLastUpdated";

export default function App() {
  const { theme, cycleTheme } = useTheme();
  const {
    data,
    currentSort,
    setCurrentSort,
    currentDataFile,
    setCurrentDataFile,
    currentIndex,
    selectSong,
    loading,
    error,
  } = usePlaylistData();
  const lastUpdated = useLastUpdated();

  return (
    <>
      <Header theme={theme} onCycleTheme={cycleTheme} lastUpdated={lastUpdated} />

      <main className="flex flex-col flex-1 max-w-[800px] w-full mx-auto px-6 max-md:p-0 min-h-0 overflow-hidden">
        {/* Toolbar */}
        <div className="flex items-center justify-between bg-bg-secondary rounded-t-xl max-md:rounded-none border-b border-divider pr-3 gap-2 shrink-0 flex-wrap">
          <TabBar currentFile={currentDataFile} onTabChange={setCurrentDataFile} />
          <SortDropdown currentSort={currentSort} onSortChange={setCurrentSort} />
        </div>

        {/* Track count */}
        <div className="flex items-center px-4 py-1.5 bg-bg-secondary border-b border-divider shrink-0">
          <div className="text-xs text-text-secondary">
            {loading ? "Loading…" : `${data.length} tracks`}
          </div>
        </div>

        {/* Scrollable list */}
        <div className="flex-1 overflow-y-auto bg-bg-secondary rounded-b-xl max-md:rounded-none min-h-0">
          {loading ? (
            <div className="flex flex-col items-center justify-center p-10 text-text-secondary text-center gap-2">
              <div className="w-6 h-6 border-3 border-divider border-t-accent rounded-full animate-spin" />
              <span>Loading tracks…</span>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center p-10 text-text-secondary text-center gap-2">
              <span>Failed to load tracks</span>
            </div>
          ) : (
            data.map((song, i) => (
              <PlaylistItem
                key={song.id}
                song={song}
                index={i}
                active={i === currentIndex}
                onSelect={() => selectSong(i)}
              />
            ))
          )}
        </div>
      </main>
    </>
  );
}
