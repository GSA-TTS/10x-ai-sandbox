<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { createEventDispatcher, onMount, getContext } from 'svelte';
	import { config, models } from '$lib/stores';
	import Tags from '$lib/components/common/Tags.svelte';

	const i18n = getContext('i18n');

	const dispatch = createEventDispatcher();

	export let message;
	export let show = false;

	let reasons = ['harmful_or_offensive', 'not_relevant', 'not_accurate', 'incomplete_response'];

	let detailed_ratings = ['bad', 'very_bad', 'extremely_bad'];
	let tags = [];

	let selectedReason = null;
	let comment = '';

	let detailedRating = null;
	let selectedModel = null;

	$: if (message) {
		init();
	}

	const init = () => {
		if (!selectedReason) {
			selectedReason = message?.annotation?.reason ?? '';
		}

		if (!comment) {
			comment = message?.annotation?.comment ?? '';
		}

		tags = (message?.annotation?.tags ?? []).map((tag) => ({
			name: tag
		}));

		if (!detailedRating) {
			detailedRating = message?.annotation?.details?.rating ?? null;
		}
	};

	onMount(() => {
		if (message?.arena) {
			selectedModel = $models.find((m) => m.id === message.selectedModelId);
			toast.success(
				$i18n.t('This response was generated by "{{model}}"', {
					model: selectedModel ? (selectedModel?.name ?? selectedModel.id) : message.selectedModelId
				})
			);
		}
	});

	const saveHandler = () => {
		console.log('saveHandler');
		dispatch('save', {
			reason: selectedReason,
			comment: comment,
			tags: tags.map((tag) => tag.name),
			details: {
				rating: detailedRating
			}
		});
		show = false;
	};
</script>

{#if message?.arena}
	<div class="text-xs font-medium pt-1.5 -mb-0.5">
		{$i18n.t('This response was generated by "{{model}}"', {
			model: selectedModel ? (selectedModel?.name ?? selectedModel.id) : message.selectedModelId
		})}
	</div>
{/if}

<div
	class=" my-2.5 rounded-xl px-4 py-3 border border-gray-50 dark:border-gray-850"
	id="message-feedback-{message.id}"
>
	<div>
		<div class="text-sm mt-1.5 py-2 font-medium">
			{$i18n.t('How would you rate this response?')}
		</div>
		<div class="flex flex-wrap gap-1.5 text-sm mt-1.5">
			{#each detailed_ratings as rating}
				<button
					class="px-3 py-2 border border-gray-400 text-sm items-center text-gray-600 dark:text-gray-400 rounded-full hover:text-gray-800 hover:border-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:border-gray-100 dark:hover:text-gray-100 {detailedRating ===
					rating
						? 'bg-gray-100 dark:bg-gray-800'
						: ''} transition rounded-xl"
					on:click={() => {
						detailedRating = rating;
					}}
				>
					{#if rating === 'bad'}
						{$i18n.t('Bad')}
					{:else if rating === 'very_bad'}
						{$i18n.t('Very bad')}
					{:else if rating === 'extremely_bad'}
						{$i18n.t('Extremely bad')}
					{:else}
						{rating}
					{/if}
				</button>
			{/each}
		</div>
	</div>

	<div>
		{#if reasons.length > 0}
			<div class="text-sm mt-1.5 py-2 font-medium">
				{$i18n.t("What didn't you like about this response?")}
			</div>

			<div class="flex flex-wrap gap-1.5 text-sm mt-1.5">
				{#each reasons as reason}
					<button
						class="px-3 py-2 border border-gray-400 text-sm items-center text-gray-600 dark:text-gray-400 rounded-full hover:text-gray-800 hover:border-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:border-gray-100 dark:hover:text-gray-100 {selectedReason ===
						reason
							? 'bg-gray-100 dark:bg-gray-800'
							: ''} transition rounded-xl"
						on:click={() => {
							selectedReason = reason;
						}}
					>
						{#if reason === 'harmful_or_offensive'}
							{$i18n.t('Harmful or offensive')}
						{:else if reason === 'not_relevant'}
							{$i18n.t('Not relevant')}
						{:else if reason === 'not_accurate'}
							{$i18n.t('Not accurate')}
						{:else if reason === 'incomplete_response'}
							{$i18n.t('Incomplete response')}
						{:else}
							{reason}
						{/if}
					</button>
				{/each}
			</div>
		{/if}
	</div>

	<div class="mt-2">
		<div class="text-sm mt-1.5 font-medium py-2" id="lbl-comment">
			{$i18n.t('Provide any specific details')}
		</div>
		<textarea
			bind:value={comment}
			class="w-full text-sm px-3 py-2 bg-transparent resize-none rounded-xl border border-gray-400 dark:border-gray-600"
			rows="3"
			aria-labelledby="lbl-comment"
		/>
	</div>

	<div class="flex items-end group">
		<Tags
			{tags}
			on:delete={(e) => {
				tags = tags.filter(
					(tag) =>
						tag.name.replaceAll(' ', '_').toLowerCase() !==
						e.detail.replaceAll(' ', '_').toLowerCase()
				);
			}}
			on:add={(e) => {
				tags = [...tags, { name: e.detail }];
			}}
		/>
	</div>
	<div class="mt-3 flex justify-end">
		<button
			class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			on:click={() => {
				saveHandler();
			}}
		>
			{$i18n.t('Save')}
		</button>
	</div>
</div>
