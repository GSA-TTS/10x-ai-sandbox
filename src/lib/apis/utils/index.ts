import { WEBUI_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';

export const getGravatarUrl = async (email: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/utils/gravatar?email=${email}`, {
		method: 'GET'
	});
};

export const formatPythonCode = async (code: string) => {
	return await apiFetch(`${WEBUI_API_BASE_URL}/utils/code/format`, {
		method: 'POST',
		body: JSON.stringify({
			code: code
		})
	});
};

export const downloadChatAsPDF = async (title: string, messages: object[]) => {
	let error = null;

	const blob = await fetch(`${WEBUI_API_BASE_URL}/utils/pdf`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			title: title,
			messages: messages
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.blob();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	return blob;
};

export const getHTMLFromMarkdown = async (md: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/utils/markdown`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			md: md
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err;
			return null;
		});

	return res.html;
};

export const downloadDatabase = async () => {
	/* This feature is only available when using a SQLite DB */
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/utils/db/download`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			credentials: 'include'
		}
	})
		.then(async (response) => {
			if (!response.ok) {
				throw await response.json();
			}
			return response.blob();
		})
		.then((blob) => {
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'webui.db';
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}
};

export const downloadLiteLLMConfig = async () => {
	/* this function is never called in the code base */
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/utils/litellm/config`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			credentials: 'include'
		}
	})
		.then(async (response) => {
			if (!response.ok) {
				throw await response.json();
			}
			return response.blob();
		})
		.then((blob) => {
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'config.yaml';
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}
};
