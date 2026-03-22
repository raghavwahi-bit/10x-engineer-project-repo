import { useState } from 'react';
import useTags from '../../hooks/useTags';

export default function TagSelector({ selectedTags = [], onAdd, onRemove }) {
  const { tags: allTags } = useTags();
  const [input, setInput] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  const available = allTags.filter(
    (t) => !selectedTags.some((s) => s.id === t.id) && t.name.toLowerCase().includes(input.toLowerCase())
  );

  const handleSelect = (tag) => {
    onAdd(tag);
    setInput('');
    setShowDropdown(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && input.trim()) {
      e.preventDefault();
      const existing = allTags.find((t) => t.name.toLowerCase() === input.trim().toLowerCase());
      if (existing && !selectedTags.some((s) => s.id === existing.id)) {
        handleSelect(existing);
      } else if (!existing && /^[a-zA-Z0-9_-]{3,50}$/.test(input.trim())) {
        onAdd({ name: input.trim(), isNew: true });
        setInput('');
        setShowDropdown(false);
      }
    }
  };

  return (
    <div className="relative">
      <div className="flex flex-wrap gap-1.5 mb-2">
        {selectedTags.map((tag) => (
          <span key={tag.id || tag.name} className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300">
            {tag.name}
            <button type="button" onClick={() => onRemove(tag)} className="hover:text-indigo-900 dark:hover:text-indigo-100">&times;</button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => { setInput(e.target.value); setShowDropdown(true); }}
        onFocus={() => setShowDropdown(true)}
        onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
        onKeyDown={handleKeyDown}
        placeholder="Add tag..."
        className="w-full px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
      {showDropdown && available.length > 0 && (
        <ul className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-md shadow-lg max-h-40 overflow-y-auto">
          {available.slice(0, 10).map((tag) => (
            <li key={tag.id}>
              <button
                type="button"
                onMouseDown={() => handleSelect(tag)}
                className="w-full text-left px-3 py-1.5 text-sm text-gray-900 dark:text-gray-100 hover:bg-indigo-50 dark:hover:bg-gray-700"
              >
                {tag.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
