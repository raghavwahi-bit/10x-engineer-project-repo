import { api } from './client';

export function getPrompts({ collectionId, search, tags } = {}) {
  const params = new URLSearchParams();
  if (collectionId) params.set('collection_id', collectionId);
  if (search) params.set('search', search);
  if (tags) params.set('tags', tags);
  const qs = params.toString();
  return api.get(`/prompts${qs ? `?${qs}` : ''}`);
}

export function getPrompt(id) {
  return api.get(`/prompts/${id}`);
}

export function createPrompt(data) {
  return api.post('/prompts', data);
}

export function updatePrompt(id, data) {
  return api.put(`/prompts/${id}`, data);
}

export function patchPrompt(id, data) {
  return api.patch(`/prompts/${id}`, data);
}

export function deletePrompt(id) {
  return api.del(`/prompts/${id}`);
}

export function getPromptTags(id) {
  return api.get(`/prompts/${id}/tags`);
}

export function addTagsToPrompt(id, tagNames) {
  return api.post(`/prompts/${id}/tags`, { tag_names: tagNames });
}

export function removeTagFromPrompt(promptId, tagId) {
  return api.del(`/prompts/${promptId}/tags/${tagId}`);
}

export function runPrompt(id, variables = null) {
  return api.post(`/prompts/${id}/run`, { variables });
}
