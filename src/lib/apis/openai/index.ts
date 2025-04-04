import { OPENAI_API_BASE_URL, WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getOpenAIConfig = async () => {
	return await apiFetch(`${OPENAI_API_BASE_URL}/config`, { method: 'GET' });
};

type OpenAIConfig = {
	ENABLE_OPENAI_API: boolean;
	OPENAI_API_BASE_URLS: string[];
	OPENAI_API_KEYS: string[];
	OPENAI_API_CONFIGS: object;
};

export const updateOpenAIConfig = async (config: OpenAIConfig) => {
	return await apiFetch(`${OPENAI_API_BASE_URL}/config/update`, {
		method: 'POST',
		body: JSON.stringify({
			...config
		})
	});
};

type OpenAMetaDataResponse =
	| { OPENAI_API_BASE_URLS: any; OPENAI_API_KEYS?: never }
	| { OPENAI_API_BASE_URLS?: never; OPENAI_API_KEYS: any };

export const getOpenAIUrls = async () => {
	const res = await apiFetch<OpenAMetaDataResponse>(`${OPENAI_API_BASE_URL}/urls`, {
		method: 'GET'
	});
	return res.OPENAI_API_BASE_URLS;
};

export const updateOpenAIUrls = async (urls: string[]) => {
	const res = await apiFetch<OpenAMetaDataResponse>(`${OPENAI_API_BASE_URL}/urls/update`, {
		method: 'POST',
		body: JSON.stringify({
			urls: urls
		})
	});
	return res.OPENAI_API_BASE_URLS;
};

export const getOpenAIKeys = async () => {
	const res = await apiFetch<OpenAMetaDataResponse>(`${OPENAI_API_BASE_URL}/keys`, {
		method: 'GET'
	});
	return res.OPENAI_API_KEYS;
};

export const updateOpenAIKeys = async (keys: string[]) => {
	const res = await apiFetch<OpenAMetaDataResponse>(`${OPENAI_API_BASE_URL}/keys/update`, {
		method: 'POST',
		body: JSON.stringify({
			keys: keys
		})
	});
	return res.OPENAI_API_KEYS;
};

export const getOpenAIModels = async (urlIdx?: number) => {
	return await apiFetch(
		`${OPENAI_API_BASE_URL}/models${typeof urlIdx === 'number' ? `/${urlIdx}` : ''}`,
		{ method: 'GET' }
	);
};

export const verifyOpenAIConnection = async (
	url: string = 'https://api.openai.com/v1',
	key: string = ''
) => {
	return apiFetch(`${OPENAI_API_BASE_URL}/verify`, {
		method: 'POST',
		body: JSON.stringify({
			url,
			key
		})
	});
};

export const chatCompletion = async (
	body: object,
	url: string = `${WEBUI_BASE_URL}/api`
): Promise<[Response | null, AbortController]> => {
	const controller = new AbortController();

	const res = await apiFetch<Response>(
		`${url}/chat/completions`,
		{
			signal: controller.signal,
			method: 'POST',
			body: JSON.stringify(body)
		},
		false
	);

	return [res, controller];
};

export const generateOpenAIChatCompletion = async (
	body: object,
	url: string = `${WEBUI_BASE_URL}/api`
) => {
	return await apiFetch(`${url}/chat/completions`, {
		method: 'POST',
		body: JSON.stringify(body)
	});
};

export const synthesizeOpenAISpeech = async (
	speaker: string = 'alloy',
	text: string = '',
	model: string = 'tts-1'
): Promise<Response> => {
	return await apiFetch(
		`${OPENAI_API_BASE_URL}/audio/speech`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				input: text,
				voice: speaker
			})
		},
		false
	);
};
