/// <reference path="../../types/global.d.ts" />
'use server';
import pool from '@/lib/db/utils';
import { cache } from 'react';
import { Metric, MetricList } from '@/types';
import { METRICS_METADATA } from '@/lib/constants';


const VALUATION_METRICS_SEARCH_QUERY = `
    SELECT
      v.tic,
      v.date,
      ss.valuation_score AS score,

      -- valuation
      v.pe_ttm,
      v.pe_forward,
      v.ps_ttm,
      v.peg_ratio_forward,
      v.p_to_fcf_ttm,
      v.price_to_book,

      v.ev_to_revenue_ttm,
      v.ev_to_ebitda_ttm,
      v.ev_to_fcf_ttm,

      v.earnings_yield_ttm,
      v.revenue_yield_ttm,
      v.fcf_yield_ttm,
      ca.total_shareholder_yield,

      -- valuation percentiles
      vp.pe_ttm_percentile,
      vp.pe_forward_percentile,
      vp.ps_ttm_percentile,
      vp.peg_ratio_forward_percentile,
      vp.p_to_fcf_ttm_percentile,
      vp.price_to_book_percentile,

      vp.ev_to_revenue_ttm_percentile,
      vp.ev_to_ebitda_ttm_percentile,
      vp.ev_to_fcf_ttm_percentile,

      vp.fcf_yield_ttm_percentile,
      vp.earnings_yield_ttm_percentile,
      vp.revenue_yield_ttm_percentile,
      cap.total_shareholder_yield_percentile

    FROM core.valuation_metrics v
    JOIN core.valuation_percentiles vp
      ON v.inference_id = vp.inference_id
    JOIN core.capital_allocation_metrics ca
      ON v.tic = ca.tic AND v.date = ca.date
    JOIN core.capital_allocation_percentiles cap
      ON ca.inference_id = cap.inference_id
    JOIN core.stock_scores ss
      ON v.tic = ss.tic AND v.date = ss.date
    WHERE v.tic = $1
    ORDER BY v.date DESC
    LIMIT 1;
`;



const PROFITABILITY_METRICS_SEARCH_QUERY = `
    SELECT
      p.tic,
      p.date,
      -- final score
      ss.profitability_score AS score,

      -- profitability
      p.net_margin,
      p.operating_margin,
      p.gross_margin,
      p.ebitda_margin,

      p.roa,
      p.roe,
      ca.roic,
      p.ocf_margin,
      p.fcf_margin,

      -- profitability percentiles
      pp.gross_margin_percentile,
      pp.operating_margin_percentile,
      pp.ebitda_margin_percentile,
      pp.net_margin_percentile,
      pp.roe_percentile,
      pp.roa_percentile,
      cap.roic_percentile,
      pp.ocf_margin_percentile,
      pp.fcf_margin_percentile

    FROM core.profitability_metrics p
    JOIN core.profitability_percentiles pp
      ON p.inference_id = pp.inference_id
    JOIN core.capital_allocation_metrics ca
      ON p.tic = ca.tic AND p.date = ca.date
    JOIN core.capital_allocation_percentiles cap
      ON ca.inference_id = cap.inference_id
    JOIN core.stock_scores ss
      ON p.tic = ss.tic AND p.date = ss.date
    WHERE p.tic = $1
    ORDER BY p.date DESC
    LIMIT 1;
`;



const GROWTH_METRICS_SEARCH_QUERY = `
    SELECT
      g.tic,
      g.date,
      -- final score
      ss.growth_score AS score,

      -- growth
      g.revenue_growth_yoy,
      g.eps_growth_yoy,
      g.ebitda_growth_yoy,
      g.fcf_growth_yoy,
      
    
      g.revenue_cagr_3y,
      g.eps_cagr_3y,
      g.ebitda_cagr_3y,
      g.fcf_cagr_3y,
      
      g.operating_income_growth_yoy,
      g.forward_revenue_growth,
      g.forward_eps_growth,

      g.revenue_cagr_5y,
      g.eps_cagr_5y,
      g.ebitda_cagr_5y,
      g.fcf_cagr_5y,
      


      -- growth percentiles
      gp.revenue_growth_yoy_percentile,
      gp.revenue_cagr_3y_percentile,
      gp.eps_growth_yoy_percentile,
      gp.eps_cagr_3y_percentile,
      gp.fcf_growth_yoy_percentile,
      gp.fcf_cagr_3y_percentile,
      gp.ebitda_growth_yoy_percentile,
      gp.ebitda_cagr_3y_percentile,

      gp.revenue_cagr_5y_percentile,
      gp.eps_cagr_5y_percentile,
      gp.fcf_cagr_5y_percentile,
      gp.ebitda_cagr_5y_percentile,
      
      gp.operating_income_growth_yoy_percentile,
      gp.forward_revenue_growth_percentile,
      gp.forward_eps_growth_percentile

    FROM core.growth_metrics g
    JOIN core.growth_percentiles gp
      ON g.inference_id = gp.inference_id
    JOIN core.stock_scores ss
      ON g.tic = ss.tic AND g.date = ss.date
    WHERE g.tic = $1
    ORDER BY g.date DESC
    LIMIT 1;
`;



const EFFICIENCY_METRICS_SEARCH_QUERY = `
    SELECT
      e.tic,
      e.date,
      -- final score
      ss.efficiency_score AS score,

      -- efficiency
      e.asset_turnover,
      e.fixed_asset_turnover,
      e.opex_ratio,
      e.cash_conversion_cycle,
      e.dso,
      e.dio,
      e.dpo,
      e.revenue_per_employee,

      -- efficiency percentiles
      ep.asset_turnover_percentile,
      ep.cash_conversion_cycle_percentile,
      ep.dso_percentile,
      ep.dio_percentile,
      ep.dpo_percentile,
      ep.fixed_asset_turnover_percentile,
      ep.revenue_per_employee_percentile,
      ep.opex_ratio_percentile,
      ep.revenue_per_employee_percentile

    FROM core.efficiency_metrics e
    JOIN core.efficiency_percentiles ep
      ON e.inference_id = ep.inference_id
    JOIN core.stock_scores ss
      ON e.tic = ss.tic AND e.date = ss.date
    WHERE e.tic = $1
    ORDER BY e.date DESC
    LIMIT 1;
`;


const FINANCIAL_HEALTH_METRICS_SEARCH_QUERY = `
    SELECT
      fh.tic,
      fh.date,
      -- final score
      ss.financial_health_score AS score,

      -- financial health
      fh.net_debt_to_ebitda_ttm,
      fh.interest_coverage_ttm,
      fh.current_ratio,
      fh.quick_ratio,
      fh.cash_ratio,
      fh.debt_to_equity,
      fh.debt_to_assets,
      fh.altman_z_score,

      -- financial health percentiles
      fhp.net_debt_to_ebitda_ttm_percentile,
      fhp.interest_coverage_ttm_percentile,
      fhp.current_ratio_percentile,
      fhp.quick_ratio_percentile,
      fhp.cash_ratio_percentile,
      fhp.debt_to_equity_percentile,
      fhp.debt_to_assets_percentile,
      fhp.altman_z_score_percentile
    FROM core.financial_health_metrics fh
    JOIN core.financial_health_percentiles fhp
      ON fh.inference_id = fhp.inference_id
    JOIN core.stock_scores ss
      ON fh.tic = ss.tic AND fh.date = ss.date
    WHERE fh.tic = $1
    ORDER BY fh.date DESC
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
      for (const [key, value] of Object.entries(row as Record<string, any>)) {
          if (key.endsWith('_percentile') || key === 'category' || key === 'tic' || key === 'date' || key === 'score') continue; // Skip percentile entries
          const percentileKey = `${key}_percentile`;
          const metadata = (METRICS_METADATA as Record<string, any>)[key];
          if (!metadata) continue;
          const metric: Metric = {
              label: key,
              name: metadata.name,
              value: metadata.display_fn(value), // Convert value to string
              percentile: (row as any)[percentileKey] as number,
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
    FROM core.stock_scores ss
    WHERE ss.tic = $1
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