import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import path from 'path';
import fs from 'fs-extra';
import { globSync as glob } from 'glob';

const project = process.env.PROJECT || 'upstream-overrides';
let routes = 'src/routes';

if (project) {
	const project_files = new Set(glob('**', { cwd: `src/${project}`, filesOnly: true }));
	const default_files = new Set(glob('**', { cwd: routes, filesOnly: true }));

	const projectPath = `src/.routes-${project}`;

	fs.removeSync(projectPath);
	fs.copySync(`src/${project}`, projectPath);

	for (const file of default_files) {
		if (!project_files.has(file)) {
			const targetDir = path.dirname(`${projectPath}/${file}`);
			fs.ensureDirSync(targetDir);
			fs.copySync(`${routes}/${file}`, `${projectPath}/${file}`);
		}
	}

	routes = projectPath;
}

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
	// for more information about preprocessors
	preprocess: vitePreprocess(),
	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
		// If your environment is not supported or you settled on a specific environment, switch out the adapter.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: 'index.html'
		}),
		files: {
			routes
		}
	},
	onwarn: (warning, handler) => {
		const { code, _ } = warning;
		if (code === 'css-unused-selector') return;

		handler(warning);
	}
};

export default config;
