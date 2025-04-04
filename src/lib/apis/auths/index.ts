import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getAdminDetails = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/details`, { method: 'GET' });
};

export const getAdminConfig = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/config`, { method: 'GET' });
};

export const updateAdminConfig = async (body: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/config`, {
		method: 'POST',
		body: JSON.stringify(body)
	});
};

export const getSessionUser = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/`, { method: 'GET' });
};

export const ldapUserSignIn = async (user: string, password: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/ldap`, {
		method: 'POST',
		body: JSON.stringify({
			user: user,
			password: password
		})
	});
};

export const getLdapConfig = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/config/ldap`, { method: 'GET' });
};

export const updateLdapConfig = async (enable_ldap: boolean) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/config/ldap`, {
		method: 'POST',
		body: JSON.stringify({
			enable_ldap: enable_ldap
		})
	});
};

export const getLdapServer = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/config/ldap/server`, { method: 'GET' });
};

export const updateLdapServer = async (body: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/admin/config/ldap/server`, {
		method: 'POST',
		body: JSON.stringify(body)
	});
};

export const userSignIn = async (email: string, password: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signin`, {
		method: 'POST',
		body: JSON.stringify({
			email: email,
			password: password
		})
	});
};

export const userSignUp = async (
	name: string,
	email: string,
	password: string,
	profile_image_url: string
) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signup`, {
		method: 'POST',
		body: JSON.stringify({
			name: name,
			email: email,
			password: password,
			profile_image_url: profile_image_url
		})
	});
};

export const userSignOut = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signout`, { method: 'GET' });
};

export const addUser = async (
	name: string,
	email: string,
	password: string,
	role: string = 'pending'
) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/add`, {
		method: 'POST',
		body: JSON.stringify({
			name: name,
			email: email,
			password: password,
			role: role
		})
	});
};

export const updateUserProfile = async (name: string, profileImageUrl: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/update/profile`, {
		method: 'POST',
		body: JSON.stringify({
			name: name,
			profile_image_url: profileImageUrl
		})
	});
};

export const updateUserPassword = async (password: string, newPassword: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/update/password`, {
		method: 'POST',
		body: JSON.stringify({
			password: password,
			new_password: newPassword
		})
	});
};

export const getSignUpEnabledStatus = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signup/enabled`, { method: 'GET' });
};

export const getDefaultUserRole = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signup/user/role`, { method: 'GET' });
};

export const updateDefaultUserRole = async (role: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signup/user/role`, {
		method: 'POST',
		body: JSON.stringify({
			role: role
		})
	});
};

export const toggleSignUpEnabledStatus = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/signup/enabled/toggle`, { method: 'GET' });
};

export const getJWTExpiresDuration = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/token/expires`, { method: 'GET' });
};

export const updateJWTExpiresDuration = async (duration: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/token/expires/update`, {
		method: 'POST',
		body: JSON.stringify({
			duration: duration
		})
	});
};

interface ApiKeyResult {
	api_key: string;
}

export const createAPIKey = async () => {
	const res = await apiFetch<ApiKeyResult>(`${WEBUI_API_BASE_URL}/auths/api_key`, {
		method: 'POST'
	});
	return res.api_key;
};

export const getAPIKey = async () => {
	const res = await apiFetch<ApiKeyResult>(`${WEBUI_API_BASE_URL}/auths/api_key`, {
		method: 'GET'
	});
	return res.api_key;
};

export const deleteAPIKey = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/auths/api_key`, { method: 'DELETE' });
};
