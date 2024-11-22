<!-- Script -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { createChart } from 'lightweight-charts';
    import type { IChartApi, ISeriesApi } from 'lightweight-charts';
    import { showAreaChart, showCandlestickChart, createToolTip, preprocessData } from '$lib/chartUtils';
    import ToolTip from '$components/ToolTip.svelte';

    let areaSeries: ISeriesApi<'Area'>;
    let candlestickSeries: ISeriesApi<'Candlestick'>;
    let chart: IChartApi;
    let state = { chart: "area" }; // area or kLine
    let url = "https://raw.githubusercontent.com/ClementPerroud/Gym-Trading-Env/main/examples/data/BTC_USD-Hourly.csv";

    onMount(async () => {
        const chartOptions = {
            layout: {
                textColor: 'black',
                background: { color: 'rgba(230, 230, 230, 1)' },
            },
        };
        chart = createChart(document.getElementById('container') as HTMLElement, chartOptions);

        chart.applyOptions({
            timeScale: { borderVisible: false, },
            rightPriceScale: { 
                borderVisible: false, 
                scaleMargins: { top: 0.1, bottom: 0.25, },
            },
            crosshair: {
                horzLine: { visible: false, labelVisible: false, },
                vertLine: { labelVisible: false, },
            },
            grid: {
                vertLines: { visible: false, },
                horzLines: { visible: false, },
            },
        });

        // create areaData
        let areaData = await preprocessData(url, "area");

        // build AreaChart
        areaSeries = chart.addAreaSeries({
            topColor: 'rgba( 38, 166, 154, 0.28)',
            bottomColor: 'rgba( 38, 166, 154, 0.05)',
            lineColor: 'rgba( 38, 166, 154, 1)',
            lineWidth: 2,
        });
    
        areaSeries.setData(areaData);

        // create Data
        let kLineData = await preprocessData(url, "kLine");

        // build KLineChart
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a', 
            downColor: '#ef5350', 
            borderVisible: false,
            wickUpColor: '#26a69a', 
            wickDownColor: '#ef5350',
        });
        
        candlestickSeries.setData(kLineData);
        

        chart.timeScale().fitContent();

        // default -> show only area chart
        candlestickSeries.applyOptions({ visible: false });

        // create tool tip
        createToolTip(state, areaSeries, candlestickSeries, chart);
    });

</script>

<!-- Style -->

<style>
    #container-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 400px;
    }

    #container {
        width: 800px;
        height: 400px;
    }

    #toggle-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
    }
</style>

<!-- MarkUp -->

<div id="container-wrapper">
    <div id="container">
        <ToolTip/>
    </div>
</div>
<div id="toggle-buttons">
    <button on:click={() => showAreaChart(state, areaSeries, candlestickSeries)}>AreaChart</button>
    <button on:click={() => showCandlestickChart(state, areaSeries, candlestickSeries)}>KLineChart</button>
</div>