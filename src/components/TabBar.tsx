import { Copy, Sparkles } from "lucide-react";

const TABS = [
  { file: "data.json", label: "All Videos", icon: Copy },
  { file: "data-newly-added.json", label: "Newly Added", icon: Sparkles },
];

interface TabBarProps {
  currentFile: string;
  onTabChange: (file: string) => void;
}

export function TabBar({ currentFile, onTabChange }: TabBarProps) {
  return (
    <div className="flex shrink-0" role="tablist">
      {TABS.map((tab) => {
        const active = currentFile === tab.file;
        return (
          <button
            key={tab.file}
            className={`inline-flex items-center gap-1.5 px-5 max-md:px-3.5 py-2.5 max-md:py-2 text-[0.85rem] max-md:text-[0.8rem] font-medium whitespace-nowrap border-b-2 transition-all cursor-pointer first:rounded-tl-xl
              ${active
                ? "text-text-primary border-text-primary"
                : "text-text-secondary border-transparent hover:text-text-primary hover:bg-bg-hover"
              }`}
            role="tab"
            aria-selected={active}
            onClick={() => onTabChange(tab.file)}
          >
            <tab.icon size={16} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
