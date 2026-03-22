import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import TagSelector from '../tags/TagSelector';
import useCollections from '../../hooks/useCollections';
import { createPrompt, updatePrompt, addTagsToPrompt } from '../../api/prompts';

export default function PromptForm({ initialData, initialTags = [], promptId }) {
  const navigate = useNavigate();
  const { collections } = useCollections();
  const isEdit = !!promptId;

  const [form, setForm] = useState({
    title: '',
    content: '',
    description: '',
    collection_id: '',
  });
  const [selectedTags, setSelectedTags] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    if (initialData) {
      setForm({
        title: initialData.title || '',
        content: initialData.content || '',
        description: initialData.description || '',
        collection_id: initialData.collection_id || '',
      });
    }
  }, [initialData]);

  useEffect(() => {
    if (initialTags.length) setSelectedTags(initialTags);
  }, [initialTags]);

  const validate = () => {
    const errs = {};
    if (!form.title.trim()) errs.title = 'Title is required';
    else if (form.title.length > 200) errs.title = 'Title must be 200 characters or less';
    if (!form.content.trim()) errs.content = 'Content is required';
    if (form.description.length > 500) errs.description = 'Description must be 500 characters or less';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setSubmitError(null);
    try {
      const payload = {
        title: form.title.trim(),
        content: form.content.trim(),
        description: form.description.trim() || null,
        collection_id: form.collection_id || null,
      };

      let result;
      if (isEdit) {
        result = await updatePrompt(promptId, payload);
      } else {
        result = await createPrompt(payload);
      }

      const newTagNames = selectedTags.filter((t) => t.isNew).map((t) => t.name);
      const existingTagNames = selectedTags.filter((t) => !t.isNew).map((t) => t.name);
      const allTagNames = [...existingTagNames, ...newTagNames];
      if (allTagNames.length > 0) {
        await addTagsToPrompt(result.id, allTagNames);
      }

      navigate(`/prompts/${result.id}`);
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const inputClass = (hasError) =>
    `w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 ${
      hasError ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
    }`;

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-5">
      {submitError && <div className="rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 text-sm text-red-700 dark:text-red-300">{submitError}</div>}

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title *</label>
        <input type="text" value={form.title} onChange={handleChange('title')} maxLength={200} className={inputClass(errors.title)} />
        <div className="flex justify-between mt-1">
          {errors.title && <p className="text-xs text-red-600 dark:text-red-400">{errors.title}</p>}
          <p className="text-xs text-gray-400 ml-auto">{form.title.length}/200</p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content *</label>
        <textarea value={form.content} onChange={handleChange('content')} rows={8} className={`${inputClass(errors.content)} font-mono`} />
        {errors.content && <p className="text-xs text-red-600 dark:text-red-400 mt-1">{errors.content}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
        <textarea value={form.description} onChange={handleChange('description')} rows={3} maxLength={500} className={inputClass(errors.description)} />
        <div className="flex justify-between mt-1">
          {errors.description && <p className="text-xs text-red-600 dark:text-red-400">{errors.description}</p>}
          <p className="text-xs text-gray-400 ml-auto">{form.description.length}/500</p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Collection</label>
        <select value={form.collection_id} onChange={handleChange('collection_id')} className={inputClass(false)}>
          <option value="">None</option>
          {collections.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tags</label>
        <TagSelector
          selectedTags={selectedTags}
          onAdd={(tag) => setSelectedTags((prev) => [...prev, tag])}
          onRemove={(tag) => setSelectedTags((prev) => prev.filter((t) => (t.id || t.name) !== (tag.id || tag.name)))}
        />
      </div>

      <div className="flex gap-3 pt-2">
        <Button type="submit" loading={loading}>{isEdit ? 'Update Prompt' : 'Create Prompt'}</Button>
        <Button variant="secondary" type="button" onClick={() => navigate(-1)}>Cancel</Button>
      </div>
    </form>
  );
}
