'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { EarningsCallAnalysis } from '@/types';
import { fixQuotes } from '../utils';

const EARNINGS_CALL_SEARCH_QUERY = `
    SELECT
        inference_id,
        event_id,
        tic,
        calendar_year,
        calendar_quarter,
        earnings_date,
        TRUNC((sentiment + guidance_direction) / 2.0)::INT AS sentiment,
        durability,
        performance_factors,
        past_summary,
        guidance_direction,
        revenue_outlook,
        margin_outlook,
        earnings_outlook,
        cashflow_outlook,
        growth_acceleration,
        future_outlook_sentiment,
        growth_drivers,
        future_summary,
        risk_mentioned,
        risk_impact,
        risk_time_horizon,
        risk_factors,
        risk_summary,
        mitigation_mentioned,
        mitigation_effectiveness,
        mitigation_time_horizon,
        mitigation_actions,
        mitigation_summary,
        transcript_sha256,
        updated_at
    FROM mart.earnings_transcript_analysis 
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.earnings_transcript_analysis WHERE tic = $1)
        AND tic = $1;
`;

const EARNINGS_CALL_LATEST_DATE_QUERY = `
    SELECT MAX(as_of_date) AS latest_date
    FROM mart.earnings_transcript_analysis
    WHERE tic = $1;
`;

export const getLatestEarningsCallDate = cache(async (tic: string): Promise<string | null> => {
  let client;
  try {
    client = await pool.connect();

    const result = await client.query<{ latest_date: string | null }>(EARNINGS_CALL_LATEST_DATE_QUERY, [tic.trim().toUpperCase()]);

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



const searchEarningsCalls = cache(async (tic: string): Promise<EarningsCallAnalysis[]> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<EarningsCallAnalysis>(EARNINGS_CALL_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: EarningsCallAnalysis) => ({
      inference_id: row.inference_id,
      event_id: row.event_id,
      tic: row.tic,
      calendar_year: row.calendar_year,
      calendar_quarter: row.calendar_quarter,
      earnings_date: row.earnings_date,
      sentiment: row.sentiment,
      durability: row.durability,
      performance_factors: row.performance_factors,
      past_summary: fixQuotes(row.past_summary),
      guidance_direction: row.guidance_direction,
      revenue_outlook: row.revenue_outlook,
      margin_outlook: row.margin_outlook,
      earnings_outlook: row.earnings_outlook,
      cashflow_outlook: row.cashflow_outlook,
      growth_acceleration: row.growth_acceleration,
      future_outlook_sentiment: row.future_outlook_sentiment,
      growth_drivers: row.growth_drivers,
      future_summary: fixQuotes(row.future_summary),
      risk_mentioned: row.risk_mentioned,
      risk_impact: row.risk_impact,
      risk_time_horizon: row.risk_time_horizon,
      risk_factors: row.risk_factors,
      risk_summary: fixQuotes(row.risk_summary),
      mitigation_mentioned: row.mitigation_mentioned,
      mitigation_effectiveness: row.mitigation_effectiveness,
      mitigation_time_horizon: row.mitigation_time_horizon,
      mitigation_actions: row.mitigation_actions,
      mitigation_summary: fixQuotes(row.mitigation_summary),
      transcript_sha256: row.transcript_sha256,
      updated_at: row.updated_at,
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

export { searchEarningsCalls };
