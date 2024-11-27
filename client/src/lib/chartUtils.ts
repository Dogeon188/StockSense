import type { ISeriesApi, IChartApi, UTCTimestamp, Time } from 'lightweight-charts';
import * as d3 from 'd3';

export async function preprocessData(url: string) {
    let data = await d3.csv(url);
    return data
        .map((d) => ({
            time: new Date(d.date).getTime() as UTCTimestamp,
            open: Number(d.open),
            high: Number(d.high),
            low: Number(d.low),
            close: Number(d.close),
            value: Number(d.close),
        }))
        .sort((a, b) => a.time - b.time);
}

export function LWCTime2Date(time: Time) {
    return typeof time === 'number'
        ? new Date(time)
        : typeof time === 'string'
          ? new Date(time)
          : new Date(`${time.year}-${time.month}-${time.day}`);
}

// show AreaChart
export function showAreaChart(
    state: { chart: string },
    areaSeries: ISeriesApi<'Area'>,
    candlestickSeries: ISeriesApi<'Candlestick'>
) {
    state.chart = 'area';
    areaSeries.applyOptions({ visible: true });
    candlestickSeries.applyOptions({ visible: false });
}

// show KLineChart
export function showCandlestickChart(
    state: { chart: string },
    areaSeries: ISeriesApi<'Area'>,
    candlestickSeries: ISeriesApi<'Candlestick'>
) {
    state.chart = 'kLine';
    areaSeries.applyOptions({ visible: false });
    candlestickSeries.applyOptions({ visible: true });
}

export function createToolTip(
    container: HTMLElement,
    tooltipEl: HTMLElement,
    state: { chart: string },
    areaSeries: ISeriesApi<'Area'>,
    candlestickSeries: ISeriesApi<'Candlestick'>,
    chart: IChartApi
) {
    // Create and style the tooltip html element
    const toolTipWidth = tooltipEl.clientWidth;
    const toolTipHeight = tooltipEl.clientHeight;
    const toolTipMargin = 5;

    // update tooltip
    chart.subscribeCrosshairMove((param) => {
        if (
            param.point === undefined ||
            !param.time ||
            param.point.x < 0 ||
            param.point.x > container.clientWidth ||
            param.point.y < 0 ||
            param.point.y > container.clientHeight
        )
            tooltipEl.style.display = 'none';
        else {
            tooltipEl.style.display = 'block';
            const date = LWCTime2Date(param.time);
            const dateStr = `${date.toLocaleDateString()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
            interface SeriesData {
                open: number;
                high: number;
                low: number;
                close: number;
                time: string | number;
                value: number;
            }
            const data =
                state.chart === 'area'
                    ? param.seriesData.get(areaSeries) as SeriesData
                    : param.seriesData.get(candlestickSeries) as SeriesData;
            const formatter = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            });
            if (state.chart === 'area') {
                tooltipEl.innerHTML = `
                <div style="text-align: center;">
                    ${formatter.format(data.value)}
                </div>
                <div style="font-size: 8px; color: ${'gray'}; text-align: center; margin-top: 5px;">
                    ${dateStr}
                </div>`;
            }
            else {
                const color = data.close >= data.open ? '#26a69a' : '#ef5350';
                const items = [
                    { label: '開', value: data.open },
                    { label: '高', value: data.high },
                    { label: '低', value: data.low },
                    { label: '收', value: data.close }
                ];
                tooltipEl.innerHTML =
                    `${items.map(item =>
                        `<div>
                            ${item.label} = 
                            <span style="color: ${color};">
                                ${formatter.format(item.value)}
                            </span>
                        </div>`
                    ).join('')}
                    <div style="font-size: 8px; color: gray; text-align: center; margin-top: 5px;">
                        ${dateStr}
                    </div>`;
            }

            const containerRect = container.getBoundingClientRect();
            let left = param.point.x + containerRect.left + window.scrollX;
            let top = param.point.y + containerRect.top + window.scrollY;

            tooltipEl.style.left = left + 'px';
            tooltipEl.style.top = top + 'px';
        }
    });
}
