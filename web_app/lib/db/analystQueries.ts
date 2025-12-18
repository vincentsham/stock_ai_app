/// <reference path="../../types/global.d.ts" />
'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { AnalystAnalysis } from '@/types';

const ANALYST_ANALYSIS_SEARCH_QUERY = `
    WITH latest_date AS (
        SELECT date
        FROM raw.stock_ohlcv_daily
        WHERE tic = $1
        ORDER BY date DESC
        LIMIT 1
    )
    SELECT sod.tic,
        sod.date,
        sod.close,
        arqs.pt_count,
        arqs.pt_high,
        arqs.pt_low,
        arqs.pt_p25,
        arqs.pt_median,
        arqs.pt_p75,
        arqs.pt_upgrade_n,
        arqs.pt_downgrade_n,
        arqs.pt_reiterate_n,
        arqs.pt_init_n,
        arqs.grade_count,
        arqs.grade_buy_n,
        arqs.grade_hold_n,
        arqs.grade_sell_n,
        arqs.grade_upgrade_n,
        arqs.grade_downgrade_n,
        arqs.grade_reiterate_n,
        arqs.grade_init_n
    FROM raw.stock_ohlcv_daily sod
    JOIN latest_date ld ON sod.date BETWEEN ld.date - INTERVAL '1 year' AND ld.date
    LEFT JOIN core.analyst_rating_yearly_summary arqs
        ON arqs.tic = sod.tic
        AND arqs.end_date = sod.date
    WHERE sod.tic = $1
          AND arqs.pt_count IS NOT NULL 
          AND arqs.grade_count IS NOT NULL
    ORDER BY sod.date DESC;
`;

const searchAnalystAnalysis = cache(async (tic: string): Promise<AnalystAnalysis[]> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<AnalystAnalysis>(ANALYST_ANALYSIS_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: AnalystAnalysis) => ({
        tic: row.tic,
        date: new Date(row.date).toISOString().slice(0, 10),
        close: Number(row.close),
        pt_count: row.pt_count != null ? Number(row.pt_count) : null,
        pt_high: row.pt_high != null ? Number(row.pt_high) : null,
        pt_low: row.pt_low != null ? Number(row.pt_low) : null,
        pt_p25: row.pt_p25 != null ? Number(row.pt_p25) : null,
        pt_median: row.pt_median != null ? Number(row.pt_median) : null,
        pt_p75: row.pt_p75 != null ? Number(row.pt_p75) : null,
        pt_upgrade_n: row.pt_upgrade_n != null ? Number(row.pt_upgrade_n) : null,
        pt_downgrade_n: row.pt_downgrade_n != null ? Number(row.pt_downgrade_n) : null,
        pt_reiterate_n: row.pt_reiterate_n != null ? Number(row.pt_reiterate_n) : null,
        pt_init_n: row.pt_init_n != null ? Number(row.pt_init_n) : null,
        grade_count: row.grade_count != null ? Number(row.grade_count) : null,
        grade_buy_n: row.grade_buy_n != null ? Number(row.grade_buy_n) : null,
        grade_hold_n: row.grade_hold_n != null ? Number(row.grade_hold_n) : null,
        grade_sell_n: row.grade_sell_n != null ? Number(row.grade_sell_n) : null,
        grade_upgrade_n: row.grade_upgrade_n != null ? Number(row.grade_upgrade_n) : null,
        grade_downgrade_n: row.grade_downgrade_n != null ? Number(row.grade_downgrade_n) : null,
        grade_reiterate_n: row.grade_reiterate_n != null ? Number(row.grade_reiterate_n) : null,
        grade_init_n: row.grade_init_n != null ? Number(row.grade_init_n) : null,
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





export { searchAnalystAnalysis };