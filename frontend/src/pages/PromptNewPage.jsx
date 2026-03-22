import PromptForm from '../features/prompts/PromptForm';

export default function PromptNewPage() {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Create New Prompt</h2>
      <PromptForm />
    </div>
  );
}
