<script lang="ts">
	export let data;
</script>

<svelte:head>
	<title>Test External Chat</title>
</svelte:head>

<p>Tests creating a new chat based on a HTML form submission.</p>

<div class="container">
	<form action="/api/v1/chats/new/external" method="post">
		<h2>Start a New Chat</h2>
		<div>
			<label for="message">Message:</label><br />
			<textarea id="message" name="message" required></textarea>
		</div>
		<div>
			<label for="model">Model:</label>
			<select id="model" name="model" required>
				{#each data.models as model}
					<option value={model.id}>{model.name}</option>
				{/each}
			</select>
		</div>
		<div>
			<input type="checkbox" id="web_search" name="web_search" value="true" />
			<label for="web_search">Enable Web Search</label>
		</div>
		<button type="submit">Start Chat</button>
	</form>
</div>

<style>
	.container {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		margin: 0;
	}
	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 2rem;
		border: 1px solid #ccc;
		border-radius: 8px;
	}
	textarea {
		width: 300px;
		height: 100px;
	}
	button {
		cursor: pointer;
	}
</style>
