import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';
import type { Banner } from '$lib/types';

export const importConfig = async (config: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/import`, {
		method: 'POST',
		body: JSON.stringify({
			config: config
		})
	});
};

export const exportConfig = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/export`, { method: 'GET' });
};

export const getModelsConfig = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/models`, { method: 'GET' });
};

export const setModelsConfig = async (config: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/models`, {
		method: 'POST',
		body: JSON.stringify({
			...config
		})
	});
};

export const setDefaultPromptSuggestions = async (promptSuggestions: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/suggestions`, {
		method: 'POST',
		body: JSON.stringify({
			suggestions: promptSuggestions
		})
	});
};

export const getBanners = async (): Promise<Banner[]> => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/banners`, { method: 'GET' });
};

export const setBanners = async (banners: Banner[]) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/configs/banners`, {
		method: 'POST',
		body: JSON.stringify({
			banners: banners
		})
	});
};
