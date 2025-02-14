import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import chokidar from 'chokidar';
import path from 'path';
import fs from 'fs-extra';

// /** @type {import('vite').Plugin} */
// const viteServerConfig = {
// 	name: 'log-request-middleware',
// 	configureServer(server) {
// 		server.middlewares.use((req, res, next) => {
// 			res.setHeader('Access-Control-Allow-Origin', '*');
// 			res.setHeader('Access-Control-Allow-Methods', 'GET');
// 			res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
// 			res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
// 			next();
// 		});
// 	}
// };

export default defineConfig({
	plugins: [
		sveltekit(),
		{
			name: 'watch-routes-override',
			configureServer() {
				const project = process.env.PROJECT || 'upstream-overrides';
				const projectPath = `src/.routes-${project}`;

				const watcher = chokidar.watch(`src/${project}`, {
					ignoreInitial: true,
					ignored: ['node_modules', '**/.*'],
					persistent: true
				});

				// Sync changes to .routes-${project}
				watcher.on('add', (filePath) => {
					const relativePath = path.relative(`src/${project}`, filePath);
					const targetPath = path.join(projectPath, relativePath);
					fs.ensureDirSync(path.dirname(targetPath));
					fs.copyFileSync(filePath, targetPath);
					console.log(`[File Added] Synced: ${relativePath}`);
				});

				watcher.on('change', (filePath) => {
					const relativePath = path.relative(`src/${project}`, filePath);
					const targetPath = path.join(projectPath, relativePath);
					fs.copyFileSync(filePath, targetPath);
					console.log(`[File Changed] Synced: ${relativePath}`);
				});

				watcher.on('unlink', (filePath) => {
					const relativePath = path.relative(`src/${project}`, filePath);
					const targetPath = path.join(projectPath, relativePath);
					fs.removeSync(targetPath);
					console.log(
						`[File Deleted] Removed: ${relativePath}. To pick up changes from the default directory, restart the server.`
					);
				});

				console.log(`Watching for changes in src/${project}...`);
			}
		}
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		sourcemap: true
	},
	worker: {
		format: 'es'
	}
});
