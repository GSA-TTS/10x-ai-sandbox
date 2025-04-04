import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const uploadFile = async (file: File) => {
	const data = new FormData();
	data.append('file', file);
	console.log('data: ', file);
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/`, {
		method: 'POST',
		body: data
	});
};

export const uploadDir = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/upload/dir`, { method: 'POST' });
};

export const getFiles = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/`, { method: 'GET' });
};

export const getFileById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/${id}`, { method: 'GET' });
};

export const updateFileDataContentById = async (id: string, content: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/${id}/data/content/update`, {
		method: 'POST',
		body: JSON.stringify({
			content: content
		})
	});
};

export const getFileContentById = async (id: string) => {
	const res = await apiFetch<Response>(
		`${WEBUI_API_BASE_URL}/files/${id}/content`,
		{
			method: 'GET'
		},
		false
	).then(async (res) => res.blob());
};

export const deleteFileById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/${id}`, { method: 'DELETE' });
};

export const deleteAllFiles = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/files/all`, { method: 'DELETE' });
};
