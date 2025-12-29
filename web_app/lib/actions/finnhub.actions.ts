'use server';

import { cache } from 'react';
import { StockPrice } from '@/types/stock';

const FINNHUB_API_KEY = process.env.FINNHUB_API_KEY; 
const FINNHUB_BASE_URL = 'https://finnhub.io/api/v1';


async function fetchJSON<T>(url: string, revalidateSeconds?: number): Promise<T> {
    const options: RequestInit & { next?: { revalidate?: number } } = revalidateSeconds
        ? { cache: 'force-cache', next: { revalidate: revalidateSeconds } }
        : { cache: 'no-store' };

    const res = await fetch(url, options);
    if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`Fetch failed ${res.status}: ${text}`);
    }
    return (await res.json()) as T;
}

export const fetchStockLogo = cache(async (tic: string): Promise<string | null> => {
    try {
        const token = FINNHUB_API_KEY;
        if (!token) {
        throw new Error('FINNHUB API key is not configured');
        }
        const url = `${FINNHUB_BASE_URL}/stock/profile2?symbol=${encodeURIComponent(tic)}&token=${token}`;
        const data = await fetchJSON<{ logo: string | null }>(url, 86400); // Cache for 24 hours
        return data.logo;
    } catch (error) {
        console.error(`Error fetching stock logo for ${tic}:`, error);
        return null;
    }
});

export const fetchStockLivePrice = cache(async (tic: string): Promise<StockPrice | null> => {
  try {
        const token = FINNHUB_API_KEY;
        if (!token) {
        throw new Error('FINNHUB API key is not configured');
        }
        const url = `${FINNHUB_BASE_URL}/quote?symbol=${encodeURIComponent(tic)}&token=${token}`;
        // Finnhub Quote Response Shape
        const data = await fetchJSON<{ c: number; d: number; dp: number }>(url);
        return {
            tic: tic,
            price: data.c,
            change: data.d,  // Finnhub does not provide absolute change directly
            changePercent: data.dp,
        };
    } catch (error) {
        console.error(`Error fetching price for ${tic}:`, error);
        return null;
    }
});