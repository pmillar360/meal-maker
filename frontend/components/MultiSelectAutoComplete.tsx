"use client";
import { useState, useRef, useEffect } from "react";

export type Option = {
  id: number;
  label: string;
};

type Props = {
  options: Option[];
  selectedOptions: Option[];
  onChange?: (selected: Option[]) => void; // optional callback when selected changes
};

export default function MultiSelectAutoComplete({ options, selectedOptions, onChange }: Props) {
  const [input, setInput] = useState("");
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const listRef = useRef<HTMLUListElement>(null);

  const filtered = options.filter(
    (opt) =>
      opt.label.toLowerCase().includes(input.toLowerCase()) &&
      !selectedOptions.some((s) => s.id === opt.id)
  ).sort((a, b) => a.id - b.id);

  const addOption = (newOption: Option) => {
    selectedOptions.push(newOption)
    setInput("");
    setHighlightedIndex(0);
    onChange?.(selectedOptions);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (filtered.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1) % filtered.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev === 0 ? filtered.length - 1 : prev - 1
      );
    } else if (e.key === "Enter") {
      e.preventDefault();
      addOption(filtered[highlightedIndex]);
    } else if (e.key === "Escape") {
      e.preventDefault();
      setInput('');
    }
  };

  useEffect(() => {
    const list = listRef.current;
    if (list) {
      const item = list.children[highlightedIndex] as HTMLElement;
      if (item) item.scrollIntoView({ block: "nearest" });
    }
  }, [highlightedIndex]);

  return (
    <div className="max-w-md relative">
      {/* Input */}
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        className="border p-2 w-full rounded-md text-sm form-input"
        placeholder="Type to search..."
      />

      {/* Suggestions */}
      {input && filtered.length > 0 && (
        <ul
          ref={listRef}
          className="border mt-1 bg-white max-h-40 overflow-y-auto absolute z-50 w-full"
        >
          {filtered.map((opt, idx) => (
            <li
              key={opt.id}
              className={`p-2 cursor-pointer ${
                idx === highlightedIndex ? "bg-blue-200" : "hover:bg-blue-100"
              }`}
              onClick={() => addOption(opt)}
              onMouseEnter={() => setHighlightedIndex(idx)}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
