<script lang="ts">
	import Bolt from '$lib/components/icons/Bolt.svelte';
	import { onMount, getContext, createEventDispatcher } from 'svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let suggestionPrompts = [];
	export let className = '';

	let prompts = [];

	$: prompts = (suggestionPrompts ?? [])
		.reduce((acc, current) => [...acc, ...[current]], [])
		.sort(() => Math.random() - 0.5);
</script>

{#if prompts.length > 0}
	<h2 class="mb-1 flex gap-1 text-sm font-medium items-center text-gray-600 dark:text-gray-400">
		<Bolt />
		{$i18n.t('Suggested prompts to get you started')}
	</h2>
{/if}

<div
	class=" h-40 max-h-full overflow-auto scrollbar-none {className} grid gap-2 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
>
	{#each prompts as prompt, promptIdx}
		<button
			class="flex flex-col flex-1 shrink-0 w-full justify-between px-1 py-2 rounded-xl bg-transparent"
			on:click={() => {
				dispatch('select', prompt.content);
			}}
		>
			<div>
				{#if prompt.title && prompt.title[0] !== ''}
					<div
						class="px-2 py-2 border border-gray-400 text-sm items-center text-gray-400 dark:text-gray-500 bg-transparent rounded-full hover:text-gray-800 hover:border-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:border-gray-100 dark:hover:text-gray-100 truncate text-overflow:ellipsis"
					>
						{prompt.title[0]}
					</div>
				{:else}
					<div
						class="font-medium dark:text-gray-300 dark:group-hover:text-gray-200 transition line-clamp-1"
					>
						{prompt.content}
					</div>
					<div class="text-xs text-gray-600 font-normal line-clamp-1">Prompt</div>
				{/if}
			</div>
		</button>
	{/each}
</div>
