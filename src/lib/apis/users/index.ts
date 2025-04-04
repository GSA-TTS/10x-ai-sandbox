import { WEBUI_API_BASE_URL } from '$lib/constants';
import { getUserPosition } from '$lib/utils';
import { apiFetch } from '$lib/utils/apiClient';

export const getUserGroups = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/groups`, {
		method: 'GET'
	});
};

export const getUserDefaultPermissions = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/default/permissions`, {
		method: 'GET'
	});
};

export const updateUserDefaultPermissions = async (permissions: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/default/permissions`, {
		method: 'POST',
		body: JSON.stringify({
			...permissions
		})
	});
};

export const updateUserRole = async (id: string, role: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/update/role`, {
		method: 'POST',
		body: JSON.stringify({
			id: id,
			role: role
		})
	});
};

export const searchUsers = async (query: string) => {
	const res = await apiFetch(`${WEBUI_API_BASE_URL}/users/search?q=${query}&limit=1000`, {
		method: 'GET'
	});

	return res ? res : [];
};

export const getUsers = async (limit?: number) => {
	let url = `${WEBUI_API_BASE_URL}/users/`;
	if (limit) url = url + `?limit=${limit}`;

	const res = await apiFetch(url, { method: 'GET' });

	return res ? res : [];
};

export const getUserSettings = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/user/settings`, { method: 'GET' });
};

export const updateUserSettings = async (settings: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/user/settings/update`, {
		method: 'POST',
		body: JSON.stringify({
			...settings
		})
	});
};

export const getUserById = async (userId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/${userId}`, {
		method: 'GET'
	});
};

export const getUserInfo = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/user/info`, {
		method: 'GET'
	});
};

export const updateUserInfo = async (info: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/user/info/update`, {
		method: 'POST',
		body: JSON.stringify({
			...info
		})
	});
};

export const getAndUpdateUserLocation = async () => {
	const location = await getUserPosition().catch((err) => {
		throw err;
	});

	if (location) {
		await updateUserInfo({ location: location });
		return location;
	} else {
		throw new Error('Failed to get user location');
	}
};

export const deleteUserById = async (userId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/${userId}`, {
		method: 'DELETE'
	});
};

type UserUpdateForm = {
	profile_image_url: string;
	email: string;
	name: string;
	password: string;
};

export const updateUserById = async (userId: string, user: UserUpdateForm) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/${userId}/update`, {
		method: 'POST',
		body: JSON.stringify({
			profile_image_url: user.profile_image_url,
			email: user.email,
			name: user.name,
			password: user.password !== '' ? user.password : undefined
		})
	});
};

export const getTotalUserCount = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/users/count`, {
		method: 'GET'
	});
};
