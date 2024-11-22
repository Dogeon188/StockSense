<script lang="ts">
    import '../app.sass';
    import Modal from '$components/Modal.svelte';
    import { UserConfig } from '$lib/userConfig';

    let { showSettings = $bindable() } = $props();
    let apiUrl = $state(UserConfig.get('apiUrl')!);
    let urlValid = $derived(
        apiUrl?.match(/^https?:\/\/[a-z0-9-]+(\.[a-z0-9-]+)*(:[0-9]+)?(\/.*)?$/i)
    );
</script>

<Modal
    bind:showModal={showSettings}
    onclose={() => {
        showSettings = false;
        if (apiUrl) localStorage.setItem('apiUrl', apiUrl);
        else apiUrl = UserConfig.get('apiUrl')!;
    }}
>
    {#snippet header()}
        <h2>Settings</h2>
    {/snippet}
    <label>
        API URL
        <input
            type="url"
            placeholder="https://api.stocksense.com"
            bind:value={apiUrl}
            aria-invalid={!urlValid}
        />
    </label>
</Modal>
