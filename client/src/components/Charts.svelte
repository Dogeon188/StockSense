<!-- Script -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { createChart } from 'lightweight-charts';
    import type { IChartApi, ISeriesApi } from 'lightweight-charts';
    import {
        showAreaChart,
        showCandlestickChart,
        createToolTip,
        preprocessData,
    } from '$lib/chartUtils';
    import ToolTip from './ToolTip.svelte';

    let areaSeries: ISeriesApi<'Area'>;
    let candlestickSeries: ISeriesApi<'Candlestick'>;
    let chart: IChartApi;
    let ChartElement: HTMLElement;
    let state = { chart: 'area' }; // area or kLine
    let { dataUrl = $bindable('') } = $props();

    onMount(async () => {
        const chartOptions = {
            layout: {
                textColor: 'black',
                background: { color: 'rgba(230, 230, 230, 1)' },
            },
        };
        chart = createChart(ChartElement as HTMLElement, chartOptions);

        chart.applyOptions({
            timeScale: { borderVisible: false },
            rightPriceScale: {
                borderVisible: false,
                scaleMargins: { top: 0.1, bottom: 0.25 },
            },
            crosshair: {
                horzLine: { visible: false, labelVisible: false },
                vertLine: { labelVisible: false },
            },
            grid: {
                vertLines: { visible: false },
                horzLines: { visible: false },
            },
        });

        // create areaData
        let areaData = await preprocessData(dataUrl, 'area');

        // build AreaChart
        areaSeries = chart.addAreaSeries({
            topColor: 'rgba( 38, 166, 154, 0.28)',
            bottomColor: 'rgba( 38, 166, 154, 0.05)',
            lineColor: 'rgba( 38, 166, 154, 1)',
            lineWidth: 2,
        });

        areaSeries.setData(areaData);

        // create Data
        let kLineData = await preprocessData(dataUrl, 'kLine');

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

<!-- MarkUp -->

<div id="container-wrapper">
    <div bind:this={ChartElement} id="container">
        <ToolTip />
    </div>
</div>
<div id="toggle-buttons">
    <button onclick={() => showAreaChart(state, areaSeries, candlestickSeries)}>AreaChart</button>
    <button onclick={() => showCandlestickChart(state, areaSeries, candlestickSeries)}>KLineChart</button>
</div>

<!-- Style -->

<style>
    #container-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 400px;
    }

    #container {
        flex: 1;
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
