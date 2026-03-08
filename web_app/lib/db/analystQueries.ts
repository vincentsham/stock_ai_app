'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { AnalystAnalysis } from '@/types';

const ANALYST_ANALYSIS_SEARCH_QUERY = `
    SELECT 
        tic,
        date,
        close,
        pt_count,
        pt_high,
        pt_low,
        pt_p25,
        pt_median,
        pt_p75,
        pt_upgrade_n,
        pt_downgrade_n,
        pt_reiterate_n,
        pt_init_n,
        grade_count,
        grade_buy_n,
        grade_hold_n,
        grade_sell_n,
        grade_upgrade_n,
        grade_downgrade_n,
        grade_reiterate_n,
        grade_init_n
    FROM mart.analyst_rating_yearly_summary 
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.analyst_rating_yearly_summary WHERE tic = $1) 
        AND tic = $1
    ORDER BY date DESC;
`;

const ANALYST_ANALYSIS_LATEST_DATE_QUERY = `
    SELECT MAX(as_of_date) AS latest_date
    FROM mart.analyst_rating_yearly_summary
    WHERE tic = $1;
`;


const searchAnalystAnalysis = cache(async (tic: string): Promise<AnalystAnalysis[]> => {
  try {
    const result = await pool.query<AnalystAnalysis>(ANALYST_ANALYSIS_SEARCH_QUERY, [tic.trim().toUpperCase()]);

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
  }
});

const getLatestAnalystAnalysisDate = cache(async (tic: string): Promise<string | null> => {
  try {
    const result = await pool.query<{ latest_date: Date | null }>(ANALYST_ANALYSIS_LATEST_DATE_QUERY, [tic.trim().toUpperCase()]);

    if (result.rows.length > 0 && result.rows[0].latest_date) {
      return result.rows[0].latest_date.toISOString().slice(0, 10);
    } else {
      return null;
    }

  } catch (err) {
    console.error('Database query error:', err);
    return null;
  }
});



export { searchAnalystAnalysis, getLatestAnalystAnalysisDate };