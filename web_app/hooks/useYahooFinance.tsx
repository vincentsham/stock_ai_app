'use client';

import { useState, useEffect } from 'react';
// UPDATE THIS PATH: Point to the file where you saved the Yahoo version of fetchStockLivePrice
import { fetchStockLivePrice } from '@/lib/actions/yfinance.actions'; 
import { StockPrice } from '@/types/stock';

export function useStockLivePrice(tic: string, initialData?: StockPrice | null) {
  const [data, setData] = useState<StockPrice | null>(initialData || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const pollPrice = async () => {
      if (!isMounted) return;
      
      // Optional: Only show loading state if we don't have data yet (prevents UI flashing on updates)
      if (!data) setIsLoading(true); 
      
      setError(null);
      
      try {
        const newData = await fetchStockLivePrice(tic);
        
        if (isMounted) {
          if (newData) {
            setData(newData);
          } else {
            // Handle case where Yahoo returns null (e.g. invalid ticker)
            setError('No data found');
          }
        }
      } catch (err: any) {
        if (isMounted) {
            console.error('Yahoo Finance Poll Error:', err);
            setError('Failed to fetch price.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    // 1. If we have no initial data, fetch immediately
    if (!initialData) {
      pollPrice();
    }

    // 2. Poll every 10 minutes (60000ms * 10)
    const intervalId = setInterval(pollPrice, 60000 * 10);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [tic, initialData]); // Note: removing 'data' from dependency array avoids infinite loops

  return { data, isLoading, error };
}