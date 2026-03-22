import { useState, useEffect } from 'react';

export default function SearchBar({ value = '', onChange, placeholder = 'Search...' }) {
  const [input, setInput] = useState(value);

  useEffect(() => { setInput(value); }, [value]);

  useEffect(() => {
    const timer = setTimeout(() => { if (input !== value) onChange(input); }, 300);
    return () => clearTimeout(timer);
  }, [input]);

  return (
    <div className="relative">
      <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-8 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
      />
      {input && (
        <button onClick={() => { setInput(''); onChange(''); }} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
          &times;
        </button>
      )}
    </div>
  );
}
