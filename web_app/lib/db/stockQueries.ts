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
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const trimmed = query.trim();
    const searchQuery = `%${trimmed}%`;

    const result = await client.query<StockProfile>(STOCKS_SEARCH_QUERY, [searchQuery]);

    // 2. Map results (omitted for brevity)
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

  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
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
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<StockProfile>(STOCK_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. return the first result or null
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

  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
  }
});




export { searchStocks, searchStock };
