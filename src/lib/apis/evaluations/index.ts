import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getConfig = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/config`, { method: 'GET' });
};

export const updateConfig = async (config: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/config`, {
		method: 'POST',
		body: JSON.stringify({
			...config
		})
	});
};

export const getAllFeedbacks = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/feedbacks/all`, { method: 'GET' });
};

export const exportAllFeedbacks = async () => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/feedbacks/all/export`, {
		method: 'GET'
	});
};

export const createNewFeedback = async (feedback: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/feedback`, {
		method: 'POST',
		body: JSON.stringify({
			...feedback
		})
	});
};

export const getFeedbackById = async (feedbackId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/feedback/${feedbackId}`, {
		method: 'GET'
	});
};

export const updateFeedbackById = async (feedbackId: string, feedback: object) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/feedback/${feedbackId}`, {
		method: 'POST',
		body: JSON.stringify({
			...feedback
		})
	});
};

export const deleteFeedbackById = async (feedbackId: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/evaluations/feedback/${feedbackId}`, {
		method: 'DELETE'
	});
};
