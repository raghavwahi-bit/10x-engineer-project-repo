import { useState, useEffect, useCallback } from 'react';
import * as collectionsApi from '../api/collections';

export default function useCollections() {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCollections = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await collectionsApi.getCollections();
      setCollections(data.collections);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchCollections(); }, [fetchCollections]);

  const create = async (data) => {
    const result = await collectionsApi.createCollection(data);
    await fetchCollections();
    return result;
  };

  const remove = async (id) => {
    await collectionsApi.deleteCollection(id);
    await fetchCollections();
  };

  return { collections, loading, error, refetch: fetchCollections, create, remove };
}
