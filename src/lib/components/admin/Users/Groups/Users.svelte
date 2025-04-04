<script lang="ts">
	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import Checkbox from '$lib/components/common/Checkbox.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import { searchUsers } from '$lib/apis/users';
	import { toast } from 'svelte-sonner';

	export let users = [];
	export let userIds = [];
	let filteredUsers = [];

	const submitSearchHandler = async () => {
		const res = await searchUsers(query).catch((error) => {
			toast.error(error);
			return null;
		});

		if (res) {
			users = res;
		}
	};

	$: filteredUsers = users
		.filter((user) => {
			if (user?.role === 'admin') {
				return false;
			}

			if (query === '') {
				return true;
			}

			return true;
		})
		.sort((a, b) => {
			const aUserIndex = userIds.indexOf(a.id);
			const bUserIndex = userIds.indexOf(b.id);

			// Compare based on userIds or fall back to alphabetical order
			if (aUserIndex !== -1 && bUserIndex === -1) return -1; // 'a' has valid userId -> prioritize
			if (bUserIndex !== -1 && aUserIndex === -1) return 1; // 'b' has valid userId -> prioritize

			// Both a and b are either in the userIds array or not, so we'll sort them by their indices
			if (aUserIndex !== -1 && bUserIndex !== -1) return aUserIndex - bUserIndex;

			// If both are not in the userIds, fallback to alphabetical sorting by name
			return a.name.localeCompare(b.name);
		});

	let query = '';
</script>

<div>
	<div class="flex w-full">
		<div class="flex flex-1 justify-end pb-2.5 border-b-[lightgrey] border-b border-solid">
			<form
				class="flex"
				on:submit={(e) => {
					e.preventDefault();
					submitSearchHandler();
				}}
			>
				<input
					class=" w-full text-sm pr-4 rounded-r-xl outline-none bg-transparent"
					bind:value={query}
					placeholder={$i18n.t('Search users')}
				/>
				<Tooltip content={$i18n.t('Search users')}>
					<button
						type="submit"
						class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full flex flex-row space-x-1 items-center break-normal"
						>Search
					</button>
				</Tooltip>
			</form>
		</div>
	</div>

	<div class="mt-3 max-h-[22rem] overflow-y-auto scrollbar-hidden">
		<div class="flex flex-col gap-2.5">
			{#if filteredUsers.length > 0}
				{#each filteredUsers as user, userIdx (user.id)}
					<div class="flex flex-row items-center gap-3 w-full text-sm">
						<div class="flex items-center">
							<Checkbox
								state={userIds.includes(user.id) ? 'checked' : 'unchecked'}
								on:change={(e) => {
									if (e.detail === 'checked') {
										userIds = [...userIds, user.id];
									} else {
										userIds = userIds.filter((id) => id !== user.id);
									}
								}}
							/>
						</div>

						<div class="flex w-full items-center justify-between">
							<Tooltip content={user.email} placement="top-start">
								<div class="flex">
									<img
										class=" rounded-full size-5 object-cover mr-2.5"
										src={user.profile_image_url.startsWith(WEBUI_BASE_URL) ||
										user.profile_image_url.startsWith('https://www.gravatar.com/avatar/') ||
										user.profile_image_url.startsWith('data:')
											? user.profile_image_url
											: `/user.png`}
										alt="user"
									/>

									<div class=" font-medium self-center">{user.name}</div>
								</div>
							</Tooltip>

							{#if userIds.includes(user.id)}
								<Badge type="success" content="member" />
							{/if}
						</div>
					</div>
				{/each}
			{:else}
				<div class="text-gray-600 dark:text-gray-500 text-xs text-center py-2 px-10">
					{$i18n.t('No users were found.')}
				</div>
			{/if}
		</div>
	</div>
</div>
