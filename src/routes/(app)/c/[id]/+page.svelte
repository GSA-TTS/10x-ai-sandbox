<script lang="ts">
	import { page } from '$app/stores';
	import { MAIN_CONTENT_ID as mainContentId } from '$lib/constants';

	import Chat from '$lib/components/chat/Chat.svelte';
	import Help from '$lib/components/layout/Help.svelte';
</script>

<Chat chatIdProp={$page.params.id} {mainContentId} />
