'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { Earnings, EarningsRegime, EPSRegime, RevenueRegime } from '@/types';

const EARNINGS_SEARCH_QUERY = `
    SELECT 
        tic,
        calendar_year,
        calendar_quarter,
        eps,
        eps_estimated,
        eps_yoy_growth,
        eps_yoy_acceleration,
        revenue,
        revenue_estimated,
        revenue_yoy_growth,
        revenue_yoy_acceleration
    FROM mart.earnings
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.earnings WHERE tic = $1)
          AND tic = $1 AND eps_estimated IS NOT NULL
    ORDER BY calendar_year ASC, calendar_quarter ASC
    LIMIT 10;
`;

const EARNINGS_LATEST_DATE_QUERY = `
    SELECT MAX(as_of_date) AS latest_date
    FROM mart.earnings
    WHERE tic = $1;
`; 

const getLatestEarningsDate = cache(async (tic: string): Promise<string | null> => {
  let client;
  try {
    client = await pool.connect();

    const result = await client.query<{ latest_date: string | null }>(EARNINGS_LATEST_DATE_QUERY, [tic.trim().toUpperCase()]);

    if (result.rows.length > 0) {
      return result.rows[0].latest_date;
    } else {
      return null;
    }

  } catch (err) {
    console.error('Database query error:', err);
    return null;

  } finally {
    if (client) {
      client.release();
    }
  }
});



const searchEarnings = cache(async (tic: string): Promise<Earnings[]> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<Earnings>(EARNINGS_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: Earnings) => ({
        tic: row.tic,
        calendar_year: row.calendar_year,
        calendar_quarter: row.calendar_quarter,
        eps: row.eps,
        eps_estimated: row.eps_estimated,
        eps_yoy_growth: row.eps_yoy_growth,
        eps_yoy_acceleration: row.eps_yoy_acceleration,
        revenue: row.revenue,
        revenue_estimated: row.revenue_estimated,
        revenue_yoy_growth: row.revenue_yoy_growth,
        revenue_yoy_acceleration: row.revenue_yoy_acceleration,
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

const EARNINGS_REGIME_SEARCH_QUERY = `
    SELECT eps_surprise_regime, revenue_surprise_regime
    FROM mart.earnings_regime
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.earnings_regime)
          AND tic = $1
    ;
`;


const searchEarningsRegimes = cache(async (tic: string): Promise<EarningsRegime> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<EarningsRegime>(EARNINGS_REGIME_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: EarningsRegime) => ({
        eps_surprise_regime: row.eps_surprise_regime.trim().toLowerCase().replace(/\s+/g, '-'),
        revenue_surprise_regime: row.revenue_surprise_regime.trim().toLowerCase().replace(/\s+/g, '-'),
    }));

    return mapped[0];

  } catch (err) {
    console.error('Database query error:', err);
    return {} as EarningsRegime;

  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
  }
});


const EPS_REGIME_SEARCH_QUERY = `
    SELECT 
        eps_yoy_growth_regime AS yoy_growth_regime, 
        eps_yoy_accel_regime AS yoy_accel_regime
    FROM mart.earnings_regime
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.earnings_regime)
          AND tic = $1
    ;
`;



const searchEPSRegimes = cache(async (tic: string): Promise<EPSRegime> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<EPSRegime>(EPS_REGIME_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: EPSRegime) => ({
        yoy_growth_regime: row.yoy_growth_regime.trim().toLowerCase().replace(/\s+/g, '-'),
        yoy_accel_regime: row.yoy_accel_regime.trim().toLowerCase().replace(/\s+/g, '-'),
    }));

    return mapped[0];

  } catch (err) {
    console.error('Database query error:', err);
    return {} as EPSRegime;

  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
  }
});


const REVENUE_REGIME_SEARCH_QUERY = `
    SELECT 
        revenue_yoy_growth_regime AS yoy_growth_regime, 
        revenue_yoy_accel_regime AS yoy_accel_regime
    FROM mart.earnings_regime
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.earnings_regime)
          AND tic = $1
    ;
`;

const searchRevenueRegimes = cache(async (tic: string): Promise<RevenueRegime> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<RevenueRegime>(REVENUE_REGIME_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: RevenueRegime) => ({
        yoy_growth_regime: row.yoy_growth_regime.trim().toLowerCase().replace(/\s+/g, '-'),
        yoy_accel_regime: row.yoy_accel_regime.trim().toLowerCase().replace(/\s+/g, '-'),
    }));

    return mapped[0];

  } catch (err) {
    console.error('Database query error:', err);
    return {} as RevenueRegime;

  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
  }
});





export { searchEarnings, searchEarningsRegimes, searchEPSRegimes, searchRevenueRegimes, getLatestEarningsDate };