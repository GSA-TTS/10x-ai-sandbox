import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

interface CompletionResponse {
	choices: {
		message: { content: string };
	}[];
}

interface DataResponse {
	data: any;
}

interface URLResponse {
	url: any;
}

export const getModels = async (base: boolean = false) => {
	const res = await apiFetch<DataResponse>(`${WEBUI_BASE_URL}/api/models${base ? '/base' : ''}`, {
		method: 'GET'
	});

	let models = res?.data ?? [];
	return models;
};

type ChatCompletedForm = {
	model: string;
	messages: string[];
	chat_id: string;
	session_id: string;
};

export const chatCompleted = async (body: ChatCompletedForm) => {
	return apiFetch(`${WEBUI_BASE_URL}/api/chat/completed`, {
		method: 'POST',
		body: JSON.stringify(body)
	});
};

type ChatActionForm = {
	model: string;
	messages: string[];
	chat_id: string;
};

export const chatAction = async (action_id: string, body: ChatActionForm) => {
	return apiFetch(`${WEBUI_BASE_URL}/api/chat/actions/${action_id}`, {
		method: 'POST',
		body: JSON.stringify(body)
	});
};

export const stopTask = async (id: string) => {
	return apiFetch(`${WEBUI_BASE_URL}/api/tasks/stop/${id}`, {
		method: 'POST'
	});
};

export const getTaskConfig = async () => {
	return apiFetch(`${WEBUI_BASE_URL}/api/v1/tasks/config`, {
		method: 'GET'
	});
};

export const updateTaskConfig = async (config: object) => {
	return apiFetch(`${WEBUI_BASE_URL}/api/v1/tasks/config/update`, {
		method: 'POST',
		body: JSON.stringify(config)
	});
};

export const generateTitle = async (model: string, messages: string[], chat_id?: string) => {
	const res = await apiFetch<CompletionResponse>(
		`${WEBUI_BASE_URL}/api/v1/tasks/title/completions`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				messages: messages,
				...(chat_id && { chat_id: chat_id })
			})
		}
	);

	return res?.choices[0]?.message?.content.replace(/["']/g, '') ?? 'New Chat';
};

export const generateTags = async (model: string, messages: string, chat_id?: string) => {
	const res = await apiFetch<CompletionResponse>(
		`${WEBUI_BASE_URL}/api/v1/tasks/title/completions`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				messages: messages,
				...(chat_id && { chat_id: chat_id })
			})
		}
	);

	try {
		// Step 1: Safely extract the response string
		const response = res?.choices[0]?.message?.content ?? '';

		// Step 2: Attempt to fix common JSON format issues like single quotes
		const sanitizedResponse = response.replace(/['‘’`]/g, '"'); // Convert single quotes to double quotes for valid JSON

		// Step 3: Find the relevant JSON block within the response
		const jsonStartIndex = sanitizedResponse.indexOf('{');
		const jsonEndIndex = sanitizedResponse.lastIndexOf('}');

		// Step 4: Check if we found a valid JSON block (with both `{` and `}`)
		if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
			const jsonResponse = sanitizedResponse.substring(jsonStartIndex, jsonEndIndex + 1);

			// Step 5: Parse the JSON block
			const parsed = JSON.parse(jsonResponse);

			// Step 6: If there's a "tags" key, return the tags array; otherwise, return an empty array
			if (parsed && parsed.tags) {
				return Array.isArray(parsed.tags) ? parsed.tags : [];
			} else {
				return [];
			}
		}

		// If no valid JSON block found, return an empty array
		return [];
	} catch (e) {
		// Catch and safely return empty array on any parsing errors
		console.error('Failed to parse response: ', e);
		return [];
	}
};

export const generateEmoji = async (model: string, prompt: string, chat_id?: string) => {
	const res = await apiFetch<CompletionResponse>(
		`${WEBUI_BASE_URL}/api/v1/tasks/emoji/completions`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				prompt: prompt,
				...(chat_id && { chat_id: chat_id })
			})
		}
	);

	const response = res?.choices[0]?.message?.content.replace(/["']/g, '') ?? null;

	if (response) {
		if (/\p{Extended_Pictographic}/u.test(response)) {
			return response.match(/\p{Extended_Pictographic}/gu)![0];
		}
	}

	return null;
};

export const generateQueries = async (
	model: string,
	messages: object[],
	prompt: string,
	type: string = 'web_search'
) => {
	const res = await apiFetch<CompletionResponse>(
		`${WEBUI_BASE_URL}/api/v1/tasks/queries/completions`,
		{
			method: 'POST',
			body: JSON.stringify({
				model: model,
				messages: messages,
				prompt: prompt,
				type: type
			})
		}
	);

	// Step 1: Safely extract the response string
	const response = res?.choices[0]?.message?.content ?? '';

	try {
		const jsonStartIndex = response.indexOf('{');
		const jsonEndIndex = response.lastIndexOf('}');

		if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
			const jsonResponse = response.substring(jsonStartIndex, jsonEndIndex + 1);

			// Step 5: Parse the JSON block
			const parsed = JSON.parse(jsonResponse);

			// Step 6: If there's a "queries" key, return the queries array; otherwise, return an empty array
			if (parsed && parsed.queries) {
				return Array.isArray(parsed.queries) ? parsed.queries : [];
			} else {
				return [];
			}
		}

		// If no valid JSON block found, return response as is
		return [response];
	} catch (e) {
		// Catch and safely return empty array on any parsing errors
		console.error('Failed to parse response: ', e);
		return [response];
	}
};

export const generateAutoCompletion = async (
	model: string,
	prompt: string,
	messages?: object[],
	type: string = 'search query'
) => {
	const controller = new AbortController();

	const res = await apiFetch<CompletionResponse>(
		`${WEBUI_BASE_URL}/api/v1/tasks/auto/completions`,
		{
			signal: controller.signal,
			method: 'POST',
			body: JSON.stringify({
				model: model,
				prompt: prompt,
				...(messages && { messages: messages }),
				type: type,
				stream: false
			})
		}
	);

	const response = res?.choices[0]?.message?.content ?? '';

	try {
		const jsonStartIndex = response.indexOf('{');
		const jsonEndIndex = response.lastIndexOf('}');

		if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
			const jsonResponse = response.substring(jsonStartIndex, jsonEndIndex + 1);

			// Step 5: Parse the JSON block
			const parsed = JSON.parse(jsonResponse);

			// Step 6: If there's a "queries" key, return the queries array; otherwise, return an empty array
			if (parsed && parsed.text) {
				return parsed.text;
			} else {
				return '';
			}
		}

		// If no valid JSON block found, return response as is
		return response;
	} catch (e) {
		// Catch and safely return empty array on any parsing errors
		console.error('Failed to parse response: ', e);
		return response;
	}
};

export const generateMoACompletion = async (
	model: string,
	prompt: string,
	responses: string[]
): Promise<[Response, AbortController]> => {
	const controller = new AbortController();

	const res = await apiFetch<Response>(
		`${WEBUI_BASE_URL}/api/v1/tasks/moa/completions`,
		{
			signal: controller.signal,
			method: 'POST',
			body: JSON.stringify({
				model: model,
				prompt: prompt,
				responses: responses,
				stream: true
			})
		},
		false
	);

	return [res, controller];
};

export const getPipelinesList = async () => {
	const res = await apiFetch<DataResponse>(`${WEBUI_BASE_URL}/api/v1/pipelines/list`, {
		method: 'GET'
	});

	let pipelines = res?.data ?? [];
	return pipelines;
};

export const uploadPipeline = async (file: File, urlIdx: string) => {
	// Create a new FormData object to handle the file upload
	const formData = new FormData();
	formData.append('file', file);
	formData.append('urlIdx', urlIdx);

	return await apiFetch(`${WEBUI_BASE_URL}/api/v1/pipelines/upload`, {
		method: 'POST',
		body: formData
	});
};

export const downloadPipeline = async (url: string, urlIdx: string) => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/v1/pipelines/add`, {
		method: 'POST',
		body: JSON.stringify({
			url: url,
			urlIdx: urlIdx
		})
	});
};

export const deletePipeline = async (id: string, urlIdx: string) => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/v1/pipelines/delete`, {
		method: 'DELETE',
		body: JSON.stringify({
			id: id,
			urlIdx: urlIdx
		})
	});
};

export const getPipelines = async (urlIdx?: string) => {
	const searchParams = new URLSearchParams();
	if (urlIdx !== undefined) {
		searchParams.append('urlIdx', urlIdx);
	}

	const res = await apiFetch<DataResponse>(
		`${WEBUI_BASE_URL}/api/v1/pipelines/?${searchParams.toString()}`,
		{
			method: 'GET'
		}
	);

	let pipelines = res?.data ?? [];
	return pipelines;
};

export const getPipelineValves = async (pipeline_id: string, urlIdx: string) => {
	const searchParams = new URLSearchParams();
	if (urlIdx !== undefined) {
		searchParams.append('urlIdx', urlIdx);
	}

	return await apiFetch(
		`${WEBUI_BASE_URL}/api/v1/pipelines/${pipeline_id}/valves?${searchParams.toString()}`,
		{ method: 'GET' }
	);
};

export const getPipelineValvesSpec = async (pipeline_id: string, urlIdx: string) => {
	const searchParams = new URLSearchParams();
	if (urlIdx !== undefined) {
		searchParams.append('urlIdx', urlIdx);
	}

	return await apiFetch(
		`${WEBUI_BASE_URL}/api/v1/pipelines/${pipeline_id}/valves/spec?${searchParams.toString()}`,
		{ method: 'GET' }
	);
};

export const updatePipelineValves = async (pipeline_id: string, valves: object, urlIdx: string) => {
	const searchParams = new URLSearchParams();
	if (urlIdx !== undefined) {
		searchParams.append('urlIdx', urlIdx);
	}

	return await apiFetch(
		`${WEBUI_BASE_URL}/api/v1/pipelines/${pipeline_id}/valves/update?${searchParams.toString()}`,
		{
			method: 'POST',
			body: JSON.stringify(valves)
		}
	);
};

export const getBackendConfig = async () => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/config`, { method: 'GET' });
};

export const getChangelog = async () => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/changelog`, { method: 'GET' });
};

export const getVersionUpdates = async () => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/version/updates`, { method: 'GET' });
};

export const getModelFilterConfig = async () => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/config/model/filter`, { method: 'GET' });
};

export const updateModelFilterConfig = async (enabled: boolean, models: string[]) => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/config/model/filter`, {
		method: 'POST',
		body: JSON.stringify({
			enabled: enabled,
			models: models
		})
	});
};

export const getWebhookUrl = async () => {
	const res = await apiFetch<URLResponse>(`${WEBUI_BASE_URL}/api/webhook`, { method: 'GET' });
	return res.url;
};

export const updateWebhookUrl = async (url: string) => {
	const res = await apiFetch<URLResponse>(`${WEBUI_BASE_URL}/api/webhook`, {
		method: 'POST',
		body: JSON.stringify({
			url: url
		})
	});
	return res.url;
};

export const getCommunitySharingEnabledStatus = async () => {
	return apiFetch(`${WEBUI_BASE_URL}/api/community_sharing`, { method: 'GET' });
};

export const toggleCommunitySharingEnabledStatus = async () => {
	return apiFetch(`${WEBUI_BASE_URL}/api/community_sharing/toggle`, { method: 'GET' });
};

export const getModelConfig = async (): Promise<GlobalModelConfig> => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/config/models`, { method: 'GET' });
};

export interface ModelConfig {
	id: string;
	name: string;
	meta: ModelMeta;
	base_model_id?: string;
	params: ModelParams;
}

export interface ModelMeta {
	description?: string;
	capabilities?: object;
	profile_image_url?: string;
}

export interface ModelParams {}

export type GlobalModelConfig = ModelConfig[];

export const updateModelConfig = async (config: GlobalModelConfig) => {
	return await apiFetch(`${WEBUI_BASE_URL}/api/config/models`, {
		method: 'POST',
		body: JSON.stringify({
			models: config
		})
	});
};
