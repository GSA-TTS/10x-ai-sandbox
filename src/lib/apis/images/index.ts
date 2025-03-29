import { IMAGES_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getConfig = async () => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/config`, { method: 'GET' });
};

export const updateConfig = async (config: object) => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/config/update`, {
		method: 'POST',
		body: JSON.stringify({
			...config
		})
	});
};

export const verifyConfigUrl = async () => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/config/url/verify`, { method: 'GET' });
};

export const getImageGenerationConfig = async () => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/image/config`, { method: 'GET' });
};

export const updateImageGenerationConfig = async (config: object) => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/image/config/update`, {
		method: 'POST',
		body: JSON.stringify({ ...config })
	});
};

export const getImageGenerationModels = async () => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/models`, { method: 'GET' });
};

export const imageGenerations = async (prompt: string) => {
	return await apiFetch(`${IMAGES_API_BASE_URL}/generations`, {
		method: 'POST',
		body: JSON.stringify({
			prompt: prompt
		})
	});
};
