'use client';

import { useState, useEffect } from 'react';
import { fetchStockLivePrice } from '@/lib/actions/finnhub.actions';
import { StockPrice } from '@/types/stock';

export function useFinnhubAPI(tic: string, initialData?: StockPrice | null) {
  const [data, setData] = useState<StockPrice | null>(initialData || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const pollPrice = async () => {
      if (!isMounted) return;
      setIsLoading(true);
      setError(null);
      try {
        const newData = await fetchStockLivePrice(tic);
        if (isMounted && newData) {
          setData(newData);
        }
      } catch (err: any) {
        const msg = err?.message || '';
        if (msg.includes('429')) {
          setError('API rate limit reached. Please try again later.');
        } else {
          setError('Failed to fetch price.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    if (!initialData) {
      pollPrice();
    }

    const intervalId = setInterval(pollPrice, 60000 * 10);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [tic, initialData]);

  return { data, isLoading, error };
}