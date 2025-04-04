import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const createNewTool = async (tool: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/create`, {
		method: 'POST',
		body: JSON.stringify({
			...tool
		})
	});
};

export const getTools = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/`, { method: 'GET' });
};

export const getToolList = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/list`, { method: 'GET' });
};

export const exportTools = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/export`, { method: 'GET' });
};

export const getToolById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}`, { method: 'GET' });
};

export const updateToolById = async (id: string, tool: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/update`, {
		method: 'POST',
		body: JSON.stringify({
			...tool
		})
	});
};

export const deleteToolById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/delete`, { method: 'DELETE' });
};

export const getToolValvesById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/valves`, { method: 'GET' });
};

export const getToolValvesSpecById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/valves/spec`, { method: 'GET' });
};

export const updateToolValvesById = async (id: string, valves: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/valves/update`, {
		method: 'POST',
		body: JSON.stringify({
			...valves
		})
	});
};

export const getUserValvesById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/valves/user`, { method: 'GET' });
};

export const getUserValvesSpecById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/valves/user/spec`, { method: 'GET' });
};

export const updateUserValvesById = async (id: string, valves: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/tools/id/${id}/valves/user/update`, {
		method: 'POST',
		body: JSON.stringify({
			...valves
		})
	});
};
