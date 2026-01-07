'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { Catalyst } from '@/types';
import { fixQuotes } from '../utils';



const CATALYST_SEARCH_QUERY = `
    SELECT
        catalyst_id,
        tic,
        date,
        catalyst_type,
        title,
        summary,
        state,
        sentiment,
        time_horizon,
        impact_magnitude,
        certainty,
        impact_area,
        mention_count,
        event_ids,
        source_types,
        evidences,
        urls,
        created_at,
        updated_at
    FROM mart.catalyst_master
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.catalyst_master)
        AND tic = $1 AND mention_count > 0 AND (sentiment = 1 OR sentiment = -1)
        AND impact_magnitude <> -1
    ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC
    LIMIT $2 OFFSET $3;
  `;

const CATALYST_SEARCH_QUERY_BULL = `
    SELECT
        catalyst_id,
        tic,
        date,
        catalyst_type,
        title,
        summary,
        state,
        sentiment,
        time_horizon,
        impact_magnitude,
        certainty,
        impact_area,
        mention_count,
        event_ids,
        source_types,
        evidences,
        urls,
        created_at,
        updated_at
    FROM mart.catalyst_master
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.catalyst_master) 
        AND tic = $1 AND mention_count > 0 AND sentiment = 1
        AND impact_magnitude <> -1
    ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC
    LIMIT $2 OFFSET $3;
  `;

const CATALYST_SEARCH_QUERY_BEAR =  `
    SELECT
        catalyst_id,
        tic,
        date,
        catalyst_type,
        title,
        summary,
        state,
        sentiment,
        time_horizon,
        impact_magnitude,
        certainty,
        impact_area,
        mention_count,
        event_ids,
        source_types,
        evidences,
        urls,
        created_at,
        updated_at
    FROM mart.catalyst_master
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.catalyst_master WHERE tic = $1) 
        AND tic = $1 AND mention_count > 0 AND sentiment = -1
        AND impact_magnitude <> -1
    ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC
    LIMIT $2 OFFSET $3;
  `;

const CATALYST_COUNT_QUERY = `
    SELECT COUNT(*) FROM mart.catalyst_master
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.catalyst_master WHERE tic = $1) 
        AND tic = $1 AND mention_count > 0 
        AND (sentiment = 1 OR sentiment = -1) AND impact_magnitude <> -1;
  `;

const CATALYST_COUNT_QUERY_BULL = `
    SELECT COUNT(*) FROM mart.catalyst_master
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.catalyst_master WHERE tic = $1) 
        AND tic = $1 AND mention_count > 0 
        AND sentiment = 1 AND impact_magnitude <> -1;
  `;

const CATALYST_COUNT_QUERY_BEAR = `
    SELECT COUNT(*) FROM mart.catalyst_master
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.catalyst_master WHERE tic = $1) 
        AND tic = $1 AND mention_count > 0 
        AND sentiment = -1 AND impact_magnitude <> -1;
  `;

const CATALYST_LATEST_DATE_QUERY = `
    SELECT MAX(as_of_date) AS latest_date
    FROM mart.catalyst_master
    WHERE tic = $1;
`;

export const getLatestCatalystDate = cache(async (tic: string): Promise<string | null> => {
    let client;
    try {
        // 1. Acquire a client (connection) from the pool
        client = await pool.connect();
        const result = await client.query<{ latest_date: string | null }>(CATALYST_LATEST_DATE_QUERY, [tic.trim().toUpperCase()]);

        // 2. Extract latest date
        const latestDate = result.rows[0].latest_date;
        return latestDate;

    } catch (err) {
        console.error('Database latest date query error:', err);
        return null;

    } finally {
        // 3. IMPORTANT: Release the client back to the pool
        if (client) {
            client.release();
        }
    }
});

const searchCatalysts = cache(async (tic: string, page: number, limit: number, sentiment?: number): Promise<Catalyst[]> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();
    const offset = (page - 1) * limit;
    let query = CATALYST_SEARCH_QUERY;
    if (sentiment === 1) {
        query = CATALYST_SEARCH_QUERY_BULL;
    } else if (sentiment === -1) {
        query = CATALYST_SEARCH_QUERY_BEAR;
    }
    const result = await client.query<Catalyst>(query, [tic.trim().toUpperCase(), limit, offset]);

    // 2. Map results (omitted for brevity)
    const mapped = result.rows.map((row: Catalyst) => ({
        catalyst_id: row.catalyst_id,
        tic: row.tic,
        date: row.date,
        catalyst_type: row.catalyst_type,
        title: fixQuotes(row.title),
        summary: fixQuotes(row.summary),
        state: row.state,
        sentiment: row.sentiment,
        time_horizon: row.time_horizon,
        impact_magnitude: row.impact_magnitude,
        certainty: row.certainty,
        impact_area: row.impact_area,
        mention_count: row.mention_count,
        event_ids: row.event_ids,
        source_types: row.source_types,
        evidences: row.evidences.map(fixQuotes),
        urls: row.urls,
        created_at: row.created_at,
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


const countCatalysts = cache(async (tic: string, sentiment?: number): Promise<number> => {
    let client;
    try {
        // 1. Acquire a client (connection) from the pool
        client = await pool.connect();
        let query = CATALYST_COUNT_QUERY;
        if (sentiment === 1) {
            query = CATALYST_COUNT_QUERY_BULL;
        } else if (sentiment === -1) {
            query = CATALYST_COUNT_QUERY_BEAR;
        }
        const result = await client.query<{ count: string }>(query, [tic.trim().toUpperCase()]);

        // 2. Extract count
        const count = parseInt(result.rows[0].count, 10);
        return count;

    } catch (err) {
        console.error('Database count query error:', err);
        return 0;

    } finally {
        // 3. IMPORTANT: Release the client back to the pool
        if (client) {
            client.release();
        }
    }
});



export { searchCatalysts, countCatalysts };
