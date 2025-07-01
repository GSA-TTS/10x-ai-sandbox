import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ url }) => {
	/*
	 * This page load function provides a method to begin a new chat via URL
	 * parameters. It is meant to allow users to initiate chats from external
	 * websites such as other parts of the USAi ecosystem.
	 *
	 * URL parameters:
	 *   - q: The initial message to send to the model
	 *   - model: The desired model identifier (get it from /api/models)
	 *   - web-search: Set 'true' to enable web search
	 *
	 * Example:
	 *
	 * https://chat.gsa.gov/new?q=hello&model=bedrock_claude_sonnet37_pipeline&web-search=true
	 *
	 */
	const q = url.searchParams.get('q');
	const model = url.searchParams.get('model');
	const webSearch = url.searchParams.get('web-search');

	const newQuery = new URLSearchParams();
	if (q) {
		newQuery.set('q', q);
	}
	if (model) {
		newQuery.set('model', model);
	}
	if (webSearch) {
		newQuery.set('web-search', webSearch);
	}

	throw redirect(307, `/?${newQuery.toString()}`);
};
