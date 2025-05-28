import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
	await page.goto('/');

	// Expect the title to contain the app name.
	await expect(page).toHaveTitle(/GSA Chat/);
});

test('has message input', async ({ page }) => {
	await page.goto('/');

	// Expect a new chat message input field.
	await expect(page.getByLabel('Enter your prompt')).toBeVisible();
});
