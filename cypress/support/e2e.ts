/// <reference types="cypress" />
// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />

// When testing in a brand new environment, like in a CI run,
// this user will be an admin by virtue of being the first user.
// But that may not be the case when testing against another DB.
export const adminUser = {
	id: '7dd4db1a-1618-4c5b-8f07-88f5e5f99922',
	name: 'Admin User',
	email: 'admin@example.com', // pragma: allowlist secret
	password: 'adminpassword', // pragma: allowlist secret
	role: 'admin'
};

export const regUser = {
	id: 'e14e76c4-0561-45e2-8b79-c3ca2c8aebc6',
	name: 'Regular User',
	email: 'user@example.com', // pragma: allowlist secret
	password: 'userpassword', // pragma: allowlist secret
	role: 'user'
};

// TODO: gotta be a better way to do this
// Based on https://docs.cypress.io/app/guides/conditional-testing#Conditionally-check-whether-an-element-has-certain-text
export const clearTCModal = (timeout = 1000, attempts = 0) => {
	if (attempts > timeout / 100) {
		return; // modal never opened
	}
	cy.get('body').then(($body) => {
		if ($body.text().includes('Welcome')) {
			cy.log('TC MODAL FOUND');
			cy.get('button').contains('Agree and continue').click();
		} else {
			cy.log('TC MODAL NOT FOUND');
			cy.wait(100);
			clearTCModal(timeout, ++attempts);
		}
	});
};

const login = (email: string, password: string) => {
	return cy.session(
		email,
		() => {
			// Make sure to test against us english to have stable tests,
			// regardless on local language preferences
			localStorage.setItem('locale', 'en-US');
			// Visit auth page
			cy.visit('/auth');
			// Fill out the form
			cy.get('input[autocomplete="email"]').type(email);
			cy.get('input[type="password"]').type(password);
			// Submit the form
			cy.get('button[type="submit"]').click();
			// Agree to terms and conditions if it pops up
			clearTCModal();
			cy.contains('How can I help you today', { timeout: 5_000 }).should('exist');
		},
		{
			validate: () => {
				cy.request({
					method: 'GET',
					url: '/api/v1/auths/signin',
					headers: {
						Authorization: 'Bearer ' + localStorage.getItem('token')
					}
				});
			}
		}
	);
};

const loginAdmin = () => {
	return login(adminUser.email, adminUser.password);
};

const loginUser = () => {
	return login(regUser.email, regUser.password);
};

const seedUsers = () => {
	for (const user of [adminUser, regUser]) {
		cy.task('runDatabaseQuery', {
			sql: `DELETE FROM public."user" WHERE id = $1;`,
			values: [user.id]
		});
		const now = Math.floor(Date.now() / 1000);
		cy.task('runDatabaseQuery', {
			sql: `INSERT INTO public."user" VALUES ($1, $2, $3, $4, '/user.png', NULL, $5, $6, $7, 'null', 'null', NULL);`,
			values: [user.id, user.name, user.email, user.role, now, now, now]
		});
	}
};

Cypress.Commands.add('login', (email, password) => login(email, password));
Cypress.Commands.add('loginAdmin', () => loginAdmin());
Cypress.Commands.add('loginUser', () => loginUser());
Cypress.Commands.add('clearTCModal', () => clearTCModal());
Cypress.Commands.add('seedUsers', () => seedUsers());

before(() => {
	cy.seedUsers();
});
