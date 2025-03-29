import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getModels = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/models/`, { method: 'GET' });
};

export const getBaseModels = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/models/base`, { method: 'GET' });
};

export const createNewModel = async (model: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/models/create`, {
		method: 'POST',
		body: JSON.stringify(model)
	});
};

export const getModelById = async (id: string) => {
	const searchParams = new URLSearchParams();
	searchParams.append('id', id);

	return await apiFetch(`${WEBUI_API_BASE_URL}/models/model?${searchParams.toString()}`, {
		method: 'GET'
	});
};

export const toggleModelById = async (id: string) => {
	const searchParams = new URLSearchParams();
	searchParams.append('id', id);

	return await apiFetch(`${WEBUI_API_BASE_URL}/models/model/toggle?${searchParams.toString()}`, {
		method: 'POST'
	});
};

export const updateModelById = async (id: string, model: object) => {
	const searchParams = new URLSearchParams();
	searchParams.append('id', id);

	return await apiFetch(`${WEBUI_API_BASE_URL}/models/model/update?${searchParams.toString()}`, {
		method: 'POST',
		body: JSON.stringify(model)
	});
};

export const deleteModelById = async (id: string) => {
	const searchParams = new URLSearchParams();
	searchParams.append('id', id);

	return await apiFetch(`${WEBUI_API_BASE_URL}/models/model/delete?${searchParams.toString()}`, {
		method: 'DELETE'
	});
};

export const deleteAllModels = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/models/delete/all`, { method: 'DELETE' });
};
