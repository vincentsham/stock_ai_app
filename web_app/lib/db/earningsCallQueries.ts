/// <reference path="../../types/global.d.ts" />
'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { EarningsCallAnalysis } from '@/types';

const EARNINGS_CALL_SEARCH_QUERY = `
  SELECT eta.*, et.earnings_date
  FROM core.earnings_transcript_analysis eta
  JOIN core.earnings_transcripts et 
  ON eta.event_id = et.event_id
  WHERE eta.tic = $1;
`;

const searchEarningsCalls = cache(async (tic: string): Promise<EarningsCallAnalysis[]> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const result = await client.query<EarningsCallAnalysis>(EARNINGS_CALL_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row) => ({
      inference_id: row.inference_id,
      event_id: row.event_id,
      tic: row.tic,
      calendar_year: row.calendar_year,
      calendar_quarter: row.calendar_quarter,
      earnings_date: row.earnings_date,
      sentiment: row.sentiment,
      durability: row.durability,
      performance_factors: row.performance_factors,
      past_summary: row.past_summary,
      guidance_direction: row.guidance_direction,
      revenue_outlook: row.revenue_outlook,
      margin_outlook: row.margin_outlook,
      earnings_outlook: row.earnings_outlook,
      cashflow_outlook: row.cashflow_outlook,
      growth_acceleration: row.growth_acceleration,
      future_outlook_sentiment: row.future_outlook_sentiment,
      growth_drivers: row.growth_drivers,
      future_summary: row.future_summary,
      risk_mentioned: row.risk_mentioned,
      risk_impact: row.risk_impact,
      risk_time_horizon: row.risk_time_horizon,
      risk_factors: row.risk_factors,
      risk_summary: row.risk_summary,
      mitigation_mentioned: row.mitigation_mentioned,
      mitigation_effectiveness: row.mitigation_effectiveness,
      mitigation_time_horizon: row.mitigation_time_horizon,
      mitigation_actions: row.mitigation_actions,
      mitigation_summary: row.mitigation_summary,
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
