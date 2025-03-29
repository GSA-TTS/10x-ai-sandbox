<script>
	import {
		addTagById,
		deleteTagById,
		getAllTags,
		getChatList,
		getChatListByTagName,
		getTagsById,
		updateChatById
	} from '$lib/apis/chats';
	import {
		tags as _tags,
		chats,
		pinnedChats,
		currentChatPage,
		scrollPaginationEnabled
	} from '$lib/stores';
	import { createEventDispatcher, onMount } from 'svelte';

	const dispatch = createEventDispatcher();

	import Tags from '../common/Tags.svelte';
	import { toast } from 'svelte-sonner';

	export let chatId = '';
	let tags = [];

	const getTags = async () => {
		return await getTagsById(chatId).catch(async (error) => {
			return [];
		});
	};

	const addTag = async (tagName) => {
		const res = await addTagById(chatId, tagName).catch(async (error) => {
			toast.error(error);
			return null;
		});
		if (!res) {
			return;
		}

		tags = await getTags();
		await updateChatById(chatId, {
			tags: tags
		});

		await _tags.set(await getAllTags());
		dispatch('add', {
			name: tagName
		});
	};

	const deleteTag = async (tagName) => {
		const res = await deleteTagById(chatId, tagName);
		tags = await getTags();
		await updateChatById(chatId, {
			tags: tags
		});

		await _tags.set(await getAllTags());
		dispatch('delete', {
			name: tagName
		});
	};

	onMount(async () => {
		if (chatId) {
			tags = await getTags();
		}
	});
</script>

<Tags
	{tags}
	on:delete={(e) => {
		deleteTag(e.detail);
	}}
	on:add={(e) => {
		addTag(e.detail);
	}}
/>
