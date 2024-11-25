<script>
    import Charts from '$components/Charts.svelte';
    import stocksense from '$lib/stocksense';

    let endpoint = $state('');
    let symbol = $state('');
    let begin = $state('2024-10-31');
    let end = $state('2024-11-01');

    let dataUrl = $state(
        'https://raw.githubusercontent.com/ClementPerroud/Gym-Trading-Env/main/examples/data/BTC_USD-Hourly.csv'
    );
</script>

<main >
    <fieldset class="grid" aria-label="Choose data source">
        <label>
            Data Endpoint
            <select
                name="endpoint"
                aria-label="Choose data endpoint"
                required
                bind:value={endpoint}
            >
                <option selected disabled value=""> Choose data endpoint </option>
                {#await stocksense.getDataEndpoints() then eps}
                    {#each eps as ep}
                        <option value={ep}>{ep}</option>
                    {/each}
                {/await}
            </select>
        </label>
        <label>
            Symbol
            <select name="symbol" aria-label="Choose symbol" required bind:value={symbol}>
                <option selected disabled value=""> Choose symbol </option>
                {#if endpoint}
                    {#await stocksense.getSymbols(endpoint) then symbols}
                        {#each symbols as symbol}
                            <option value={symbol}>{symbol}</option>
                        {/each}
                    {/await}
                {/if}
            </select></label
        >
    </fieldset>
    <fieldset class="grid" aria-label="Choose data source">
        <label>
            Begin Date
            <input
                type="date"
                name="begin"
                aria-label="Choose begin date"
                required
                bind:value={begin}
            />
        </label>
        <label>
            End Date
            <input type="date" name="end" aria-label="Choose end date" required bind:value={end} />
        </label>
    </fieldset>
    <button
        type="button"
        onclick={async () => {
            dataUrl = stocksense.getKLinesUrl(endpoint, symbol, begin, end);
            console.log(dataUrl);
        }}
    >
        Get Data
    </button>
    <!-- <div> -->
    <Charts bind:dataUrl/>
    <!-- </div> -->
</main>

<style lang="sass">

</style>
