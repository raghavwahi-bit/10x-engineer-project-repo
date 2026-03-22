export default function CollectionList({ collections, activeId, onSelect, onDelete }) {
  return (
    <ul className="space-y-0.5">
      {collections.map((c) => (
        <li key={c.id} className="group flex items-center">
          <button
            onClick={() => onSelect(c.id)}
            className={`flex-1 text-left px-3 py-2 text-sm rounded-md truncate transition-colors ${
              activeId === c.id
                ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            {c.name}
          </button>
          {onDelete && (
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(c.id); }}
              className="hidden group-hover:block px-2 text-gray-400 hover:text-red-500 text-sm"
              title="Delete collection"
            >
              &times;
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
