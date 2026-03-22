import { useState, useEffect, useCallback } from 'react';
import * as tagsApi from '../api/tags';

export default function useTags() {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTags = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await tagsApi.getTags();
      setTags(data.tags);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTags(); }, [fetchTags]);

  const create = async (data) => {
    const result = await tagsApi.createTag(data);
    await fetchTags();
    return result;
  };

  const remove = async (id) => {
    await tagsApi.deleteTag(id);
    await fetchTags();
  };

  return { tags, loading, error, refetch: fetchTags, create, remove };
}
