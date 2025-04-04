import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';
import { t } from 'i18next';

type ChannelForm = {
	name: string;
	data?: object;
	meta?: object;
	access_control?: object;
};

export const createNewChannel = async (channel: ChannelForm) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/channels/create`, {
		method: 'POST',
		body: JSON.stringify({ ...channel })
	});
};

export const getChannels = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/channels/`, { method: 'GET' });
};

export const getChannelById = async (channel_id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/channels/${channel_id}`, { method: 'GET' });
};

export const updateChannelById = async (channel_id: string, channel: ChannelForm) => {
	return apiFetch(`${WEBUI_API_BASE_URL}/channels/${channel_id}/update`, {
		method: 'POST',
		body: JSON.stringify({ ...channel })
	});
};

export const deleteChannelById = async (channel_id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/channels/${channel_id}/delete`, {
		method: 'DELETE'
	});
};

export const getChannelMessages = async (
	channel_id: string,
	skip: number = 0,
	limit: number = 50
) => {
	return await apiFetch(
		`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages?skip=${skip}&limit=${limit}`,
		{
			method: 'GET'
		}
	);
};

export const getChannelThreadMessages = async (
	channel_id: string,
	message_id: string,
	skip: number = 0,
	limit: number = 50
) => {
	return await apiFetch(
		`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages/${message_id}/thread?skip=${skip}&limit=${limit}`,
		{
			method: 'GET'
		}
	);
};

type MessageForm = {
	parent_id?: string;
	content: string;
	data?: object;
	meta?: object;
};

export const sendMessage = async (channel_id: string, message: MessageForm) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages/post`, {
		method: 'POST',
		body: JSON.stringify({ ...message })
	});
};

export const updateMessage = async (
	channel_id: string,
	message_id: string,
	message: MessageForm
) => {
	return await apiFetch(
		`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages/${message_id}/update`,
		{
			method: 'POST',
			body: JSON.stringify({ ...message })
		}
	);
};

export const addReaction = async (channel_id: string, message_id: string, name: string) => {
	return await apiFetch(
		`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages/${message_id}/reactions/add`,
		{
			method: 'POST',
			body: JSON.stringify({ name })
		}
	);
};

export const removeReaction = async (channel_id: string, message_id: string, name: string) => {
	return await apiFetch(
		`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages/${message_id}/reactions/remove`,
		{
			method: 'POST',
			body: JSON.stringify({ name })
		}
	);
};

export const deleteMessage = async (channel_id: string, message_id: string) => {
	return await apiFetch(
		`${WEBUI_API_BASE_URL}/channels/${channel_id}/messages/${message_id}/delete`,
		{
			method: 'DELETE'
		}
	);
};
