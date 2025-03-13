<script context="module">
	// Update this version number when updating the terms content. Any change to
	// this value will trigger a re-display of the terms for all users.
	export const TERMS_VERSION = 1;
</script>

<script lang="ts">
	import { settings, user } from '$lib/stores';

	import Modal from './common/Modal.svelte';
	import { updateUserSettings } from '$lib/apis/users';

	export let show = false;

	let headingId = 'terms-heading';

	async function acceptTerms() {
		await settings.set({ ...$settings, ...{ acceptedTermsVersion: TERMS_VERSION } });
		await updateUserSettings(localStorage.token, { ui: $settings });
		show = false;
	}
</script>

<Modal bind:show allowEasyDismiss={false} {headingId} closeButton={false}>
	<div class="px-5 pt-4">
		<h2 id={headingId} class="text-xl text-[#00538E] font-semibold">
			Welcome{$user?.name ? ` ${$user.name}` : ''}!
			<span class="sr-only"
				>Please review and accept the terms and conditions before proceeding.</span
			>
		</h2>
	</div>

	<div class="w-full p-4 px-5 text-gray-700 dark:text-gray-100">
		<div class="overflow-y-scroll max-h-100 scrollbar-hidden">
			<div class="mb-3">
				<p class="my-2 font-semibold">
					Chat is GSA’s AI-powered chatbot. You can use Chat to help you:
				</p>
				<ul class="mt-1 list-disc pl-5">
					<li>Write and edit documents</li>
					<li>Summarize information</li>
					<li>Research a common topic</li>
				</ul>
				<p class="my-2 font-semibold">
					When using Chat, you need to understand and agree to our <a
						href="https://insite.gsa.gov/services-and-offices/staff-offices/office-of-gsa-it/artificial-intelligence/gsas-aipowered-chat/chat-resources/chat-privacy-policy"
						>privacy policy</a
					>, which covers the following:
				</p>
				<ul class="terms-list list-none p-0">
					<li>
						All prompts and responses will be logged. Your data will be protected and used only to
						improve and further refine Chat.
					</li>
					<li>
						GSA's <a
							href="https://insite.gsa.gov/directives-library/gsa-information-technology-it-general-rules-of-behavior-4"
							>IT Rules of Behavior</a
						>
						and
						<a
							href="https://insite.gsa.gov/directives-library/use-of-artificial-intelligence-at-gsa"
							>AI Directive</a
						> prohibit using Chat inappropriately or for harmful purposes.
					</li>
					<li>
						Chat may generate incorrect or misleading information. Please carefully review its
						responses.
					</li>
				</ul>
				<p class="my-2 font-semibold">
					If you have any feedback, need further assistance, or have an issue, please reach out to
					the team at <a href="mailto:chat@gsa.gov">chat@gsa.gov</a>.
				</p>
			</div>
		</div>
		<div class="flex justify-end pt-3 text-sm font-medium">
			<button
				on:click={acceptTerms}
				class=" px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
			>
				<span class="relative">Agree and continue</span>
			</button>
		</div>
	</div>
</Modal>

<style>
	.terms-list li::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0.25rem;
		width: 2rem;
		height: 2rem;
		background-color: #e4f4ff;
		border-radius: 50%;
		background-repeat: no-repeat;
		background-position: center;
		background-size: 1.25rem;
	}

	.terms-list li {
		padding-left: 2.75rem;
		position: relative;
		margin-bottom: 0.75rem;
	}

	.terms-list li:nth-child(1)::before {
		/* icon: database */
		background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%2300538E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-database"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>');
	}

	.terms-list li:nth-child(2)::before {
		/* icon: list */
		background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%2300538E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-list"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>');
	}

	.terms-list li:nth-child(3)::before {
		/* icon: alert-triangle */
		background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%2300538E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>');
	}
</style>
