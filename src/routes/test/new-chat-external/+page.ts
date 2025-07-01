import type { PageLoad } from './$types';
import { apiFetch } from '$lib/utils/apiClient';

export const load: PageLoad = async () => {
	const models = await apiFetch('/api/models', { method: 'GET' });
	return { models: models.data };
};
