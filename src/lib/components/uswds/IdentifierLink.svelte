<script lang="ts">
	import '@uswds/uswds/css/uswds.css';

	export let text: string;
	export let href: string;
</script>

<li class="usa-identifier__required-links-item">
	<a {href} class="usa-identifier__required-link usa-link">{text}</a>
</li>
