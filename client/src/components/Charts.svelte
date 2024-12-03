<!-- Script -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { createChart } from 'lightweight-charts';
    import type { IChartApi, ISeriesApi, TickMarkType, Time } from 'lightweight-charts';
    import {
        showAreaChart,
        showCandlestickChart,
        createToolTip,
        preprocessData,
        LWCTime2Date,
    } from '$lib/chartUtils';
    import ToolTip from './ToolTip.svelte';

    let { dataUrl = $bindable('') } = $props();

    let areaSeries: ISeriesApi<'Area'>;
    let candlestickSeries: ISeriesApi<'Candlestick'>;
    let chart: IChartApi;
    let chartContainer: HTMLElement;
    let chartState = { chart: 'area' }; // area or kLine
    let tooltipEl: HTMLDivElement = $state(null)!;

    onMount(async () => {
        const chartOptions = {
            layout: {
                textColor: 'black',
                background: { color: 'rgba(230, 230, 230, 1)' },
            },
        };
        chart = createChart(chartContainer as HTMLElement, chartOptions);

        chart.applyOptions({
            autoSize: true,
            timeScale: {
                tickMarkFormatter: (time: Time, tickMarkType: TickMarkType, locale: string) => {
                    const date = LWCTime2Date(time);
                    switch (tickMarkType) {
                        case 0: // TickMarkType.Year
                        case 1: // TickMarkType.Month
                        case 2: // TickMarkType.DayOfMonth
                            return date.toLocaleDateString(locale);
                        case 3: // TickMarkType.Time
                        case 4: // TickMarkType.TimeWithSeconds
                            return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
                        default:
                            return '';
                    }
                },
                timeVisible: true,
                secondsVisible: false
            },
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

        // build AreaChart
        areaSeries = chart.addAreaSeries({
            topColor: 'rgba( 38, 166, 154, 0.28)',
            bottomColor: 'rgba( 38, 166, 154, 0.05)',
            lineColor: 'rgba( 38, 166, 154, 1)',
            lineWidth: 2,
        });

        // build KLineChart
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        });

        chart.timeScale().fitContent();

        // default -> show only area chart
        candlestickSeries.applyOptions({ visible: false });

        // create tool tip
        createToolTip(chartContainer, tooltipEl, chartState, areaSeries, candlestickSeries, chart);
    });

    $effect(() => {
        if (dataUrl) {
            (async () => {
                let data = await preprocessData(dataUrl);
                areaSeries.setData(data);
                candlestickSeries.setData(data);
                chart.timeScale().fitContent();
            })();
        }
    });
</script>

<!-- MarkUp -->

<div>
    <div bind:this={chartContainer} class="container chart-container">
        <ToolTip bind:tooltipEl />
    </div>
    <div class="container toggle-buttons" role="group">
        <button onclick={() => showAreaChart(chartState, areaSeries, candlestickSeries)}
            >AreaChart</button
        >
        <button onclick={() => showCandlestickChart(chartState, areaSeries, candlestickSeries)}
            >KLineChart</button
        >
    </div>
</div>

<!-- Style -->

<style>
    .chart-container {
        width: 100%;
        height: 400px;
    }

    .toggle-buttons {
        width: auto;
    }
</style>
