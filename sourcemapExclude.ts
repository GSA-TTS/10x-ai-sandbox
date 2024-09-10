import type { Plugin } from 'vite';

interface SourcemapExclude {
	excludeNodeModules?: boolean;
}
export function sourcemapExclude(opts?: SourcemapExclude): Plugin {
	return {
		name: 'sourcemap-exclude',
		transform(code: string, id: string) {
			if (opts?.excludeNodeModules && id.includes('node_modules')) {
				return {
					code,
					// https://github.com/rollup/rollup/blob/master/docs/plugin-development/index.md#source-code-transformations
					map: { mappings: '' }
				};
			}
		}
	};
}
