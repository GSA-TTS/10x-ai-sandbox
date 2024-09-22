<script>
	import { goto } from '$app/navigation';
	import { userSignIn, userSignInOauth, userSignUp } from '$lib/apis/auths';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user, socket } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { generateInitialsImage, canvasPixelTest } from '$lib/utils';

	const i18n = getContext('i18n');

	import { page } from '$app/stores';

	let loaded = false;
	let mode = 'signin';

	let name = '';
	let email = '';
	let password = '';
	let state = '';
	let code = '';
	let provider = '';

	const setSessionUser = async (sessionUser) => {
		if (sessionUser) {
			console.log('sessionUser:', sessionUser);
			toast.success($i18n.t(`You're now logged in.`));
			localStorage.token = sessionUser.token;

			$socket.emit('user-join', { auth: { token: sessionUser.token } });
			await user.set(sessionUser);
			goto('/');
		}
	};

	const signInHandler = async () => {
		const sessionUser = await userSignIn(email, password).catch((error) => {
			toast.error(error); // Error handled here
			return null; // sessionUser becomes null
		});

		if (sessionUser) {
			// Check if sessionUser is not null
			await setSessionUser(sessionUser); // Only called if sign-in was successful
		}
	};

	const signInHandlerOauth = async () => {
		const sessionUser = await userSignInOauth(state, code, provider).catch((error) => {
			toast.error(error); // Error handled here
			state = '';
			code = '';
			provider = '';
			goto('/auth');
		});

		if (sessionUser) {
			// Check if sessionUser is not null
			await setSessionUser(sessionUser); // Only called if sign-in was successful
		} else {
			console.log('sessionUser does not exist');
		}
	};

	const signUpHandler = async () => {
		const sessionUser = await userSignUp(name, email, password, generateInitialsImage(name)).catch(
			(error) => {
				toast.error(error); // Error handled here
				return null; // sessionUser becomes null
			}
		);

		if (sessionUser) {
			// Check if sessionUser is not null
			await setSessionUser(sessionUser); // Only called if sign-up was successful
		}
	};

	const submitHandler = async () => {
		if (mode === 'signin') {
			await signInHandler();
		} else {
			await signUpHandler();
		}
	};

	onMount(async () => {
		if ($user !== undefined) {
			await goto('/');
		}
		loaded = true;

		const params = $page.url.searchParams;
		if (params.has('state') && params.has('code') && params.has('provider')) {
			state = params.get('state') ?? '';
			code = params.get('code') ?? '';
			provider = params.get('provider') ?? '';
			if (state && code && provider) {
				await signInHandlerOauth();
			}
		}

		if (($config?.features.auth_trusted_header ?? false) || $config?.features.auth === false) {
			await signInHandler();
		}
	});
</script>

<svelte:head>
	<title>
		{`${$WEBUI_NAME}`}
	</title>
</svelte:head>

{#if loaded}
	<div class="fixed m-10 z-50">
		<div class="flex space-x-2">
			<div class=" self-center">
				<img
					crossorigin="anonymous"
					src="{WEBUI_BASE_URL}/static/favicon.png"
					class=" w-8 rounded-full"
					alt="logo"
				/>
			</div>
		</div>
	</div>

	<div class=" bg-white dark:bg-gray-950 min-h-screen w-full flex justify-center font-mona">
		<div class="w-full sm:max-w-md px-10 min-h-screen flex flex-col text-center">
			{#if code !== '' && state !== ''}
				<div class=" my-auto pb-10 w-full">
					<div
						class="flex items-center justify-center gap-3 text-xl sm:text-2xl text-center font-medium dark:text-gray-200"
					>
						<div>
							{$i18n.t('Signing in')}
							{$i18n.t('to')}
							{$WEBUI_NAME}
						</div>

						<div>
							<Spinner />
						</div>
					</div>
				</div>
			{:else}
				<div class="  my-auto pb-10 w-full dark:text-gray-100">
					<form
						class=" flex flex-col justify-center"
						on:submit|preventDefault={() => {
							submitHandler();
						}}
					>
						<div class="mb-1 pb-10">
							<div class=" text-2xl font-medium">
								{$WEBUI_NAME}
								<br /><span>powered by 10x</span>
							</div>

							{#if mode === 'signup'}
								<div class=" mt-1 text-xs font-medium text-gray-500">
									ⓘ {$WEBUI_NAME}
									{$i18n.t(
										'does not make any external connections outside of GSA govcloud, and your data is stored securely on cloud.gov.'
									)}
								</div>
							{/if}
						</div>
						<div class="mb-1">
							<a
								href="{WEBUI_BASE_URL}/authorize/cloudgov"
								class="inline-block bg-gray-900 hover:bg-gray-800 w-full rounded-2xl text-white font-medium text-sm py-3 transition text-center"
							>
								{'Sign in with Cloud.gov'}
							</a>
						</div>
						<div class="mb-1">
							<a
								href="{WEBUI_BASE_URL}/authorize/github"
								class="inline-block bg-gray-900 hover:bg-gray-800 w-full rounded-2xl text-white font-medium text-sm py-3 transition text-center"
							>
								{'Sign in with Github'}
							</a>
						</div>
					</form>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.font-mona {
		font-family: 'Mona Sans', -apple-system, 'Arimo', ui-sans-serif, system-ui, 'Segoe UI', Roboto,
			Ubuntu, Cantarell, 'Noto Sans', sans-serif, 'Helvetica Neue', Arial, 'Apple Color Emoji',
			'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
	}
</style>
