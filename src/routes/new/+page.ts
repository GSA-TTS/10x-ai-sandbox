import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ url }) => {
	const q = url.searchParams.get('q');
	const model = url.searchParams.get('model');

	const newQuery = new URLSearchParams();
	if (q) {
		newQuery.set('q', q);
	}
	if (model) {
		newQuery.set('model', model);
	}

	throw redirect(307, `/?${newQuery.toString()}`);
};
