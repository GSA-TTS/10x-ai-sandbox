// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />
import { adminUser, regUser } from '../support/e2e';

// These tests assume the following defaults:
// 1. No users exist in the database or that the test admin user is an admin
// 2. Language is set to English
// 3. The default role for new users is 'pending'
describe('Login', () => {
	// Wait for 2 seconds after all tests to fix an issue with Cypress's video recording missing the last few frames
	after(() => {
		// eslint-disable-next-line cypress/no-unnecessary-waiting
		cy.wait(2000);
	});

	beforeEach(() => {
		cy.visit('/signout');
		cy.visit('/auth');
	});

	it('can login with the admin user', () => {
		// Fill out the form
		cy.get('input[autocomplete="email"]').type(adminUser.email);
		cy.get('input[type="password"]').type(adminUser.password);
		// Submit the form
		cy.get('button[type="submit"]').click();
		// Wait until the user is redirected to the home page
		cy.contains('How can I help you today');
	});

	it('can login with the regular user', () => {
		// Fill out the form
		cy.get('input[autocomplete="email"]').type(regUser.email);
		cy.get('input[type="password"]').type(regUser.password);
		// Submit the form
		cy.get('button[type="submit"]').click();
		// Wait until the user is redirected to the home page
		cy.contains('How can I help you today');
	});
});
