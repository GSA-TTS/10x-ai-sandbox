import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const createNewGroup = async (group: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/groups/create`, {
		method: 'POST',
		body: JSON.stringify({
			...group
		})
	});
};

export const getGroups = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/groups/`, { method: 'GET' });
};

export const getGroupById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/groups/id/${id}`, { method: 'GET' });
};

export const updateGroupById = async (id: string, group: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/groups/id/${id}/update`, {
		method: 'POST',
		body: JSON.stringify({
			...group
		})
	});
};

export const deleteGroupById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/groups/id/${id}/delete`, {
		method: 'DELETE'
	});
};
