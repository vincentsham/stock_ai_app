'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { Metric, MetricList } from '@/types';
import { METRICS_METADATA } from '@/lib/constants';


const VALUATION_METRICS_SEARCH_QUERY = `
    SELECT
      tic,
      date,
      score,

      -- valuation
      pe_ttm,
      pe_forward,
      ps_ttm,
      peg_ratio_forward,
      p_to_fcf_ttm,
      price_to_book,

      ev_to_revenue_ttm,
      ev_to_ebitda_ttm,
      ev_to_fcf_ttm,

      earnings_yield_ttm,
      revenue_yield_ttm,
      fcf_yield_ttm,
      total_shareholder_yield_ttm,

      -- valuation percentiles
      pe_ttm_percentile,
      pe_forward_percentile,
      ps_ttm_percentile,
      peg_ratio_percentile,
      peg_ratio_forward_percentile,
      p_to_fcf_ttm_percentile,
      price_to_book_percentile,

      ev_to_revenue_ttm_percentile,
      ev_to_ebitda_ttm_percentile,
      ev_to_fcf_ttm_percentile,

      fcf_yield_ttm_percentile,
      earnings_yield_ttm_percentile,
      revenue_yield_ttm_percentile,
      total_shareholder_yield_ttm_percentile
    FROM mart.valuation_metrics
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.valuation_metrics WHERE tic = $1)
          AND tic = $1
    ORDER BY date DESC
    LIMIT 1;
`;


const PROFITABILITY_METRICS_SEARCH_QUERY = `
    SELECT
      tic,
      date,
      -- final score
      score,

      -- profitability
      net_margin,
      operating_margin,
      gross_margin,
      ebitda_margin,

      roa,
      roe,
      roic,
      ocf_margin,
      fcf_margin,

      -- profitability percentiles
      gross_margin_percentile,
      operating_margin_percentile,
      ebitda_margin_percentile,
      net_margin_percentile,
      roe_percentile,
      roa_percentile,
      roic_percentile,
      ocf_margin_percentile,
      fcf_margin_percentile

    FROM mart.profitability_metrics
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.profitability_metrics WHERE tic = $1)
          AND tic = $1
    ORDER BY date DESC
    LIMIT 1;
`;



const GROWTH_METRICS_SEARCH_QUERY = `
    SELECT
      tic,
      date,
      -- final score
      score,

      -- growth
      revenue_growth_yoy,
      eps_growth_yoy,
      ebitda_growth_yoy,
      fcf_growth_yoy,
      
    
      revenue_cagr_3y,
      eps_cagr_3y,
      ebitda_cagr_3y,
      fcf_cagr_3y,
      
      operating_income_growth_yoy,
      forward_revenue_growth,
      forward_eps_growth,

      revenue_cagr_5y,
      eps_cagr_5y,

      -- growth percentiles
      revenue_growth_yoy_percentile,
      revenue_cagr_3y_percentile,
      eps_growth_yoy_percentile,
      eps_cagr_3y_percentile,
      fcf_growth_yoy_percentile,
      fcf_cagr_3y_percentile,
      ebitda_growth_yoy_percentile,
      ebitda_cagr_3y_percentile,

      revenue_cagr_5y_percentile,
      eps_cagr_5y_percentile,

      
      operating_income_growth_yoy_percentile,
      forward_revenue_growth_percentile,
      forward_eps_growth_percentile

    FROM mart.growth_metrics
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.growth_metrics WHERE tic = $1)
          AND tic = $1
    ORDER BY date DESC
    LIMIT 1;
`;



const EFFICIENCY_METRICS_SEARCH_QUERY = `
    SELECT
      tic,
      date,
      -- final score
      score,

      -- efficiency
      asset_turnover,
      fixed_asset_turnover,
      opex_ratio,
      cash_conversion_cycle,
      dso,
      dio,
      dpo,
      revenue_per_employee,

      -- efficiency percentiles
      asset_turnover_percentile,
      cash_conversion_cycle_percentile,
      dso_percentile,
      dio_percentile,
      dpo_percentile,
      fixed_asset_turnover_percentile,
      revenue_per_employee_percentile,
      opex_ratio_percentile

    FROM mart.efficiency_metrics 
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.efficiency_metrics WHERE tic = $1)
          AND tic = $1
    ORDER BY date DESC
    LIMIT 1;
`;


const FINANCIAL_HEALTH_METRICS_SEARCH_QUERY = `
    SELECT
      tic,
      date,
      -- final score
      score,

      -- financial health
      net_debt_to_ebitda_ttm,
      interest_coverage_ttm,
      current_ratio,
      quick_ratio,
      cash_ratio,
      debt_to_equity,
      debt_to_assets,
      altman_z_score,

      -- financial health percentiles
      net_debt_to_ebitda_ttm_percentile,
      interest_coverage_ttm_percentile,
      current_ratio_percentile,
      quick_ratio_percentile,
      cash_ratio_percentile,
      debt_to_equity_percentile,
      debt_to_assets_percentile,
      altman_z_score_percentile
    FROM mart.financial_health_metrics
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.financial_health_metrics WHERE tic = $1)
          AND tic = $1
    ORDER BY date DESC
    LIMIT 1;
`;




const searchMetrics = cache(async (tic: string, category: string, query: string): Promise<MetricList> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const data = await client.query(query, [tic.trim().toUpperCase()]);

    // 2. Process the results
    if (data.rows.length > 0) {
      const row = data.rows[0];
      // Map to MetricList structure
      const metricList: MetricList = {
        category: category,
        tic: tic,
        score: row['score'] as number | null,
        metrics: [] as Metric[],
        defaultVisibleCount: 0,
      };
      for (const [key, value] of Object.entries(row as Record<string, unknown>)) {
          if (key.endsWith('_percentile') || key === 'category' || key === 'tic' || key === 'date' || key === 'score') continue; // Skip percentile entries
          const percentileKey = `${key}_percentile`;
          const metadata = (METRICS_METADATA as Record<string, { name: string, display_fn: (v: unknown) => string, description: string, inverse: boolean | null, displayByDefault: boolean }>)[key];
          if (!metadata) continue;
          const metric: Metric = {
              label: key,
              name: metadata.name,
              value: metadata.display_fn(value), // Convert value to string
              percentile: (row as Record<string, unknown>)[percentileKey] as number,
              description: metadata.description,
              inverse: metadata.inverse,
              displayByDefault: metadata.displayByDefault,
          };
          if (metric.displayByDefault) {
              metricList.defaultVisibleCount += 1;
          }
          metricList.metrics.push(metric);
      }
      return metricList;

    }


  } catch (err) {
    console.error('Database query error:', err);
    return { category, tic, score: null, metrics: [], defaultVisibleCount: 0 };

  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
  }

  // Return an empty object if no results are found
  return { category, tic, score: null, metrics: [], defaultVisibleCount: 0 };
});

export const searchValuationMetrics = async (tic: string) => searchMetrics(tic, 'Valuation', VALUATION_METRICS_SEARCH_QUERY);
export const searchProfitabilityMetrics = async (tic: string) => searchMetrics(tic, 'Profitability', PROFITABILITY_METRICS_SEARCH_QUERY);
export const searchGrowthMetrics = async (tic: string) => searchMetrics(tic, 'Growth', GROWTH_METRICS_SEARCH_QUERY);
export const searchEfficiencyMetrics = async (tic: string) => searchMetrics(tic, 'Efficiency', EFFICIENCY_METRICS_SEARCH_QUERY);
export const searchFinancialHealthMetrics = async (tic: string) => searchMetrics(tic, 'Financial Health', FINANCIAL_HEALTH_METRICS_SEARCH_QUERY);


const STOCK_SCORES_SEARCH_QUERY = `
    SELECT
      ss.tic,
      ss.valuation_score,
      ss.profitability_score,
      ss.growth_score,
      ss.efficiency_score,
      ss.financial_health_score,
      ss.total_score
    FROM mart.stock_scores ss
    WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.stock_scores WHERE tic = $1)
          AND ss.tic = $1
    ORDER BY ss.date DESC
    LIMIT 1;
`;


export const searchStockScores = cache(async (tic: string) => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();

    const data = await client.query(STOCK_SCORES_SEARCH_QUERY, [tic.trim().toUpperCase()]);

    // 2. Process the results
    if (data.rows.length > 0) {
      const row = data.rows[0];
      const stockScores = {
        tic: row['tic'] as string,
        valuation_score: row['valuation_score'] as number | null,
        profitability_score: row['profitability_score'] as number | null,
        growth_score: row['growth_score'] as number | null,
        efficiency_score: row['efficiency_score'] as number | null,
        financial_health_score: row['financial_health_score'] as number | null,
        total_score: row['total_score'] as number | null,
      };
      return stockScores;
    } else {
      return {
        tic,
        valuation_score: null,
        profitability_score: null,
        growth_score: null,
        efficiency_score: null,
        financial_health_score: null,
        total_score: null,
      };
    }
  } catch (err) {
    console.error('Database query error:', err);
    return {
      tic,
      valuation_score: null,
      profitability_score: null,
      growth_score: null,
      efficiency_score: null,
      financial_health_score: null,
      total_score: null,
    };
  } finally {
    // 3. IMPORTANT: Release the client back to the pool
    if (client) {
      client.release();
    }
  }
});



const TOP_STOCKS_SEARCH_QUERY = `
      SELECT
        ss.tic
      FROM mart.stock_scores ss
      WHERE as_of_date = (SELECT MAX(as_of_date) FROM mart.stock_scores)
      ORDER BY ss.total_score DESC
      LIMIT $1;
`;

const STOCK_SCORES_LATEST_DATE_WITH_TIC_QUERY = `
    SELECT MAX(as_of_date) AS latest_date
    FROM mart.stock_scores
    WHERE tic = $1;
`;

const STOCK_SCORES_LATEST_DATE_QUERY = `
    SELECT MAX(as_of_date) AS latest_date
    FROM mart.stock_scores;
`;

export const getLatestStockScoresDate = cache(async (tic: string | null): Promise<string | null> => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();
    let result;
    if (tic && tic.trim() !== '') {
      result = await client.query<{ latest_date: Date | null }>(STOCK_SCORES_LATEST_DATE_WITH_TIC_QUERY, [tic.trim().toUpperCase()]);
    } else {
      result = await client.query<{ latest_date: Date | null }>(STOCK_SCORES_LATEST_DATE_QUERY);
    }

    if (result.rows.length > 0 && result.rows[0].latest_date) {
      return result.rows[0].latest_date.toISOString().slice(0, 10);
    } else {
      return null;
    }

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

export const searchTopStocks = cache(async (limit: number) => {
  let client;
  try {
    // 1. Acquire a client (connection) from the pool
    client = await pool.connect();
    const result = await client.query(TOP_STOCKS_SEARCH_QUERY, [limit]);

    // 2. create a list of tic from result
    const topTics: string[] = result.rows.map((row: any) => row['tic'] as string);
    return topTics;

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




