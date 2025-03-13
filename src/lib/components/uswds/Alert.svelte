<script lang="ts">
	import '@uswds/uswds/css/uswds.css';

	// USWDS official variants
	export let type: 'info' | 'warning' | 'success' | 'error' | 'emergency';
	export let heading = '';
	export let slim = false;
	export let icon = true;

	// Custom variants (not part of USWDS)
	export let border = true;
	export let centered = false;
	export let margins = true;

	let variations = '';
	if (slim) variations += ' usa-alert--slim';
	if (!icon) variations += ' usa-alert--no-icon';

	if (!border) variations += ' noborder';
	if (centered) variations += ' centered';
	if (!margins) variations += ' nomargins';
</script>

<div class="usa-alert usa-alert--{type} {variations}">
	<div class="usa-alert__body">
		{#if heading}<h4 class="usa-alert__heading">{heading}</h4>{/if}
		<p class="usa-alert__text">
			<slot />
		</p>
	</div>
</div>

<style lang="postcss">
	.noborder {
		border-left: none;
	}

	.centered {
		display: flex;
		flex-direction: row;
		justify-content: center;
	}

	.nomargins {
		margin: 0;
	}
</style>
