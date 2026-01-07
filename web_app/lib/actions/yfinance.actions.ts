'use server';

import { cache } from 'react';
import YahooFinance from 'yahoo-finance2';
import { StockPrice } from '@/types/stock';

type YahooQuote = {
  regularMarketPrice?: number | null;
  regularMarketChange?: number | null;
  regularMarketChangePercent?: number | null;
};


const yahooFinance = new YahooFinance();

export const fetchStockLivePrice = cache(async (tic: string): Promise<StockPrice | null> => {
  try {
    const quote = (await yahooFinance.quote(tic)) as YahooQuote;

    if (quote?.regularMarketPrice == null) {
      console.error(`No price data found for ${tic}`);
      return null;
    }

    return {
      tic,
      price: quote.regularMarketPrice,
      change: quote.regularMarketChange ?? 0,
      changePercent: quote.regularMarketChangePercent ?? 0,
    };
  } catch (error) {
    console.error(`Error fetching price for ${tic} via Yahoo:`, error);
    return null;
  }
});