import { useState, useEffect, useCallback } from 'react';
import * as promptsApi from '../api/prompts';

export default function usePrompts(filters = {}) {
  const [prompts, setPrompts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPrompts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await promptsApi.getPrompts(filters);
      setPrompts(data.prompts);
      setTotal(data.total);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters.collectionId, filters.search, filters.tags]);

  useEffect(() => { fetchPrompts(); }, [fetchPrompts]);

  const remove = async (id) => {
    await promptsApi.deletePrompt(id);
    await fetchPrompts();
  };

  return { prompts, total, loading, error, refetch: fetchPrompts, remove };
}
