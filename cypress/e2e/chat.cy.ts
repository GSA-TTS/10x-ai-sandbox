// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />

// These tests run through the chat flow.
describe('Chats', () => {
	// Wait for 2 seconds after all tests to fix an issue with Cypress's video recording missing the last few frames
	after(() => {
		// eslint-disable-next-line cypress/no-unnecessary-waiting
		cy.wait(2000);
	});

	beforeEach(() => {
		// Login as the regular user
		cy.loginAdmin(); // for some reason only the admin user works in GH actions
		// Visit the home page
		cy.visit('/');
	});

	// model name should be the exact text shown in the model selector dropdown
	const chatTest = (modelName) => {
		cy.clearTCModal(); // adding this here seemed to make tests in GH actions move forward
		// Click on the model selector
		cy.get('button[id="model-selector-0-button"]').click();
		// Select the desired model
		cy.contains(modelName).click();
		// Type a message
		cy.get('#chat-input').click();
		const message = 'Hi, what can you do? A single sentence only please.';
		cy.get('#chat-input', { timeout: 10_000 }).type(message, {
			force: true
		});
		// Send the message
		cy.get('button[type="submit"]').click();
		// User's message should be visible
		cy.contains(message).should('exist');
		// Response should be visible
		cy.get('.chat-assistant', { timeout: 10_000 }).should('exist');
	};

	context('Claude Sonnet 3.5 v2', () => {
		it('user can perform a text chat', chatTest.bind(this, 'Claude Sonnet 3.5 v2'));
	});

	context('Claude Haiku 3.5', () => {
		it('user can perform a text chat', chatTest.bind(this, 'Claude Haiku 3.5'));
	});

	context('Meta LLaMa 3.2 (11B)', () => {
		it('user can perform a text chat', chatTest.bind(this, 'Meta LLaMa 3.2 (11B)'));
	});
});
