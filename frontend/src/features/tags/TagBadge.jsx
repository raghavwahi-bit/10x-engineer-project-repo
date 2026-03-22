export default function TagBadge({ tag, onRemove }) {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300">
      {tag.name}
      {onRemove && (
        <button onClick={() => onRemove(tag.id)} className="hover:text-indigo-900 dark:hover:text-indigo-100 ml-0.5">&times;</button>
      )}
    </span>
  );
}
