/// <reference path="../../types/global.d.ts" />
'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { Earnings, EarningsRegime, EPSRegime, RevenueRegime } from '@/types';

const EARNINGS_SEARCH_QUERY = `
    SELECT *
    FROM (
        SELECT e.tic, e.calendar_year, e.calendar_quarter, e.earnings_date, 
              e.eps, e.eps_estimated, 
              edm.eps_diluted_yoy_growth * 100 AS eps_yoy_growth,
              edm.eps_diluted_yoy_accel * 100 AS eps_yoy_acceleration,
              e.revenue, e.revenue_estimated, 
              rm.revenue_yoy_growth * 100 AS revenue_yoy_growth, 
              rm.revenue_yoy_accel * 100 AS revenue_yoy_acceleration
        FROM core.earnings AS e
        LEFT JOIN core.eps_diluted_metrics AS edm
        ON e.tic = edm.tic 
          AND e.calendar_year = edm.calendar_year
          AND e.calendar_quarter = edm.calendar_quarter
        LEFT JOIN core.revenue_metrics AS rm
        ON e.tic = rm.tic
          AND e.calendar_year = rm.calendar_year
          AND e.calendar_quarter = rm.calendar_quarter
        WHERE e.tic = $1 AND e.eps_estimated IS NOT NULL
        ORDER BY e.calendar_year DESC, e.calendar_quarter DESC
        LIMIT 9) AS subquery
    ORDER BY calendar_year ASC, calendar_quarter ASC;
`;

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
    WITH latest_earnings AS (
        SELECT 
            tic, calendar_year, calendar_quarter, 
            eps, eps_estimated, revenue, revenue_estimated 
        FROM core.earnings 
        WHERE tic = $1 AND eps IS NOT NULL 
        ORDER BY tic, calendar_year DESC, calendar_quarter DESC 
    LIMIT 1)
    SELECT eps_surprise_regime, revenue_surprise_regime
    FROM core.earnings_metrics em
    JOIN latest_earnings le
    ON em.tic = le.tic
    AND em.calendar_year = le.calendar_year
    AND em.calendar_quarter = le.calendar_quarter
    WHERE le.tic = $1
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
    WITH latest_earnings AS (
        SELECT 
            tic, calendar_year, calendar_quarter, 
            eps, eps_estimated, revenue, revenue_estimated 
        FROM core.earnings 
        WHERE tic = $1 AND eps IS NOT NULL 
        ORDER BY tic, calendar_year DESC, calendar_quarter DESC 
    LIMIT 1)
    SELECT 
        eps_diluted_yoy_growth_regime AS yoy_growth_regime, 
        eps_diluted_yoy_accel_regime AS yoy_accel_regime
    FROM core.eps_diluted_metrics em
    JOIN latest_earnings le
    ON em.tic = le.tic
    AND em.calendar_year = le.calendar_year
    AND em.calendar_quarter = le.calendar_quarter
    WHERE le.tic = $1
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
    WITH latest_earnings AS (
        SELECT 
            tic, calendar_year, calendar_quarter, 
            eps, eps_estimated, revenue, revenue_estimated 
        FROM core.earnings 
        WHERE tic = $1 AND eps IS NOT NULL 
        ORDER BY tic, calendar_year DESC, calendar_quarter DESC 
    LIMIT 1)
    SELECT 
        revenue_yoy_growth_regime AS yoy_growth_regime, 
        revenue_yoy_accel_regime AS yoy_accel_regime
    FROM core.revenue_metrics em
    JOIN latest_earnings le
    ON em.tic = le.tic
    AND em.calendar_year = le.calendar_year
    AND em.calendar_quarter = le.calendar_quarter
    WHERE le.tic = $1
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





export { searchEarnings, searchEarningsRegimes, searchEPSRegimes, searchRevenueRegimes };