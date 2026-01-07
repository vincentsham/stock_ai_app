'use server';

import { cache } from 'react';
import yahooFinance from '@/lib/yahoo';
import { StockPrice } from '@/types/stock';

type YahooQuote = {
    regularMarketPrice?: number | null;
    regularMarketChange?: number | null;
    regularMarketChangePercent?: number | null;
};

export const fetchStockLivePrice = cache(async (tic: string): Promise<StockPrice | null> => {
    try {
        // Use the imported instance directly and cast to a minimal shape we need.
        const quote = (await yahooFinance.quote(tic)) as YahooQuote;

        if (!quote || quote.regularMarketPrice == null) {
            console.error(`No price data found for ${tic}`);
            return null;
        }

        return {
            tic: tic,
            price: quote.regularMarketPrice,
            change: quote.regularMarketChange ?? 0,
            changePercent: quote.regularMarketChangePercent ?? 0,
        };
    } catch (error) {
        console.error(`Error fetching price for ${tic} via Yahoo:`, error);
        return null;
    }
});