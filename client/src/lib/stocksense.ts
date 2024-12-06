import UserConfig from './userConfig';

export default class StockSense {
    static async getDataEndpoints(): Promise<string[]> {
        const apiUrl = UserConfig.get('apiUrl');
        const res = await fetch(`${apiUrl}/data/endpoints`);
        return res.json();
    }

    static async getSymbols(endpoint: string): Promise<string[]> {
        const apiUrl = UserConfig.get('apiUrl');
        const res = await fetch(`${apiUrl}/data/endpoints/${endpoint}/symbols`);
        return res.json();
    }

    // TODO: move to use timestamp instead of ISO string
    static getKLinesUrl(endpoint: string, symbol: string, begin: string, end: string, timeframe: string = "1h"): string {
        if (endpoint === "yfinance") timeframe = "1d";
        const apiUrl = UserConfig.get('apiUrl');
        const beginDate = new Date(begin);
        const endDate = new Date(end);
        const query = new URLSearchParams({
            symbol: symbol,
            since: beginDate.getTime().toString(),
            until: endDate.getTime().toString(),
            timeframe: timeframe
        });
        return `${apiUrl}/data/endpoints/${endpoint}/kline?${query}`;
    }
}
