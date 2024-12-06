<script lang="ts">
    import stocksense from '$lib/stocksense';

    let { dataUrl = $bindable('') } = $props();

    let endpoint = $state('');
    let symbol = $state('');
    let symbolAvailable = $derived(endpoint !== '');
    let begin = $state('2017-01-01');
    let end = $state('2024-11-01');
</script>

<fieldset class="grid" aria-label="Choose data source">
    <label>
        Data Endpoint
        <select name="endpoint" aria-label="Choose data endpoint" required bind:value={endpoint}>
            <option selected value=""> Choose data endpoint </option>
            {#await stocksense.getDataEndpoints() then eps}
                {#each eps as ep}
                    <option value={ep}>{ep}</option>
                {/each}
            {/await}
        </select>
    </label>
    <label>
        Symbol
        <select name="symbol" aria-label="Choose symbol" required bind:value={symbol} disabled={!symbolAvailable}>
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
    }}
>
    Get Data
</button>
