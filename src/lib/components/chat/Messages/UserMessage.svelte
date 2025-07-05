<script lang="ts">
	import dayjs from 'dayjs';
	import { toast } from 'svelte-sonner';
	import { tick, getContext, onMount } from 'svelte';

	import { models, settings } from '$lib/stores';
	import { user as _user } from '$lib/stores';
	import { copyToClipboard as _copyToClipboard } from '$lib/utils';

	import Name from './Name.svelte';
	import ProfileImage from './ProfileImage.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import Markdown from './Markdown.svelte';
	import Image from '$lib/components/common/Image.svelte';

	import Edit from '$lib/components/icons/Edit.svelte';
	import Copy from '$lib/components/icons/Copy.svelte';
	import Delete from '$lib/components/icons/Delete.svelte';

	const i18n = getContext('i18n');

	export let user;

	export let history;
	export let messageId;

	export let siblings;

	export let showPreviousMessage: Function;
	export let showNextMessage: Function;

	export let editMessage: Function;
	export let deleteMessage: Function;

	export let isFirstMessage: boolean;
	export let readOnly: boolean;

	let edit = false;
	let editedContent = '';
	let messageEditTextAreaElement: HTMLTextAreaElement;

	let message = JSON.parse(JSON.stringify(history.messages[messageId]));
	$: if (history.messages) {
		if (JSON.stringify(message) !== JSON.stringify(history.messages[messageId])) {
			message = JSON.parse(JSON.stringify(history.messages[messageId]));
		}
	}

	const copyToClipboard = async (text) => {
		const res = await _copyToClipboard(text);
		if (res) {
			toast.success($i18n.t('Copying to clipboard was successful!'));
		}
	};

	const editMessageHandler = async () => {
		edit = true;
		editedContent = message.content;

		await tick();

		messageEditTextAreaElement.style.height = '';
		messageEditTextAreaElement.style.height = `${messageEditTextAreaElement.scrollHeight}px`;

		messageEditTextAreaElement?.focus();
	};

	const editMessageConfirmHandler = async (submit = true) => {
		editMessage(message.id, editedContent, submit);

		edit = false;
		editedContent = '';
	};

	const cancelEditMessage = () => {
		edit = false;
		editedContent = '';
	};

	const deleteMessageHandler = async () => {
		deleteMessage(message.id);
	};

	onMount(() => {
		// console.log('UserMessage mounted');
	});
</script>

<div class=" flex w-full user-message" dir={$settings.chatDirection} id="message-{message.id}">
	{#if !($settings?.chatBubble ?? true)}
		<div class={`flex-shrink-0 ${($settings?.chatDirection ?? 'LTR') === 'LTR' ? 'mr-3' : 'ml-3'}`}>
			<ProfileImage
				src={message.user
					? ($models.find((m) => m.id === message.user)?.info?.meta?.profile_image_url ??
						'/user.png')
					: (user?.profile_image_url ?? '/user.png')}
				className={'size-8'}
			/>
		</div>
	{/if}
	<div class="flex-auto w-0 max-w-full pl-1">
		{#if !($settings?.chatBubble ?? true)}
			<div>
				<Name>
					{#if message.user}
						{$i18n.t('You')}
						<span class=" text-gray-600 text-sm font-medium">{message?.user ?? ''}</span>
					{:else if $settings.showUsername || $_user.name !== user.name}
						{user.name}
					{:else}
						{$i18n.t('You')}
					{/if}

					{#if message.timestamp}
						<span
							class=" invisible group-hover:visible text-gray-400 text-xs font-medium uppercase ml-0.5 -mt-0.5"
						>
							{dayjs(message.timestamp).format($i18n.t('h:mm a'))}
						</span>
					{/if}
				</Name>
			</div>
		{/if}

		<div class="chat-{message.role} w-full min-w-full markdown-prose">
			{#if message.files}
				<div class="mt-2.5 mb-1 w-full flex flex-col justify-end gap-1 flex-wrap">
					{#each message.files as file}
						<div class={($settings?.chatBubble ?? true) ? 'self-end' : ''}>
							{#if file.type === 'image'}
								<Image src={file.url} imageClassName=" max-h-96 rounded-lg" />
							{:else}
								<FileItem
									item={file}
									url={file.url}
									name={file.name}
									type={file.type}
									size={file?.size}
									colorClassName="bg-white dark:bg-gray-850"
									className="max-w-full"
								/>
							{/if}
						</div>
					{/each}
				</div>
			{/if}

			{#if edit === true}
				<div class=" w-full bg-gray-50 dark:bg-gray-800 rounded-3xl px-5 py-3 mb-2">
					<div class="max-h-96 overflow-auto">
						<textarea
							id="message-edit-{message.id}"
							bind:this={messageEditTextAreaElement}
							class=" bg-transparent outline-none w-full resize-none"
							bind:value={editedContent}
							on:input={(e) => {
								e.target.style.height = '';
								e.target.style.height = `${e.target.scrollHeight}px`;
							}}
							on:keydown={(e) => {
								if (e.key === 'Escape') {
									document.getElementById('close-edit-message-button')?.click();
								}

								const isCmdOrCtrlPressed = e.metaKey || e.ctrlKey;
								const isEnterPressed = e.key === 'Enter';

								if (isCmdOrCtrlPressed && isEnterPressed) {
									document.getElementById('confirm-edit-message-button')?.click();
								}
							}}
						/>
					</div>

					<div class=" mt-2 mb-1 flex justify-between text-sm font-medium">
						<div>
							<button
								id="save-edit-message-button"
								class=" px-4 py-2 bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 border dark:border-gray-700 text-gray-700 dark:text-gray-200 transition rounded-3xl"
								on:click={() => {
									editMessageConfirmHandler(false);
								}}
							>
								{$i18n.t('Save')}
							</button>
						</div>

						<div class="flex space-x-1.5">
							<button
								id="close-edit-message-button"
								class="px-4 py-2 bg-white dark:bg-gray-900 hover:bg-gray-100 text-gray-800 dark:text-gray-100 transition rounded-3xl"
								on:click={() => {
									cancelEditMessage();
								}}
							>
								{$i18n.t('Cancel')}
							</button>

							<button
								id="confirm-edit-message-button"
								class=" px-4 py-2 bg-gray-900 dark:bg-white hover:bg-gray-850 text-gray-100 dark:text-gray-800 transition rounded-3xl"
								on:click={() => {
									editMessageConfirmHandler();
								}}
							>
								{$i18n.t('Send')}
							</button>
						</div>
					</div>
				</div>
			{:else}
				<div class="w-full">
					<div class="flex {($settings?.chatBubble ?? true) ? 'justify-end pb-1' : 'w-full'}">
						<div
							class="chat-message-user rounded-3xl {($settings?.chatBubble ?? true)
								? `max-w-[90%] px-5 py-2 dark:bg-gray-850 ${message.files ? 'rounded-tr-lg' : ''}`
								: ' w-full'}"
						>
							{#if message.content}
								<Markdown id={message.id} content={message.content} />
							{/if}
						</div>
					</div>

					<div
						class=" flex {($settings?.chatBubble ?? true)
							? 'justify-end'
							: ''}  text-gray-600 dark:text-gray-500"
					>
						{#if !($settings?.chatBubble ?? true)}
							{#if siblings.length > 1}
								<div class="flex self-center" dir="ltr">
									<button
										aria-label="show previous message"
										class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition"
										on:click={() => {
											showPreviousMessage(message);
										}}
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2.5"
											class="size-3.5"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M15.75 19.5 8.25 12l7.5-7.5"
											/>
										</svg>
									</button>

									<div class="text-sm tracking-widest font-semibold self-center dark:text-gray-100">
										{siblings.indexOf(message.id) + 1}/{siblings.length}
									</div>

									<button
										aria-label="show next message"
										class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition"
										on:click={() => {
											showNextMessage(message);
										}}
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2.5"
											class="size-3.5"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="m8.25 4.5 7.5 7.5-7.5 7.5"
											/>
										</svg>
									</button>
								</div>
							{/if}
						{/if}
						{#if !readOnly}
							<Tooltip content={$i18n.t('Edit')} placement="bottom">
								<button
									class="invisible group-hover:visible p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition edit-user-message-button"
									on:click={() => {
										editMessageHandler();
									}}
								>
									<!-- Edit icon -->
									<Edit className="size-[23px] text-steel-800" />
								</button>
							</Tooltip>
						{/if}

						<Tooltip content={$i18n.t('Copy')} placement="bottom">
							<button
								class="invisible group-hover:visible p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
								on:click={() => {
									copyToClipboard(message.content);
								}}
							>
								<!-- Copy icon -->
								<Copy />
							</button>
						</Tooltip>

						{#if !isFirstMessage && !readOnly}
							<Tooltip content={$i18n.t('Delete')} placement="bottom">
								<button
									class="invisible group-hover:visible p-1 rounded dark:hover:text-white hover:text-black transition"
									on:click={() => {
										deleteMessageHandler();
									}}
								>
									<!-- Delete icon -->

									<Delete className="size-5" strokeWidth="1.75" />
								</button>
							</Tooltip>
						{/if}

						{#if $settings?.chatBubble ?? true}
							{#if siblings.length > 1}
								<div class="flex self-center" dir="ltr">
									<button
										class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition"
										on:click={() => {
											showPreviousMessage(message);
										}}
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2.5"
											class="size-3.5"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M15.75 19.5 8.25 12l7.5-7.5"
											/>
										</svg>
									</button>

									<div class="text-sm tracking-widest font-semibold self-center dark:text-gray-100">
										{siblings.indexOf(message.id) + 1}/{siblings.length}
									</div>

									<button
										class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition"
										on:click={() => {
											showNextMessage(message);
										}}
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2.5"
											class="size-3.5"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="m8.25 4.5 7.5 7.5-7.5 7.5"
											/>
										</svg>
									</button>
								</div>
							{/if}
						{/if}
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
