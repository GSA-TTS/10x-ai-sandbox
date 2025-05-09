// load the global Cypress types
/// <reference types="cypress" />

declare namespace Cypress {
	interface Chainable {
		login(email: string, password: string): Chainable<null>;
		loginAdmin(): Chainable<null>;
		loginUser(): Chainable<null>;
		clearTCModal(): Chainable<null>;
		seedUsers(): Chainable<null>;
	}
}
