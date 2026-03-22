import { useState, useEffect, useCallback } from 'react';
import * as promptsApi from '../api/prompts';

export default function usePromptDetail(id) {
  const [prompt, setPrompt] = useState(null);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPrompt = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [promptData, tagsData] = await Promise.all([
        promptsApi.getPrompt(id),
        promptsApi.getPromptTags(id),
      ]);
      setPrompt(promptData);
      setTags(tagsData.tags);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchPrompt(); }, [fetchPrompt]);

  const addTags = async (tagNames) => {
    await promptsApi.addTagsToPrompt(id, tagNames);
    const tagsData = await promptsApi.getPromptTags(id);
    setTags(tagsData.tags);
  };

  const removeTag = async (tagId) => {
    await promptsApi.removeTagFromPrompt(id, tagId);
    const tagsData = await promptsApi.getPromptTags(id);
    setTags(tagsData.tags);
  };

  return { prompt, tags, loading, error, refetch: fetchPrompt, addTags, removeTag };
}
