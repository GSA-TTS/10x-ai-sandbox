import { userSignOut } from '$lib/apis/auths';

/**
 * apiClient.ts
 * This is intended to be a dropin replacement for
 * fetch() that handles unauthorized responses by
 * redirecting to the auth page.
 *  */

export class ApiError extends Error {
	public status?: number;
	public details?: unknown;

	constructor(message: string, status?: number, details: unknown = {}) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.details = details;
		Object.setPrototypeOf(this, ApiError.prototype);
	}
}

/**
 * Parse the response as JSON if json is true (default), throw if !response.ok
 * Other wise return the raw fetch Response, this is sometimes needed for streams
 */
async function handleResponse<T>(response: Response, json: boolean = true): Promise<T> {
	if (!response.ok) {
		let errorBody: unknown;
		try {
			errorBody = await response.json();
		} catch {
			errorBody = {};
		}
		const message = (errorBody as any)?.detail ?? `Request failed with status ${response.status}`;
		throw new ApiError(message, response.status, errorBody);
	}
	if (json) {
		return (await response.json()) as T;
	} else {
		return response as T;
	}
}

/**
 * apiFetch - A fetch wrapper that:
 *  1. Includes credentials (cookies) on every request.
 *  2. On receiving a 401 or 403 redirect to auth.
 */
export async function apiFetch<T = unknown>(
	input: RequestInfo | URL,
	init: RequestInit = {},
	json: boolean = true
): Promise<T> {
	const defaultHeaders: Record<string, string> = {
		Accept: 'application/json',
		'Content-Type': 'application/json'
	};

	const userHeaders = init.headers ?? {};
	Object.assign(defaultHeaders, userHeaders);

	// Handle situations where we are uploading FormData
	// remove Content-Type so the browser can properl set it (with the boundary).
	if (init.body instanceof FormData) {
		delete defaultHeaders['Content-Type'];
	}
	const mergedInit: RequestInit = {
		credentials: 'include',
		...init,
		headers: defaultHeaders
	};

	let response: Response;
	try {
		response = await fetch(input, mergedInit);
	} catch (err) {
		console.error('Network error:', err);
		throw err;
	}

	if (response.status === 401 || response.status === 403) {
		console.log('got unauth response from API, redirecting');
		try {
			await userSignOut();
		} catch (err) {
			console.log('error signing out', err);
		}
		if (window.location.pathname !== '/auth') {
			window.location.href = '/auth';
		}

		// this is mostly to satisfy the return type in the signature
		throw new ApiError('Not authenticated', 401);
	} else {
		return handleResponse<T>(response, json);
	}
}
