<script lang="ts">
	import { getContext, onMount, tick } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');

	export let show = false;
	export let citation;
	export let showPercentage = false;
	export let showRelevance = true;

	let mergedDocuments = [];

	function calculatePercentage(distance: number) {
		if (distance < 0) return 100;
		if (distance > 1) return 0;
		return (1 - distance) * 100;
	}

	function getRelevanceColor(percentage: number) {
		if (percentage >= 80)
			return 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200';
		if (percentage >= 60)
			return 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200';
		if (percentage >= 40)
			return 'bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200';
		return 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200';
	}

	$: if (citation) {
		mergedDocuments = citation.document?.map((c, i) => {
			return {
				source: citation.source,
				document: c,
				metadata: citation.metadata?.[i],
				distance: citation.distances?.[i]
			};
		});
		if (mergedDocuments.every((doc) => doc.distance !== undefined)) {
			mergedDocuments = mergedDocuments.sort(
				(a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity)
			);
		}
	}

	let headingId = 'citations-heading';
</script>

<Modal size="lg" {headingId} bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<h2 class=" text-lg font-medium self-center capitalize" id={headingId}>
				{$i18n.t('Citation')}
			</h2>
		</div>

		<div class="flex flex-col md:flex-row w-full px-6 pb-5 md:space-x-4">
			<div
				class="flex flex-col w-full dark:text-gray-200 overflow-y-scroll max-h-[22rem] scrollbar-hidden"
			>
				{#each mergedDocuments as document, documentIdx}
					<div class="flex flex-col w-full">
						<div class="text-sm font-medium dark:text-gray-300">
							{$i18n.t('Source')}
						</div>

						{#if document.source?.name}
							<div class="text-sm dark:text-gray-400 flex items-center gap-2 w-fit">
								<a
									class="hover:text-gray-500 hover:dark:text-gray-100 underline flex-grow"
									href={document?.metadata?.file_id
										? `${WEBUI_API_BASE_URL}/files/${document?.metadata?.file_id}/content${document?.metadata?.page !== undefined ? `#page=${document.metadata.page + 1}` : ''}`
										: document.source?.url?.includes('http')
											? document.source.url
											: `#`}
									target="_blank"
								>
									{document?.metadata?.name ?? document.source.name}
								</a>

								{#if document?.metadata?.page}
									<span class="text-xs text-gray-600 dark:text-gray-400">
										({$i18n.t('page')}
										{document.metadata.page + 1})
									</span>
								{/if}
							</div>

							{#if showRelevance}
								<div class="text-sm font-medium dark:text-gray-300 mt-2">
									{$i18n.t('Relevance')}
								</div>
								{#if document.distance !== undefined}
									<Tooltip
										className="w-fit"
										content={$i18n.t('Semantic distance to query')}
										placement="top-start"
										tippyOptions={{ duration: [500, 0] }}
									>
										<div class="text-sm my-1 dark:text-gray-400 flex items-center gap-2 w-fit">
											{#if showPercentage}
												{@const percentage = calculatePercentage(document.distance)}
												<span class={`px-1 rounded font-medium ${getRelevanceColor(percentage)}`}>
													{percentage.toFixed(2)}%
												</span>
											{:else}
												<span class="text-gray-600 dark:text-gray-500">
													{document.distance.toFixed(4)}
												</span>
											{/if}
										</div>
									</Tooltip>
								{:else}
									<div class="text-sm dark:text-gray-400">
										{$i18n.t('No distance available')}
									</div>
								{/if}
							{/if}
						{:else}
							<div class="text-sm dark:text-gray-400">
								{$i18n.t('No source available')}
							</div>
						{/if}
					</div>
					<div class="flex flex-col w-full">
						<div class=" text-sm font-medium dark:text-gray-300 mt-2">
							{$i18n.t('Content')}
						</div>
						{#if document.metadata?.html}
							<iframe
								class="w-full border-0 h-auto rounded-none"
								sandbox="allow-scripts allow-forms allow-same-origin"
								srcdoc={document.document}
								title={$i18n.t('Content')}
							></iframe>
						{:else}
							<pre class="text-sm dark:text-gray-400 whitespace-pre-line">
                {document.document}
              </pre>
						{/if}
					</div>

					{#if documentIdx !== mergedDocuments.length - 1}
						<hr class=" dark:border-gray-850 my-3" />
					{/if}
				{/each}
			</div>
		</div>
	</div>
</Modal>
