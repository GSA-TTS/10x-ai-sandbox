import { defineConfig } from 'cypress';
import { Pool } from 'pg';

export default defineConfig({
	e2e: {
		baseUrl: 'http://localhost:8080',
		setupNodeEvents(on, config) {
			on('task', {
				async runDatabaseQuery({ sql, values }) {
					const pool = new Pool({
						user: 'postgres',
						database: 'postgres',
						password: 'postgres', // pragma: allowlist secret
						host: 'localhost',
						port: 5432
					});
					try {
						const result = await pool.query(sql, values);
						await pool.end();
						return result;
					} catch (e) {
						console.error(e);
						throw e;
					}
				}
			});
		}
	},
	video: true
});
