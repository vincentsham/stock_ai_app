'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { StockProfile } from '@/types';

const STOCKS_SEARCH_QUERY = `
  SELECT tic, name, exchange, sector, industry
  FROM mart.stock_profiles
  WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.stock_profiles) AND (tic ILIKE $1 OR name ILIKE $1)
  LIMIT 15;
`;

const searchStocks = cache(async (query: string): Promise<StockProfile[]> => {
  try {
    const trimmed = query.trim();
    const searchQuery = `%${trimmed}%`;

    const result = await pool.query<StockProfile>(STOCKS_SEARCH_QUERY, [searchQuery]);

    const mapped = result.rows.map((row: StockProfile) => ({
      tic: row.tic,
      name: row.name,
      exchange: row.exchange,
      sector: row.sector,
      industry: row.industry,
    }));

    return mapped;

  } catch (err) {
    console.error('Database query error:', err);
    return [];
  }
});


const STOCK_SEARCH_QUERY = `
  SELECT tic, name, exchange, sector, industry
  FROM mart.stock_profiles
  WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.stock_profiles WHERE tic = $1) 
        AND tic = $1
  LIMIT 1;
`;

const searchStock = cache(async (tic: string): Promise<StockProfile | null> => {
  try {
    const result = await pool.query<StockProfile>(STOCK_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    const stock = result.rows.map((row: StockProfile) => ({
      tic: row.tic,
      name: row.name,
      exchange: row.exchange,
      sector: row.sector,
      industry: row.industry,
    }))[0];

    return stock;

  } catch (err) {
    console.error('Database query error:', err);
    return null;
  }
});




export { searchStocks, searchStock };
