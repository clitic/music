import { useState, useEffect, useRef } from "react";
import {
  Eye,
  ThumbsUp,
  MessageSquare,
  Globe,
  SlidersHorizontal,
  ChevronDown,
  Check,
} from "lucide-react";
import type { SortKey } from "../types";

const SORT_OPTIONS: { value: SortKey; label: string; icon: typeof Eye }[] = [
  { value: "views", label: "Views", icon: Eye },
  { value: "likes", label: "Likes", icon: ThumbsUp },
  { value: "comments", label: "Comments", icon: MessageSquare },
  { value: "frequency", label: "Region Coverage", icon: Globe },
];

interface SortDropdownProps {
  currentSort: SortKey;
  onSortChange: (key: SortKey) => void;
}

export function SortDropdown({ currentSort, onSortChange }: SortDropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("click", handleClick);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("click", handleClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const sortLabel =
    SORT_OPTIONS.find((o) => o.value === currentSort)?.label ?? "Views";

  return (
    <div ref={ref} className="relative inline-block">
      <button
        className="inline-flex items-center gap-1.5 px-4 max-md:px-3 py-2 max-md:py-1.5 rounded-full bg-bg-secondary text-text-primary text-[0.85rem] max-md:text-[0.8rem] font-medium hover:bg-bg-hover transition-colors whitespace-nowrap cursor-pointer"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((prev) => !prev);
        }}
      >
        <SlidersHorizontal size={16} />
        <span>{sortLabel}</span>
        <ChevronDown
          size={16}
          className={`text-text-secondary transition-transform duration-200 shrink-0 ${open ? "rotate-180" : ""}`}
        />
      </button>

      <div
        className={`absolute top-[calc(100%+4px)] right-0 min-w-[200px] bg-bg-secondary rounded-xl py-2 z-40 shadow-[0_4px_16px_rgba(0,0,0,0.3)] transition-all duration-150
          ${open ? "opacity-100 visible translate-y-0 scale-100" : "opacity-0 invisible -translate-y-1 scale-[0.97]"}`}
        role="listbox"
      >
        {SORT_OPTIONS.map((opt) => {
          const selected = currentSort === opt.value;
          return (
            <div
              key={opt.value}
              className={`flex items-center gap-2.5 px-4 py-2.5 text-[0.85rem] cursor-pointer transition-colors hover:bg-bg-hover
                ${selected ? "text-accent" : "text-text-primary"}`}
              role="option"
              aria-selected={selected}
              onClick={(e) => {
                e.stopPropagation();
                onSortChange(opt.value);
                setOpen(false);
              }}
            >
              <opt.icon size={18} className="shrink-0" />
              {opt.label}
              <Check
                size={16}
                className={`ml-auto shrink-0 text-accent ${selected ? "block" : "hidden"}`}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
