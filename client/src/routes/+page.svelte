<script>
    import Charts from '$components/Charts.svelte';
    import SymbolSelector from '$components/SymbolSelector.svelte';

    let dataUrl = $state('https://raw.githubusercontent.com/ClementPerroud/Gym-Trading-Env/main/examples/data/BTC_USD-Hourly.csv');
</script>

<main >
    <SymbolSelector bind:dataUrl/>    
    <Charts bind:dataUrl/>
</main>

<style lang="sass">

</style>
