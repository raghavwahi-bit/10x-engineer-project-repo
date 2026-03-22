import { api } from './client';

export function getCollections() {
  return api.get('/collections');
}

export function getCollection(id) {
  return api.get(`/collections/${id}`);
}

export function createCollection(data) {
  return api.post('/collections', data);
}

export function deleteCollection(id) {
  return api.del(`/collections/${id}`);
}
