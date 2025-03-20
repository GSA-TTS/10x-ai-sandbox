<script lang="ts">
	export let logo = '';
	export let domain = '';
	export let agency = 'U.S. government';
	export let agencyLink = '#';
	export let showUsaGovSection = true;
</script>

<div class="flex flex-row justify-center px-2 bg-[#1b1b1b] text-white">
	<div class="flex flex-col my-8 space-y-8">
		<section class="flex flex-col sm:flex-row gap-4 sm:items-end" aria-label="Agency identifier,">
			{#if logo}
				<a href={agencyLink}><img class="h-12 w-12" src={logo} alt="{agency} logo" /></a>
			{/if}
			<section aria-label="Agency description,">
				{#if domain}<p class="text-[#a9aeb1]">{domain}</p>{/if}
				<p class="font-bold">
					<span aria-hidden="true">An </span>official website of the
					<a href={agencyLink}>{agency}</a>
				</p>
			</section>
		</section>
		<nav class="" aria-label="Important links,">
			<ul class="flex flex-col sm:grid sm:grid-cols-4 gap-6">
				<slot />
			</ul>
		</nav>
		{#if showUsaGovSection}
			<section aria-label="U.S. government information and services,">
				<div class="inline-block">Looking for U.S. government information and services?</div>
				<a href="https://www.usa.gov/" class="font-bold underline">Visit USA.gov</a>
			</section>
		{/if}
	</div>
</div>
