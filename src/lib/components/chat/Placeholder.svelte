<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { marked } from 'marked';

	import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
	import { blur, fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	import { config, user, models as _models, temporaryChatEnabled } from '$lib/stores';
	import { sanitizeResponseContent, findWordIndices } from '$lib/utils';
	import { WEBUI_BASE_URL } from '$lib/constants';

	import Suggestions from './Suggestions.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import MessageInput from './MessageInput.svelte';

	const i18n = getContext('i18n');

	export let transparentBackground = false;

	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined;
	export let selectedModels: [''];

	export let history;

	export let prompt = '';
	export let files = [];

	export let selectedToolIds = [];
	export let webSearchEnabled = false;

	let models = [];

	const selectSuggestionPrompt = async (p) => {
		let text = p;

		if (p.includes('{{CLIPBOARD}}')) {
			const clipboardText = await navigator.clipboard.readText().catch((err) => {
				toast.error($i18n.t('Failed to read clipboard contents'));
				return '{{CLIPBOARD}}';
			});

			text = p.replaceAll('{{CLIPBOARD}}', clipboardText);

			console.log('Clipboard text:', clipboardText, text);
		}

		prompt = text;

		console.log(prompt);
		await tick();

		const chatInputContainerElement = document.getElementById('chat-input-container');
		const chatInputElement = document.getElementById('chat-input');

		if (chatInputContainerElement) {
			chatInputContainerElement.style.height = '';
			chatInputContainerElement.style.height =
				Math.min(chatInputContainerElement.scrollHeight, 200) + 'px';
		}

		await tick();
		if (chatInputElement) {
			chatInputElement.focus();
			chatInputElement.dispatchEvent(new Event('input'));
		}

		await tick();
	};

	let selectedModelIdx = 0;

	$: if (selectedModels.length > 0) {
		selectedModelIdx = models.length - 1;
	}

	$: models = selectedModels.map((id) => $_models.find((m) => m.id === id));

	onMount(() => {});
</script>

<div class="m-auto w-full max-w-6xl px-2 xl:px-20 translate-y-6 py-24 text-center">
	{#if $temporaryChatEnabled}
		<Tooltip
			content="This chat won't appear in history and your messages will not be saved."
			className="w-full flex justify-center mb-0.5"
			placement="top"
		>
			<div class="flex items-center gap-2 text-gray-600 font-medium text-lg my-2 w-fit">
				<EyeSlash strokeWidth="2.5" className="size-5" /> Temporary Chat
			</div>
		</Tooltip>
	{/if}

	<div
		class="w-full text-gray-800 dark:text-gray-100 font-medium text-center flex items-center gap-4 font-primary"
	>
		<div class="w-full flex flex-col justify-center items-center">
			<div class="flex flex-row justify-center gap-3 sm:gap-3.5 w-fit px-5 mb-3">
				{#if $config?.features?.enable_message_input_logo}
					<div class="flex flex-shrink-0 justify-center">
						<div class="flex -space-x-4 mb-0.5" in:fade={{ duration: 100 }}>
							{#each models as model, modelIdx}
								<Tooltip
									content={(models[modelIdx]?.info?.meta?.tags ?? [])
										.map((tag) => tag.name.toUpperCase())
										.join(', ')}
									placement="top"
								>
									<button
										on:click={() => {
											selectedModelIdx = modelIdx;
										}}
										disabled={!models.length < 2}
									>
										<img
											crossorigin="anonymous"
											src={model?.info?.meta?.profile_image_url ??
												($i18n.language === 'dg-DG'
													? `/doge.png`
													: `${WEBUI_BASE_URL}/static/gsai.png`)}
											class=" w-16 sm:w-20"
											alt=""
											draggable="false"
										/>
									</button>
								</Tooltip>
							{/each}
						</div>
					</div>
				{/if}

				<h1 class="text-xl lg:text-3xl sm:text-2xl line-clamp-1" in:fade={{ duration: 100 }}>
					{$i18n.t('How can I help you today?')}
				</h1>
			</div>

			<div
				class="text-base font-normal xl:translate-x-6 md:max-w-3xl w-full py-3 {atSelectedModel
					? 'mt-2'
					: ''}"
			>
				<MessageInput
					{history}
					{selectedModels}
					bind:files
					bind:prompt
					bind:autoScroll
					bind:selectedToolIds
					bind:webSearchEnabled
					bind:atSelectedModel
					{transparentBackground}
					{stopResponse}
					{createMessagePair}
					placeholder={$i18n.t('Send a message')}
					on:upload={(e) => {
						dispatch('upload', e.detail);
					}}
					on:submit={(e) => {
						dispatch('submit', e.detail);
					}}
				/>
			</div>
		</div>
	</div>
	{#if $config?.features?.enable_prompt_suggestions}
		<div class="mx-auto max-w-3xl font-primary px-8" in:fade={{ duration: 200, delay: 200 }}>
			<div class="mx-1">
				<Suggestions
					suggestionPrompts={models[selectedModelIdx]?.info?.meta?.suggestion_prompts ??
						$config?.default_prompt_suggestions ??
						[]}
					on:select={(e) => {
						selectSuggestionPrompt(e.detail);
					}}
				/>
			</div>
		</div>
	{/if}
</div>
