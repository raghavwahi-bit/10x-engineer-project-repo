import { useParams, useOutletContext, Link } from 'react-router-dom';
import usePromptDetail from '../hooks/usePromptDetail';
import PromptDetail from '../features/prompts/PromptDetail';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function PromptDetailPage() {
  const { id } = useParams();
  const { collections } = useOutletContext();
  const { prompt, tags, loading, error, refetch, addTags, removeTag } = usePromptDetail(id);

  if (loading) return <LoadingSpinner message="Loading prompt..." />;
  if (error) {
    return (
      <div>
        <ErrorMessage message={error} onRetry={refetch} />
        <Link to="/" className="inline-block mt-4 text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Back to dashboard</Link>
      </div>
    );
  }
  if (!prompt) return null;

  return (
    <div>
      <Link to="/" className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline mb-4 inline-block">&larr; Back</Link>
      <PromptDetail
        prompt={prompt}
        tags={tags}
        onAddTags={addTags}
        onRemoveTag={removeTag}
        collections={collections}
      />
    </div>
  );
}
