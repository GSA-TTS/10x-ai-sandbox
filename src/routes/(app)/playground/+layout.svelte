<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { WEBUI_NAME, showSidebar, functions } from '$lib/stores';
	import MenuLines from '$lib/components/icons/MenuLines.svelte';
	import { page } from '$app/stores';
	import { MAIN_CONTENT_ID as mainContentId } from '$lib/constants';

	const i18n = getContext('i18n');

	onMount(async () => {});
</script>

<svelte:head>
	<title>
		{$i18n.t('Playground')} | {$WEBUI_NAME}
	</title>
</svelte:head>

<svelte:element
	this={mainContentId ? 'main' : 'div'}
	id={mainContentId}
	class=" flex flex-col w-full h-screen max-h-[100dvh] {$showSidebar
		? 'md:max-w-[calc(100%-260px)]'
		: ''}"
>
	<div class=" px-2.5 py-1 backdrop-blur-xl">
		<div class=" flex items-center">
			<div class="{$showSidebar ? 'md:hidden' : ''} flex flex-none items-center">
				<button
					id="sidebar-toggle-button"
					class="cursor-pointer p-1.5 flex rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition"
					on:click={() => {
						showSidebar.set(!$showSidebar);
					}}
					aria-expanded={$showSidebar}
					aria-label="Toggle Sidebar"
				>
					<div class=" m-auto self-center">
						<MenuLines />
					</div>
				</button>
			</div>

			<div class=" flex w-full">
				<div
					class="flex gap-1 scrollbar-none overflow-x-auto w-fit text-center text-sm font-medium rounded-full bg-transparent pt-1"
				>
					<a
						class="min-w-fit rounded-full p-1.5 {['/playground', '/playground/'].includes(
							$page.url.pathname
						)
							? ''
							: 'text-gray-600 dark:text-gray-500 hover:text-gray-700 dark:hover:text-white'} transition"
						href="/playground">{$i18n.t('Chat')}</a
					>

					<!-- <a
						class="min-w-fit rounded-full p-1.5 {$page.url.pathname.includes('/playground/notes')
							? ''
							: 'text-gray-600 dark:text-gray-500 hover:text-gray-700 dark:hover:text-white'} transition"
						href="/playground/notes">{$i18n.t('Notes')}</a
					> -->

					<a
						class="min-w-fit rounded-full p-1.5 {$page.url.pathname.includes(
							'/playground/completions'
						)
							? ''
							: 'text-gray-600 dark:text-gray-500 hover:text-gray-700 dark:hover:text-white'} transition"
						href="/playground/completions">{$i18n.t('Completions')}</a
					>
				</div>
			</div>
		</div>
	</div>

	<div class=" flex-1 max-h-full overflow-y-auto">
		<slot />
	</div>
</svelte:element>
