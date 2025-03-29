import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const createNewKnowledge = async (
	name: string,
	description: string,
	accessControl: null | object
) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/create`, {
		method: 'POST',
		body: JSON.stringify({
			name: name,
			description: description,
			access_control: accessControl
		})
	});
};

export const getKnowledgeBases = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/`, { method: 'GET' });
};

export const getKnowledgeBaseList = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/list`, { method: 'GET' });
};

export const getKnowledgeById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}`, { method: 'GET' });
};

type KnowledgeUpdateForm = {
	name?: string;
	description?: string;
	data?: object;
	access_control?: null | object;
};

export const updateKnowledgeById = async (id: string, form: KnowledgeUpdateForm) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}/update`, {
		method: 'POST',
		body: JSON.stringify({
			name: form?.name ? form.name : undefined,
			description: form?.description ? form.description : undefined,
			data: form?.data ? form.data : undefined,
			access_control: form.access_control
		})
	});
};

export const addFileToKnowledgeById = async (id: string, fileId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}/file/add`, {
		method: 'POST',
		body: JSON.stringify({
			file_id: fileId
		})
	});
};

export const updateFileFromKnowledgeById = async (id: string, fileId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}/file/update`, {
		method: 'POST',
		body: JSON.stringify({
			file_id: fileId
		})
	});
};

export const removeFileFromKnowledgeById = async (id: string, fileId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}/file/remove`, {
		method: 'POST',
		body: JSON.stringify({
			file_id: fileId
		})
	});
};

export const resetKnowledgeById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}/reset`, {
		method: 'POST'
	});
};

export const deleteKnowledgeById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/knowledge/${id}/delete`, {
		method: 'DELETE'
	});
};
