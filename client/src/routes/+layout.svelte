<script lang="ts">
    import SettingsModal from '$components/SettingsModal.svelte';
    import '../app.sass';

    let { children } = $props();
    let showSettings = $state(false);
</script>

<SettingsModal bind:showSettings />

<header>
    <nav>
        <ul>
            <li><h2>StockSense</h2></li>
        </ul>
        <ul>
            <li><a href="/" class="contrast">Home</a></li>
            <li><button onclick={() => (showSettings = true)}>Settings</button></li>
        </ul>
    </nav>
</header>
<main>
    {@render children()}
</main>
