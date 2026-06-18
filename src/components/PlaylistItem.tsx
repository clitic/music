import { Eye, ThumbsUp, MessageSquare, Globe } from "lucide-react";
import type { Video } from "../types";
import { formatNumber } from "../utils";

interface PlaylistItemProps {
  song: Video;
  index: number;
  active: boolean;
  onSelect: () => void;
}

export function PlaylistItem({ song, index, active, onSelect }: PlaylistItemProps) {
  return (
    <div
      className={`flex items-center gap-2 py-2 pr-2 pl-3 max-md:p-2 cursor-pointer transition-colors border-l-3 border-b border-divider min-h-14
        ${active
          ? "bg-bg-active border-l-accent"
          : "border-l-transparent hover:bg-bg-hover"
        }`}
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect();
        }
      }}
    >
      {/* Index / Equalizer */}
      <div className={`w-6 text-[0.8rem] text-center shrink-0 ${active ? "text-accent" : "text-text-secondary"}`}>
        {active ? (
          <div className="flex items-end justify-center gap-px h-3.5">
            {[
              { h: "4px", d: "0s" },
              { h: "10px", d: "0.2s" },
              { h: "6px", d: "0.4s" },
              { h: "12px", d: "0.1s" },
            ].map((bar, i) => (
              <div
                key={i}
                className="w-[3px] bg-accent animate-eq-bounce"
                style={{ height: bar.h, animationDelay: bar.d }}
              />
            ))}
          </div>
        ) : (
          <span>{index + 1}</span>
        )}
      </div>

      {/* Thumbnail */}
      <img
        className="w-[100px] h-14 max-md:w-20 max-md:h-[45px] rounded-md object-cover shrink-0 bg-bg-hover"
        src={`https://img.youtube.com/vi/${song.id}/mqdefault.jpg`}
        alt=""
        loading="lazy"
      />

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="text-[0.85rem] max-md:text-[0.8rem] font-medium leading-tight line-clamp-2">
          {song.title}
        </div>
        <div className="flex flex-wrap gap-1.5 mt-1">
          <span className="inline-flex items-center gap-1 text-[0.65rem] text-text-secondary bg-bg-hover/50 px-2 py-0.5 rounded-full">
            <Eye size={10} className="shrink-0" />
            {formatNumber(song.view_count)}
          </span>
          <span className="inline-flex items-center gap-1 text-[0.65rem] text-text-secondary bg-bg-hover/50 px-2 py-0.5 rounded-full">
            <ThumbsUp size={10} className="shrink-0" />
            {formatNumber(song.like_count)}
          </span>
          <span className="inline-flex items-center gap-1 text-[0.65rem] text-text-secondary bg-bg-hover/50 px-2 py-0.5 rounded-full">
            <MessageSquare size={10} className="shrink-0" />
            {formatNumber(song.comment_count)}
          </span>
          <span className="inline-flex items-center gap-1 text-[0.65rem] text-text-secondary bg-bg-hover/50 px-2 py-0.5 rounded-full">
            <Globe size={10} className="shrink-0" />
            {song.frequency.toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}
