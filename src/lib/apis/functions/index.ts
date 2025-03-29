import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const createNewFunction = async (func: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/create`, {
		method: 'POST',
		body: JSON.stringify({
			...func
		})
	});
};

export const getFunctions = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/`, { method: 'GET' });
};

export const exportFunctions = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/export`, { method: 'GET' });
};

export const getFunctionById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}`, { method: 'GET' });
};

export const updateFunctionById = async (id: string, func: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/update`, {
		method: 'POST',
		body: JSON.stringify({
			...func
		})
	});
};

export const deleteFunctionById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/delete`, { method: 'DELETE' });
};

export const toggleFunctionById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/toggle`, {
		method: 'POST'
	});
};

export const toggleGlobalById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/toggle/global`, {
		method: 'POST'
	});
};

export const getFunctionValvesById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/valves`, {
		method: 'GET'
	});
};

export const getFunctionValvesSpecById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/valves/spec`, {
		method: 'GET'
	});
};

export const updateFunctionValvesById = async (id: string, valves: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/valves/update`, {
		method: 'POST',
		body: JSON.stringify({
			...valves
		})
	});
};

export const getUserValvesById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/valves/user`, {
		method: 'GET'
	});
};

export const getUserValvesSpecById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/valves/user/spec`, {
		method: 'GET'
	});
};

export const updateUserValvesById = async (id: string, valves: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/functions/id/${id}/valves/user/update`, {
		method: 'POST',
		body: JSON.stringify({
			...valves
		})
	});
};
