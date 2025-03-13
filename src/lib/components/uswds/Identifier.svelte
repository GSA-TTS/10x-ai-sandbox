<script lang="ts">
	import '@uswds/uswds/css/uswds.css';

	export let logo = '';
	export let domain = '';
	export let agency = 'U.S. government';
	export let agencyLink = '#';
	export let showUsaGovSection = true;
</script>

<div class="usa-identifier">
	<section
		class="usa-identifier__section usa-identifier__section--masthead"
		aria-label="Agency identifier,"
	>
		<div class="usa-identifier__container">
			{#if logo}
				<div class="usa-identifier__logos">
					<a href={agencyLink} class="usa-identifier__logo"
						><img
							class="usa-identifier__logo-img"
							src={logo}
							alt="&lt;Parent agency&gt; logo"
							role="img"
						/></a
					>
				</div>
			{/if}
			<section class="usa-identifier__identity" aria-label="Agency description,">
				{#if domain}<p class="usa-identifier__identity-domain">{domain}</p>{/if}
				<p class="usa-identifier__identity-disclaimer">
					<span aria-hidden="true">An </span>official website of the
					<a href={agencyLink}>{agency}</a>
				</p>
			</section>
		</div>
	</section>
	<nav
		class="usa-identifier__section usa-identifier__section--required-links"
		aria-label="Important links,"
	>
		<div class="usa-identifier__container">
			<ul class="usa-identifier__required-links-list">
				<slot />
			</ul>
		</div>
	</nav>
	{#if showUsaGovSection}
		<section
			class="usa-identifier__section usa-identifier__section--usagov"
			aria-label="U.S. government information and services,"
		>
			<div class="usa-identifier__container">
				<div class="usa-identifier__usagov-description">
					Looking for U.S. government information and services?
				</div>
				<a href="https://www.usa.gov/" class="usa-link">Visit USA.gov</a>
			</div>
		</section>
	{/if}
</div>
