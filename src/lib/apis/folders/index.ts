import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const createNewFolder = async (name: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/`, {
		method: 'POST',
		body: JSON.stringify({
			name: name
		})
	});
};

export const getFolders = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/`, { method: 'GET' });
};

export const getFolderById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/${id}`, { method: 'GET' });
};

export const updateFolderNameById = async (id: string, name: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/${id}/update`, {
		method: 'POST',
		body: JSON.stringify({
			name: name
		})
	});
};

export const updateFolderIsExpandedById = async (id: string, isExpanded: boolean) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/${id}/update/expanded`, {
		method: 'POST',
		body: JSON.stringify({
			is_expanded: isExpanded
		})
	});
};

export const updateFolderParentIdById = async (id: string, parentId?: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/${id}/update/parent`, {
		method: 'POST',
		body: JSON.stringify({
			parent_id: parentId
		})
	});
};

type FolderItems = {
	chat_ids: string[];
	file_ids: string[];
};

export const updateFolderItemsById = async (id: string, items: FolderItems) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/${id}/update/items`, {
		method: 'POST',
		body: JSON.stringify({
			items: items
		})
	});
};

export const deleteFolderById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/folders/${id}`, { method: 'DELETE' });
};
