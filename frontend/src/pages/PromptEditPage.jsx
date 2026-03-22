import { useParams, Link } from 'react-router-dom';
import usePromptDetail from '../hooks/usePromptDetail';
import PromptForm from '../features/prompts/PromptForm';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function PromptEditPage() {
  const { id } = useParams();
  const { prompt, tags, loading, error, refetch } = usePromptDetail(id);

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
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Edit Prompt</h2>
      <PromptForm initialData={prompt} initialTags={tags} promptId={id} />
    </div>
  );
}
