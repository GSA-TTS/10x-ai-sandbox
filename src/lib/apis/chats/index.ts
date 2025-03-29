import { WEBUI_API_BASE_URL } from '$lib/constants';
import { getTimeRange } from '$lib/utils';
import { apiFetch } from '$lib/utils/apiClient';

export const createNewChat = async (chat: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/new`, {
		method: 'POST',
		body: JSON.stringify({
			chat: chat
		})
	});
};

export const importChat = async (
	chat: object,
	meta: object | null,
	pinned?: boolean,
	folderId?: string | null
) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/import`, {
		method: 'POST',
		body: JSON.stringify({
			chat: chat,
			meta: meta ?? {},
			pinned: pinned,
			folder_id: folderId
		})
	});
};

export const getChatList = async (page: number | null = null) => {
	const searchParams = new URLSearchParams();

	if (page !== null) {
		searchParams.append('page', `${page}`);
	}

	const res = await apiFetch<any[]>(`${WEBUI_API_BASE_URL}/chats/?${searchParams.toString()}`, {
		method: 'GET'
	});

	return res.map((chat) => ({
		...chat,
		time_range: getTimeRange(chat.updated_at)
	}));
};

export const getChatListByUserId = async (userId: string) => {
	const res = await apiFetch<any[]>(`${WEBUI_API_BASE_URL}/chats/list/user/${userId}`, {
		method: 'GET'
	});

	return res.map((chat) => ({
		...chat,
		time_range: getTimeRange(chat.updated_at)
	}));
};

export const getArchivedChatList = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/archived`, { method: 'GET' });
};

export const getAllChats = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/all`, { method: 'GET' });
};

export const getChatListBySearchText = async (text: string, page: number = 1) => {
	const searchParams = new URLSearchParams();
	searchParams.append('text', text);
	searchParams.append('page', `${page}`);

	const res = await apiFetch<any[]>(
		`${WEBUI_API_BASE_URL}/chats/search?${searchParams.toString()}`,
		{
			method: 'GET'
		}
	);

	return res.map((chat) => ({
		...chat,
		time_range: getTimeRange(chat.updated_at)
	}));
};

export const getChatsByFolderId = async (folderId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/folder/${folderId}`, { method: 'GET' });
};

export const getAllArchivedChats = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/all/archived`, { method: 'GET' });
};

export const getAllUserChats = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/all/db`, { method: 'GET' });
};

export const getAllTags = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/all/tags`, { method: 'GET' });
};

export const getPinnedChatList = async () => {
	const res = await apiFetch<any[]>(`${WEBUI_API_BASE_URL}/chats/pinned`, { method: 'GET' });

	return res.map((chat) => ({
		...chat,
		time_range: getTimeRange(chat.updated_at)
	}));
};

export const getChatListByTagName = async (tagName: string) => {
	const res = await apiFetch<any[]>(`${WEBUI_API_BASE_URL}/chats/tags`, {
		method: 'POST',
		body: JSON.stringify({
			name: tagName
		})
	});
	return res.map((chat) => ({
		...chat,
		time_range: getTimeRange(chat.updated_at)
	}));
};

export const getChatById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}`, { method: 'GET' });
};

export const getChatByShareId = async (share_id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/share/${share_id}`, { method: 'GET' });
};

export const getChatPinnedStatusById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/pinned`, { method: 'GET' });
};

export const toggleChatPinnedStatusById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/pin`, { method: 'POST' });
};

export const cloneChatById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/clone`, { method: 'POST' });
};

export const shareChatById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/share`, { method: 'POST' });
};

export const updateChatFolderIdById = async (id: string, folderId?: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/folder`, {
		method: 'POST',
		body: JSON.stringify({
			folder_id: folderId
		})
	});
};

export const archiveChatById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/archive`, { method: 'POST' });
};

export const deleteSharedChatById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/share`, { method: 'DELETE' });
};

export const updateChatById = async (id: string, chat: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}`, {
		method: 'POST',
		body: JSON.stringify({
			chat: chat
		})
	});
};

export const deleteChatById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}`, { method: 'DELETE' });
};

export const getTagsById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/tags`, { method: 'GET' });
};

export const addTagById = async (id: string, tagName: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/tags`, {
		method: 'POST',
		body: JSON.stringify({
			name: tagName
		})
	});
};

export const deleteTagById = async (id: string, tagName: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/tags`, {
		method: 'DELETE',
		body: JSON.stringify({
			name: tagName
		})
	});
};
export const deleteTagsById = async (id: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/${id}/tags/all`, { method: 'DELETE' });
};

export const deleteAllChats = async () => {
	return apiFetch(`${WEBUI_API_BASE_URL}/chats/`, { method: 'DELETE' });
};

export const archiveAllChats = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/chats/archive/all`, { method: 'POST' });
};
