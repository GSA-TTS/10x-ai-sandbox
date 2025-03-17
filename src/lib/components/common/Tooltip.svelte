<script lang="ts">
	import DOMPurify from 'dompurify';

	import { onDestroy } from 'svelte';
	import { marked } from 'marked';

	import tippy from 'tippy.js';
	import { roundArrow } from 'tippy.js';

	export let placement = 'top';
	export let content = `I'm a tooltip!`;
	export let touch = true;
	export let className = 'flex';
	export let theme = '';
	export let allowHTML = true;
	export let tippyOptions = {};

	let tooltipElement;
	let tooltipInstance;

	$: if (tooltipElement && content) {
		if (tooltipInstance) {
			tooltipInstance.setContent(DOMPurify.sanitize(content));
		} else {
			tooltipInstance = tippy(tooltipElement, {
				content: DOMPurify.sanitize(content),
				placement: placement,
				allowHTML: allowHTML,
				touch: touch,
				...(theme !== '' ? { theme } : { theme: 'dark' }),
				arrow: false,
				offset: [0, 4],
				...tippyOptions
			});
		}
	} else if (tooltipInstance && content === '') {
		if (tooltipInstance) {
			tooltipInstance.destroy();
		}
	}

	onDestroy(() => {
		if (tooltipInstance) {
			tooltipInstance.destroy();
		}
	});
</script>

<!-- removing aria-label from tooltips because the way OpenwebUI uses them isn't how tooltips should be used -->
<div bind:this={tooltipElement} class={className}>
	<slot />
</div>
