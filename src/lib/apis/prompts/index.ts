import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

type PromptItem = {
	command: string;
	title: string;
	content: string;
	access_control?: null | object;
};

export const createNewPrompt = async (prompt: PromptItem) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/prompts/create`, {
		method: 'POST',
		body: JSON.stringify({
			...prompt,
			command: `/${prompt.command}`
		})
	});
};

export const getPrompts = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/prompts/`, { method: 'GET' });
};

export const getPromptList = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/prompts/list`, { method: 'GET' });
};

export const getPromptByCommand = async (command: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/prompts/command/${command}`, { method: 'GET' });
};

export const updatePromptByCommand = async (prompt: PromptItem) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/prompts/command/${prompt.command}/update`, {
		method: 'POST',
		body: JSON.stringify({
			...prompt,
			command: `/${prompt.command}`
		})
	});
};

export const deletePromptByCommand = async (command: string) => {
	command = command.charAt(0) === '/' ? command.slice(1) : command;

	return await apiFetch(`${WEBUI_API_BASE_URL}/prompts/command/${command}/delete`, {
		method: 'DELETE'
	});
};
