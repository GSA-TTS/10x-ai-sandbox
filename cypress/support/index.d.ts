// load the global Cypress types
/// <reference types="cypress" />

declare namespace Cypress {
	interface Chainable {
		login(email: string, password: string): Chainable<null>;
		register(name: string, email: string, password: string): Chainable<Response<any>>;
		registerAdmin(): Chainable<Response<any>>;
		registerUser(): Chainable<Response<any>>;
		loginAdmin(): Chainable<null>;
		loginUser(): Chainable<null>;
		clearTCModal(): Chainable<null>;
	}
}
