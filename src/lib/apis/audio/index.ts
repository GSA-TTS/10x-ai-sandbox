import { AUDIO_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getAudioConfig = async () => {
	return await apiFetch(`${AUDIO_API_BASE_URL}/config`, { method: 'GET' });
};

type OpenAIConfigForm = {
	url: string;
	key: string;
	model: string;
	speaker: string;
};

export const updateAudioConfig = async (payload: OpenAIConfigForm) => {
	return await apiFetch(`${AUDIO_API_BASE_URL}/config/update`, {
		method: 'POST',
		body: JSON.stringify({
			...payload
		})
	});
};

export const transcribeAudio = async (file: File) => {
	const data = new FormData();
	data.append('file', file);

	return apiFetch(`${AUDIO_API_BASE_URL}/transcriptions`, {
		method: 'POST',
		body: data
	});
};

export const synthesizeOpenAISpeech = async (
	speaker: string = 'alloy',
	text: string = '',
	model?: string
) => {
	return await apiFetch(
		`${AUDIO_API_BASE_URL}/speech`,
		{
			method: 'POST',
			body: JSON.stringify({
				input: text,
				voice: speaker,
				...(model && { model })
			})
		},
		false
	);
};

interface AvailableModelsResponse {
	models: { name: string; id: string }[] | { id: string }[];
}

export const getModels = async (): Promise<AvailableModelsResponse> => {
	return await apiFetch(`${AUDIO_API_BASE_URL}/models`, { method: 'GET' });
};

export const getVoices = async () => {
	return await apiFetch(`${AUDIO_API_BASE_URL}/voices`, { method: 'GET' });
};
