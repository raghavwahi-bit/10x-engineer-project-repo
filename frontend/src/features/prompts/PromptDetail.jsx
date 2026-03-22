import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import ConfirmDialog from '../../components/ConfirmDialog';
import TagBadge from '../tags/TagBadge';
import { deletePrompt, runPrompt } from '../../api/prompts';

export default function PromptDetail({ prompt, tags, onAddTags, onRemoveTag, collections }) {
  const navigate = useNavigate();
  const [showDelete, setShowDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [running, setRunning] = useState(false);
  const [aiOutput, setAiOutput] = useState(null);
  const [aiError, setAiError] = useState(null);

  const collection = collections?.find((c) => c.id === prompt.collection_id);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deletePrompt(prompt.id);
      navigate('/');
    } catch {
      setDeleting(false);
    }
  };

  const handleAddTag = async (e) => {
    e.preventDefault();
    const name = tagInput.trim();
    if (!name || !/^[a-zA-Z0-9_-]{3,50}$/.test(name)) return;
    try {
      await onAddTags([name]);
      setTagInput('');
    } catch {
      // handled by parent
    }
  };

  const handleRun = async () => {
    setRunning(true);
    setAiError(null);
    setAiOutput(null);
    try {
      const result = await runPrompt(prompt.id);
      setAiOutput(result);
    } catch (err) {
      setAiError(err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-3xl">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{prompt.title}</h1>
          {collection && (
            <span className="text-sm text-indigo-600 dark:text-indigo-400 mt-1 inline-block">{collection.name}</span>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="success" size="sm" onClick={handleRun} loading={running}>
            <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            Run
          </Button>
          <Button variant="secondary" size="sm" onClick={() => navigate(`/prompts/${prompt.id}/edit`)}>Edit</Button>
          <Button variant="danger" size="sm" onClick={() => setShowDelete(true)}>Delete</Button>
        </div>
      </div>

      {prompt.description && (
        <p className="text-gray-600 dark:text-gray-300 mb-4">{prompt.description}</p>
      )}

      <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Prompt</span>
        </div>
        <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono">{prompt.content}</pre>
      </div>

      {/* AI Output */}
      {(aiOutput || aiError) && (
        <div className={`border rounded-lg p-4 mb-6 ${aiError ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' : 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'}`}>
          <div className="flex items-center justify-between mb-2">
            <span className={`text-xs font-medium uppercase tracking-wider ${aiError ? 'text-red-500' : 'text-green-600 dark:text-green-400'}`}>
              {aiError ? 'Error' : `AI Output (${aiOutput.model})`}
            </span>
            {aiOutput && (
              <button
                onClick={() => { navigator.clipboard.writeText(aiOutput.output); }}
                className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                Copy
              </button>
            )}
          </div>
          <pre className={`text-sm whitespace-pre-wrap font-mono ${aiError ? 'text-red-700 dark:text-red-300' : 'text-gray-800 dark:text-gray-200'}`}>
            {aiError || aiOutput.output}
          </pre>
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Tags</h3>
        <div className="flex flex-wrap gap-1.5 mb-3">
          {tags.length === 0 && <span className="text-sm text-gray-400">No tags</span>}
          {tags.map((tag) => (
            <TagBadge key={tag.id} tag={tag} onRemove={() => onRemoveTag(tag.id)} />
          ))}
        </div>
        <form onSubmit={handleAddTag} className="flex gap-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            placeholder="Add tag (3-50 chars, a-z, 0-9, -, _)"
            className="flex-1 px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <Button size="sm" type="submit" disabled={!tagInput.trim()}>Add</Button>
        </form>
      </div>

      <div className="text-xs text-gray-400 space-y-1">
        <p>Created: {new Date(prompt.created_at).toLocaleString()}</p>
        <p>Updated: {new Date(prompt.updated_at).toLocaleString()}</p>
      </div>

      <ConfirmDialog
        isOpen={showDelete}
        onConfirm={handleDelete}
        onCancel={() => setShowDelete(false)}
        title="Delete Prompt"
        message="Are you sure you want to delete this prompt? This action cannot be undone."
        loading={deleting}
      />
    </div>
  );
}
