<script lang="ts">
	import Chat from '$lib/components/chat/Chat.svelte';
	import Help from '$lib/components/layout/Help.svelte';
	import { MAIN_CONTENT_ID as mainContentId } from '$lib/constants';
</script>

<Chat {mainContentId} />
