import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getMemories = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/memories/`, { method: 'GET' });
};

export const addNewMemory = async (content: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/memories/add`, {
		method: 'POST',
		body: JSON.stringify({
			content: content
		})
	});
};

export const updateMemoryById = async (id: string, content: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/memories/${id}/update`, {
		method: 'POST',
		body: JSON.stringify({
			content: content
		})
	});
};

export const queryMemory = async (content: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/memories/query`, {
		method: 'POST',
		body: JSON.stringify({
			content: content
		})
	});
};

export const deleteMemoryById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/memories/${id}`, { method: 'DELETE' });
};

export const deleteMemoriesByUserId = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/memories/delete/user`, { method: 'DELETE' });
};
