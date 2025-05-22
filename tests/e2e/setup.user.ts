import { test as setup, expect } from '@playwright/test';
import postgres from 'postgres';

const testUser = {
	id: crypto.randomUUID(),
	name: 'Test User',
	email: 'test@example.com', // Needs to match the X-User-Email header
	password: '$2b$12$2tGwAvh8Y6zwBweJg.CO3.CYyyeArii583SvoBZ9LdyztoVSjG5mW', // pragma: allowlist secret - hash of 'testuser'
	role: 'admin',
	active: true,
	profileImageUrl: '/user.png',
	settings: JSON.stringify({ ui: { acceptedTermsVersion: 0 } })
};

setup('insert test user in database', async () => {
	const dbUrl =
		process.env.POSTGRES_URL || 'postgresql://postgres:postgres@localhost:5432/postgres'; // pragma: allowlist secret
	const sql = postgres(dbUrl);

	// Remove stale test user if any
	await sql`DELETE FROM public."auth" WHERE email = ${testUser.email}`;
	await sql`DELETE FROM public."user" WHERE email = ${testUser.email}`;

	const auth = await sql`INSERT INTO public."auth"
        (id, email, password, active)
        VALUES
        (${testUser.id}, ${testUser.email}, ${testUser.password}, ${testUser.active})
		RETURNING id, email, active
    `;

	const timestamp = Math.floor(Date.now() / 1000);

	const user = await sql`INSERT INTO public."user"
		(id, name, email, role, profile_image_url, created_at, updated_at, last_active_at, settings)
		VALUES
		(${testUser.id}, ${testUser.name}, ${testUser.email}, ${testUser.role}, ${testUser.profileImageUrl}, ${timestamp}, ${timestamp}, ${timestamp}, ${testUser.settings})
		RETURNING id, name, email, role
	`;

	console.log('Test user created:', auth[0], user[0]);
});

setup('sign in test user and accept the terms', async ({ page }) => {
	await page.goto('/auth');
	await page.getByText('Agree and continue').click();
});
