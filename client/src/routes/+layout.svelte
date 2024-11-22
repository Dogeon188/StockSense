<script lang="ts">
    import SettingsModal from '$components/SettingsModal.svelte';
    import '../app.sass';

    let { children } = $props();
    let showSettings = $state(false);
</script>

<SettingsModal bind:showSettings />

<header>
    <h1>StockSense</h1>
    <nav>
        <a href="/">Home</a>
        <button onclick={() => (showSettings = true)}>Settings</button>
    </nav>
</header>
<main>
    {@render children()}
</main>

<style lang="sass">
    header
        display: flex
        justify-content: space-between
        align-items: center

        nav
            display: flex
            justify-content: space-between
            align-items: center
            a
                color: inherit
                text-decoration: none
                margin-right: 1em
</style>
