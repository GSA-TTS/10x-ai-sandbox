/// <reference types="cypress" />
// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />

// When testing in a brand new environment, like in a CI run,
// this user will be an admin by virtue of being the first user.
// But that may not be the case when testing against another DB.
export const adminUser = {
	name: 'Admin User',
	email: 'admin@example.com', // pragma: allowlist secret
	password: 'adminpassword' // pragma: allowlist secret
};

export const regUser = {
	name: 'Regular User',
	email: 'user@example.com', // pragma: allowlist secret
	password: 'userpassword' // pragma: allowlist secret
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
			cy.contains('How can I help you today').should('exist');
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

const register = (name: string, email: string, password: string) => {
	return cy
		.request({
			method: 'POST',
			url: '/api/v1/auths/signup',
			body: {
				name: name,
				email: email,
				password: password
			},
			failOnStatusCode: false
		})
		.then((response) => {
			expect(response.status).to.be.oneOf([200, 400, 403]);
		});
};

const registerAdmin = () => {
	return register(adminUser.name, adminUser.email, adminUser.password);
};

const registerUser = () => {
	return register(regUser.name, regUser.email, regUser.password);
};

const loginAdmin = () => {
	return login(adminUser.email, adminUser.password);
};

const loginUser = () => {
	return login(regUser.email, regUser.password);
};

Cypress.Commands.add('login', (email, password) => login(email, password));
Cypress.Commands.add('register', (name, email, password) => register(name, email, password));
Cypress.Commands.add('registerAdmin', () => registerAdmin());
Cypress.Commands.add('registerUser', () => registerUser());
Cypress.Commands.add('loginAdmin', () => loginAdmin());
Cypress.Commands.add('loginUser', () => loginUser());

before(() => {
	cy.registerAdmin();
	cy.registerUser();
});
