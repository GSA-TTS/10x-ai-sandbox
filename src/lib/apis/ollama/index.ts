import { OLLAMA_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const verifyOllamaConnection = async (url: string = '', key: string = '') => {
	return await apiFetch(`${OLLAMA_API_BASE_URL}/verify`, {
		method: 'POST',
		body: JSON.stringify({
			url,
			key
		})
	});
};

export const getOllamaConfig = async () => {
	return await apiFetch(`${OLLAMA_API_BASE_URL}/config`, { method: 'GET' });
};

type OllamaConfig = {
	ENABLE_OLLAMA_API: boolean;
	OLLAMA_BASE_URLS: string[];
	OLLAMA_API_CONFIGS: object;
};

export const updateOllamaConfig = async (config: OllamaConfig) => {
	return await apiFetch(`${OLLAMA_API_BASE_URL}/config/update`, {
		method: 'POST',
		body: JSON.stringify({
			...config
		})
	});
};

interface OllamaUrlResult {
	OLLAMA_BASE_URLS: any;
}

export const getOllamaUrls = async () => {
	const res = await apiFetch<OllamaUrlResult>(`${OLLAMA_API_BASE_URL}/urls`, { method: 'GET' });

	return res.OLLAMA_BASE_URLS;
};

export const updateOllamaUrls = async (urls: string[]) => {
	const res = await apiFetch<OllamaUrlResult>(`${OLLAMA_API_BASE_URL}/urls/update`, {
		method: 'POST',
		body: JSON.stringify({
			urls: urls
		})
	});

	return res.OLLAMA_BASE_URLS;
};

interface OllamaVersionResult {
	version: number;
}

export const getOllamaVersion = async (urlIdx?: number) => {
	const res = await apiFetch<OllamaVersionResult>(
		`${OLLAMA_API_BASE_URL}/api/version${urlIdx ? `/${urlIdx}` : ''}`,
		{
			method: 'GET'
		}
	);
	return res?.version ?? false;
};

interface OllamaModelsResult {
	models: any[];
}

export const getOllamaModels = async (urlIdx: null | number = null) => {
	const res = await apiFetch<OllamaModelsResult>(
		`${OLLAMA_API_BASE_URL}/api/tags${urlIdx !== null ? `/${urlIdx}` : ''}`,
		{
			method: 'GET'
		}
	);

	return (res?.models ?? [])
		.map((model) => ({ id: model.model, name: model.name ?? model.model, ...model }))
		.sort((a, b) => {
			return a.name.localeCompare(b.name);
		});
};

export const generatePrompt = async (model: string, conversation: string) => {
	if (conversation === '') {
		conversation = '[no existing conversation]';
	}

	return await apiFetch(
		`${OLLAMA_API_BASE_URL}/api/generate`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				prompt: `Conversation:
			${conversation}

			As USER in the conversation above, your task is to continue the conversation. Remember, Your responses should be crafted as if you're a human conversing in a natural, realistic manner, keeping in mind the context and flow of the dialogue. Please generate a fitting response to the last message in the conversation, or if there is no existing conversation, initiate one as a normal person would.
			
			Response:
			`
			})
		},
		false
	);
};

export const generateEmbeddings = async (model: string, text: string) => {
	return await apiFetch(
		`${OLLAMA_API_BASE_URL}/api/embeddings`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				prompt: text
			})
		},
		false
	);
};

export const generateTextCompletion = async (model: string, text: string) => {
	return await apiFetch(
		`${OLLAMA_API_BASE_URL}/api/generate`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				prompt: text,
				stream: true
			})
		},
		false
	);
};

export const generateChatCompletion = async (
	body: object
): Promise<[Response, AbortController]> => {
	let controller = new AbortController();

	const res = await apiFetch<Response>(
		`${OLLAMA_API_BASE_URL}/api/chat`,
		{
			signal: controller.signal,
			method: 'POST',
			body: JSON.stringify(body)
		},
		false
	);

	return [res, controller];
};

export const createModel = async (
	tagName: string,
	content: string,
	urlIdx: string | null = null
) => {
	return await apiFetch(
		`${OLLAMA_API_BASE_URL}/api/create${urlIdx !== null ? `/${urlIdx}` : ''}`,
		{
			method: 'POST',
			body: JSON.stringify({
				name: tagName,
				modelfile: content
			})
		},
		false
	);
};

export const deleteModel = async (tagName: string, urlIdx: string | null = null) => {
	return await apiFetch(`${OLLAMA_API_BASE_URL}/api/delete${urlIdx !== null ? `/${urlIdx}` : ''}`, {
		method: 'DELETE',
		body: JSON.stringify({
			name: tagName
		})
	});
};

export const pullModel = async (
	tagName: string,
	urlIdx: number | null = null
): Promise<[Response, AbortController]> => {
	const controller = new AbortController();

	const res = await apiFetch<Response>(
		`${OLLAMA_API_BASE_URL}/api/pull${urlIdx !== null ? `/${urlIdx}` : ''}`,
		{
			signal: controller.signal,
			method: 'POST',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json'
			},

			body: JSON.stringify({
				name: tagName
			})
		},
		false
	);

	return [res, controller];
};

export const downloadModel = async (download_url: string, urlIdx: string | null = null) => {
	return await apiFetch(
		`${OLLAMA_API_BASE_URL}/models/download${urlIdx !== null ? `/${urlIdx}` : ''}`,
		{
			method: 'POST',
			body: JSON.stringify({
				url: download_url
			})
		},
		false
	);
};

export const uploadModel = async (file: File, urlIdx: string | null = null) => {
	const formData = new FormData();
	formData.append('file', file);

	return await apiFetch(
		`${OLLAMA_API_BASE_URL}/models/upload${urlIdx !== null ? `/${urlIdx}` : ''}`,
		{
			method: 'POST',
			body: formData
		},
		false
	);
};
