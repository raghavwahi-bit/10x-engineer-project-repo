import { useNavigate, useOutletContext } from 'react-router-dom';
import usePrompts from '../hooks/usePrompts';
import PromptList from '../features/prompts/PromptList';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { search, collectionId } = useOutletContext();
  const { prompts, loading, error, refetch, remove } = usePrompts({
    collectionId,
    search,
  });

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          {collectionId ? 'Collection Prompts' : 'All Prompts'}
        </h2>
        {search && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Showing results for &ldquo;{search}&rdquo;</p>}
      </div>

      <PromptList
        prompts={prompts}
        loading={loading}
        error={error}
        onRetry={refetch}
        onDelete={remove}
        onCreateNew={() => navigate('/prompts/new')}
      />
    </div>
  );
}
