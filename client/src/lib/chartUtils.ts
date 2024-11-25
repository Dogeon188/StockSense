import type { ISeriesApi, IChartApi } from 'lightweight-charts';
import * as d3 from 'd3';

export async function preprocessData(url: string, type: string) {
    let data = await d3.csv(url);
    let list = [];
    let prev = '';
    for (let i = data.length - 1; i >= 0; i--) {
        let pair =
            type === 'area'
                ? { time: data[i].date.split(' ')[0], value: Number(data[i].close) }
                : {
                      time: data[i].date.split(' ')[0],
                      open: Number(data[i].open),
                      high: Number(data[i].high),
                      low: Number(data[i].low),
                      close: Number(data[i].close),
                  };
        if (pair.time !== prev) {
            list.push(pair);
            prev = pair.time;
        }
    }
    return list;
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
    state: { chart: string },
    areaSeries: ISeriesApi<'Area'>,
    candlestickSeries: ISeriesApi<'Candlestick'>,
    chart: IChartApi
) {
    // create toolTip
    const container = document.getElementById('container');
    // Create and style the tooltip html element
    const toolTip = document.getElementById('toolTip');
    if (!container || !toolTip) return;
    const toolTipWidth = toolTip.clientWidth;
    const toolTipHeight = toolTip.clientHeight;
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
            toolTip.style.display = 'none';
        else {
            toolTip.style.display = 'block';
            const dateStr = param.time;
            const data =
                state.chart === 'area'
                    ? param.seriesData.get(areaSeries)
                    : param.seriesData.get(candlestickSeries);
            const formatter = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            });
            if (data === undefined) return;
            if (state.chart === 'area') {
                toolTip.innerHTML = `<div>
                    ${
                        // @ts-ignore
                        formatter.format(data.value)
                    }
                    </div>
                    <div style="font-size: 8px; color: ${'gray'}; text-align: center; "margin-top: 5px;"">
                    ${dateStr}
                    </div>`;
            } else {
                // @ts-ignore
                const color = data.close >= data.open ? '#26a69a' : '#ef5350';

                toolTip.innerHTML = `<div>開 = 
                        <span style="color: ${color};">
                            ${
                                // @ts-ignore
                                formatter.format(data.open)
                            }
                        </span>
                    </div>
                    <div>高 = 
                        <span style="color: ${color};">
                            ${
                                // @ts-ignore
                                formatter.format(data.high)
                            }
                        </span>
                    </div>
                    <div>低 = 
                        <span style="color: ${color};">
                            ${
                                // @ts-ignore
                                formatter.format(data.low)
                            }
                        </span>
                    </div>
                    <div>收 = 
                        <span style="color: ${color};">
                            ${
                                // @ts-ignore
                                formatter.format(data.close)
                            }
                        </span>
                    </div>
                    <div style="font-size: 8px; color: ${'gray'}; text-align: center; "margin-top: 5px;"">
                    ${dateStr}
                    </div>`;
            }

            let left = param.point.x + container.getClientRects()[0].x;
            // if (left > container.clientWidth + container.getClientRects()[0].x - toolTipWidth) {
            //     left =
            //         param.point.x + container.getClientRects()[0].x - toolTipMargin - toolTipWidth;
            // }

            let top = param.point.y + container.getClientRects()[0].y;
            // if (top > container.clientHeight - toolTipHeight) {
            //     top = param.point.y - toolTipHeight - toolTipMargin;
            // }
            toolTip.style.left = left + 'px';
            toolTip.style.top = top + 'px';
        }
    });
}
