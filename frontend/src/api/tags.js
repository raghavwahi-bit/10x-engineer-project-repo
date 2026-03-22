import { api } from './client';

export function getTags() {
  return api.get('/tags');
}

export function createTag(data) {
  return api.post('/tags', data);
}

export function deleteTag(id) {
  return api.del(`/tags/${id}`);
}
