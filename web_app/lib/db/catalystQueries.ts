/// <reference path="../../types/global.d.ts" />
'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { Catalyst } from '@/types';


const CATALYST_SEARCH_QUERY = `
    WITH catalyst_events AS (
        SELECT
            cv.event_id,
            cv.catalyst_id,
            cv.evidence,
            COALESCE(
                CASE
                    WHEN cv.source_type = 'earnings_transcript'
                        THEN 'earnings transcript (Q' || et.calendar_quarter || ' ' || et.calendar_year || ')'
                    ELSE 'news article'
                END,
                'unknown'
            ) AS source_type,
            cv.url
        FROM core.catalyst_versions AS cv
        LEFT JOIN (
            SELECT event_id, calendar_quarter, calendar_year
            FROM core.earnings_transcripts
            WHERE tic = $1
        ) AS et
            ON cv.event_id = et.event_id
        WHERE cv.is_valid = 1 AND cv.tic = $1
    )
    SELECT
        cm.*,
        COALESCE(ev.source_types, ARRAY[]::text[])   AS source_types,
        COALESCE(ev.evidences, ARRAY[]::text[])      AS evidences,
        COALESCE(ev.urls, ARRAY[]::text[])     AS urls
    FROM core.catalyst_master AS cm
    LEFT JOIN LATERAL (
        SELECT
            array_agg(ce.source_type ORDER BY ce.event_id) AS source_types,
            array_agg(ce.evidence ORDER BY ce.event_id)    AS evidences,
            array_agg(ce.url ORDER BY ce.event_id)   AS urls
        FROM catalyst_events AS ce
        WHERE ce.catalyst_id = cm.catalyst_id AND ce.event_id::text = ANY(cm.event_ids)
    ) AS ev ON TRUE
    WHERE cm.tic = $1 AND cm.mention_count > 0 AND (cm.sentiment = 1 OR cm.sentiment = -1)
    ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC
    LIMIT $2 OFFSET $3;
  `;

const CATALYST_SEARCH_QUERY_BULL = `
    WITH catalyst_events AS (
        SELECT
            cv.event_id,
            cv.catalyst_id,
            cv.evidence,
            COALESCE(
                CASE
                    WHEN cv.source_type = 'earnings_transcript'
                        THEN 'earnings transcript (Q' || et.calendar_quarter || ' ' || et.calendar_year || ')'
                    ELSE 'news article'
                END,
                'unknown'
            ) AS source_type,
            cv.url
        FROM core.catalyst_versions AS cv
        LEFT JOIN (
            SELECT event_id, calendar_quarter, calendar_year
            FROM core.earnings_transcripts
            WHERE tic = $1
        ) AS et
            ON cv.event_id = et.event_id
        WHERE cv.is_valid = 1 AND cv.tic = $1
    )
    SELECT
        cm.*,
        COALESCE(ev.source_types, ARRAY[]::text[])   AS source_types,
        COALESCE(ev.evidences, ARRAY[]::text[])      AS evidences,
        COALESCE(ev.urls, ARRAY[]::text[])     AS urls
    FROM core.catalyst_master AS cm
    LEFT JOIN LATERAL (
        SELECT
            array_agg(ce.source_type ORDER BY ce.event_id) AS source_types,
            array_agg(ce.evidence ORDER BY ce.event_id)    AS evidences,
            array_agg(ce.url ORDER BY ce.event_id)   AS urls
        FROM catalyst_events AS ce
        WHERE ce.catalyst_id = cm.catalyst_id AND ce.event_id::text = ANY(cm.event_ids)
    ) AS ev ON TRUE
    WHERE cm.tic = $1 AND cm.mention_count > 0 AND cm.sentiment = 1
    ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC
    LIMIT $2 OFFSET $3;
  `;

const CATALYST_SEARCH_QUERY_BEAR =  `
    WITH catalyst_events AS (
        SELECT
            cv.event_id,
            cv.catalyst_id,
            cv.evidence,
            COALESCE(
                CASE
                    WHEN cv.source_type = 'earnings_transcript'
                        THEN 'earnings transcript (Q' || et.calendar_quarter || ' ' || et.calendar_year || ')'
                    ELSE 'news article'
                END,
                'unknown'
            ) AS source_type,
            cv.url
        FROM core.catalyst_versions AS cv
        LEFT JOIN (
            SELECT event_id, calendar_quarter, calendar_year
            FROM core.earnings_transcripts
            WHERE tic = $1
        ) AS et
            ON cv.event_id = et.event_id
        WHERE cv.is_valid = 1 AND cv.tic = $1
    )
    SELECT
        cm.*,
        COALESCE(ev.source_types, ARRAY[]::text[])   AS source_types,
        COALESCE(ev.evidences, ARRAY[]::text[])      AS evidences,
        COALESCE(ev.urls, ARRAY[]::text[])     AS urls
    FROM core.catalyst_master AS cm
    LEFT JOIN LATERAL (
        SELECT
            array_agg(ce.source_type ORDER BY ce.event_id) AS source_types,
            array_agg(ce.evidence ORDER BY ce.event_id)    AS evidences,
            array_agg(ce.url ORDER BY ce.event_id)   AS urls
        FROM catalyst_events AS ce
        WHERE ce.catalyst_id = cm.catalyst_id AND ce.event_id::text = ANY(cm.event_ids)
    ) AS ev ON TRUE
    WHERE cm.tic = $1 AND cm.mention_count > 0 AND cm.sentiment = -1
    ORDER BY date DESC, impact_magnitude DESC, updated_at DESC, catalyst_id DESC
    LIMIT $2 OFFSET $3;
  `;

const CATALYST_COUNT_QUERY = `
    SELECT COUNT(*) FROM core.catalyst_master
    WHERE tic = $1 AND mention_count > 0 AND (sentiment = 1 OR sentiment = -1);
  `;

const CATALYST_COUNT_QUERY_BULL = `
    SELECT COUNT(*) FROM core.catalyst_master
    WHERE tic = $1 AND mention_count > 0 AND sentiment = 1;
  `;

const CATALYST_COUNT_QUERY_BEAR = `
    SELECT COUNT(*) FROM core.catalyst_master
    WHERE tic = $1 AND mention_count > 0 AND sentiment = -1;
  `;

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
        title: row.title,
        summary: row.summary,
        state: row.state,
        sentiment: row.sentiment,
        time_horizon: row.time_horizon,
        impact_magnitude: row.impact_magnitude,
        certainty: row.certainty,
        impact_area: row.impact_area,
        mention_count: row.mention_count,
        event_ids: row.event_ids,
        source_types: row.source_types,
        evidences: row.evidences,
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
