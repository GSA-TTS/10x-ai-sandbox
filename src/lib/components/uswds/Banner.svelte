<script lang="ts">
	import usFlagSmall from '$lib/assets/uswds/us_flag_small.png';
	import iconDotGov from '$lib/assets/uswds/icon-dot-gov.svg';
	import iconHttps from '$lib/assets/uswds/icon-https.svg';
	import expandLess from '$lib/assets/uswds/expand_less.svg';
	import expandMore from '$lib/assets/uswds/expand_more.svg';

	let bannerExpanded = false;

	function toggleBanner() {
		bannerExpanded = !bannerExpanded;
	}
</script>

<section
	class="px-2 bg-[#f0f0f0] dark:bg-gray-800"
	aria-label="Official website of the United States government"
>
	<header class="flex flex-row items-stretch justify-start sm:justify-center gap-2 py-1.5">
		<img aria-hidden="true" class="h-[11px] leading-none" src={usFlagSmall} alt="" />
		<div class="flex flex-col sm:flex-row gap-2 items-start">
			<p class="text-xs leading-none">An official website of the United States government</p>
			<button
				type="button"
				class="text-xs leading-none flex flex-row"
				aria-expanded={bannerExpanded}
				aria-controls="gov-banner-default"
				on:click={toggleBanner}
			>
				<span class="text-blue-800 dark:text-blue-400 underline">Here’s how you know</span>
				<img
					src={bannerExpanded ? expandLess : expandMore}
					alt=""
					aria-hidden="true"
					class="h-[13px] dark:invert"
				/>
			</button>
		</div>
	</header>
	<div class="mx-auto py-8 max-w-5xl {bannerExpanded ? 'block' : 'hidden'}" id="gov-banner-default">
		<div class="flex flex-col sm:flex-row gap-4 text-sm">
			<div class="flex flex-row justify-start gap-2 flex-1">
				<img class="h-[40px] w-[40px]" src={iconDotGov} alt="" aria-hidden="true" />
				<p>
					<strong>Official websites use .gov</strong><br />A
					<strong>.gov</strong> website belongs to an official government organization in the United
					States.
				</p>
			</div>
			<div class="flex flex-row justify-start gap-2 flex-1">
				<img class="h-[40px] w-[40px]" src={iconHttps} alt="" aria-hidden="true" />
				<p>
					<strong>Secure .gov websites use HTTPS</strong><br />A
					<strong>lock</strong> (
					<span class=""
						><svg
							xmlns="http://www.w3.org/2000/svg"
							width="11"
							height="11"
							viewBox="0 0 52 64"
							class="inline dark:invert"
							role="img"
							aria-labelledby="banner-lock-description-default"
							focusable="false"
						>
							<title id="banner-lock-title-default">Lock</title>
							<desc id="banner-lock-description-default">Locked padlock icon</desc>
							<path
								fill="#000000"
								fill-rule="evenodd"
								d="M26 0c10.493 0 19 8.507 19 19v9h3a4 4 0 0 1 4 4v28a4 4 0 0 1-4 4H4a4 4 0 0 1-4-4V32a4 4 0 0 1 4-4h3v-9C7 8.507 15.507 0 26 0zm0 8c-5.979 0-10.843 4.77-10.996 10.712L15 19v9h22v-9c0-6.075-4.925-11-11-11z"
							/>
						</svg>
					</span>) or <strong>https://</strong> means you’ve safely connected to the .gov website. Share
					sensitive information only on official, secure websites.
				</p>
			</div>
		</div>
	</div>
</section>
