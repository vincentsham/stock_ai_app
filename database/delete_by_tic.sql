DELETE FROM raw.analyst_grades WHERE tic = 'TSM' ;
DELETE FROM raw.analyst_price_targets  WHERE tic = 'TSM' ;
DELETE FROM raw.balance_sheets_quarterly WHERE tic = 'TSM' ;
DELETE FROM raw.cash_flow_statements_quarterly  WHERE tic = 'TSM' ;
DELETE FROM raw.earnings  WHERE tic = 'TSM' ;
DELETE FROM raw.earnings_transcripts  WHERE tic = 'TSM' ;
DELETE FROM raw.income_statements_quarterly WHERE tic = 'TSM' ;
DELETE FROM raw.news  WHERE tic = 'TSM' ;
DELETE FROM raw.stock_ohlcv_daily WHERE tic = 'TSM' ;
DELETE FROM raw.stock_profiles WHERE tic = 'TSM' ;

-- core.analyst_grades                    core.efficiency_percentiles
-- core.analyst_price_targets             core.eps_diluted_metrics
-- core.analyst_rating_monthly_summary    core.financial_health_metrics
-- core.analyst_rating_quarterly_summary  core.financial_health_percentiles
-- core.analyst_rating_yearly_summary     core.growth_metrics
-- core.balance_sheets_quarterly          core.growth_percentiles
-- core.cash_flow_statements_quarterly    core.income_statements_quarterly
-- core.catalyst_master                   core.news
-- core.catalyst_master_embeddings        core.news_analysis
-- core.catalyst_version_embeddings       core.news_chunk_signal
-- core.catalyst_versions                 core.news_chunks
-- core.earnings                          core.news_embeddings
-- core.earnings_calendar                 core.profitability_metrics
-- core.earnings_metrics                  core.profitability_percentiles
-- core.earnings_transcript_analysis      core.revenue_metrics
-- core.earnings_transcript_chunk_signal  core.stock_profiles
-- core.earnings_transcript_chunks        core.stock_scores
-- core.earnings_transcript_embeddings    core.valuation_metrics
-- core.earnings_transcripts              core.valuation_percentiles
-- core.efficiency_metrics  

DELETE FROM core.analyst_grades WHERE tic = 'TSM' ;
DELETE FROM core.analyst_price_targets WHERE tic = 'TSM' ;
DELETE FROM core.analyst_rating_monthly_summary WHERE tic = 'TSM' ;
DELETE FROM core.analyst_rating_quarterly_summary WHERE tic = 'TSM' ;
DELETE FROM core.analyst_rating_yearly_summary WHERE tic = 'TSM' ;
DELETE FROM core.balance_sheets_quarterly WHERE tic = 'TSM' ;
DELETE FROM core.cash_flow_statements_quarterly WHERE tic = 'TSM' ;
DELETE FROM core.catalyst_master WHERE tic = 'TSM' ;
DELETE FROM core.catalyst_versions WHERE tic = 'TSM' ;
DELETE FROM core.earnings WHERE tic = 'TSM' ;
DELETE FROM core.earnings_calendar WHERE tic = 'TSM' ;
DELETE FROM core.earnings_metrics WHERE tic = 'TSM' ;
DELETE FROM core.earnings_transcript_analysis WHERE tic = 'TSM' ;
DELETE FROM core.earnings_transcript_chunk_signal WHERE tic = 'TSM' ;
DELETE FROM core.earnings_transcript_chunks WHERE tic = 'TSM' ;
DELETE FROM core.earnings_transcript_embeddings WHERE tic = 'TSM' ;
DELETE FROM core.earnings_transcripts WHERE tic = 'TSM' ;
DELETE FROM core.efficiency_metrics WHERE tic = 'TSM' ;
DELETE FROM core.efficiency_percentiles WHERE tic = 'TSM' ;
DELETE FROM core.eps_diluted_metrics WHERE tic = 'TSM' ;
DELETE FROM core.financial_health_metrics WHERE tic = 'TSM' ;
DELETE FROM core.financial_health_percentiles WHERE tic = 'TSM' ;
DELETE FROM core.growth_metrics WHERE tic = 'TSM' ;
DELETE FROM core.growth_percentiles WHERE tic = 'TSM' ;
DELETE FROM core.income_statements_quarterly WHERE tic = 'TSM' ;
DELETE FROM core.news WHERE tic = 'TSM' ;
DELETE FROM core.news_analysis WHERE tic = 'TSM' ;
DELETE FROM core.news_chunk_signal WHERE tic = 'TSM' ;
DELETE FROM core.news_chunks WHERE tic = 'TSM' ;
DELETE FROM core.news_embeddings WHERE tic = 'TSM' ;
DELETE FROM core.profitability_metrics WHERE tic = 'TSM' ;
DELETE FROM core.profitability_percentiles WHERE tic = 'TSM' ;
DELETE FROM core.revenue_metrics WHERE tic = 'TSM' ;
DELETE FROM core.stock_profiles WHERE tic = 'TSM' ;
DELETE FROM core.stock_scores WHERE tic = 'TSM' ;
DELETE FROM core.valuation_metrics WHERE tic = 'TSM' ;
DELETE FROM core.valuation_percentiles WHERE tic = 'TSM' ;   

-- mart.analyst_rating_yearly_summary  mart.earnings_transcript_analysis   mart.profitability_metrics
-- mart.catalyst_master                mart.efficiency_metrics             mart.stock_profiles
-- mart.earnings                       mart.financial_health_metrics       mart.stock_scores
-- mart.earnings_regime                mart.growth_metrics                 mart.valuation_metrics

DELETE FROM mart.analyst_rating_yearly_summary WHERE tic = 'TSM' ;
DELETE FROM mart.catalyst_master WHERE tic = 'TSM' ;
DELETE FROM mart.earnings WHERE tic = 'TSM' ;
DELETE FROM mart.earnings_regime WHERE tic = 'TSM' ;
DELETE FROM mart.earnings_transcript_analysis WHERE tic = 'TSM' ;
DELETE FROM mart.efficiency_metrics WHERE tic = 'TSM' ;
DELETE FROM mart.financial_health_metrics WHERE tic = 'TSM' ;
DELETE FROM mart.growth_metrics WHERE tic = 'TSM' ;
DELETE FROM mart.profitability_metrics WHERE tic = 'TSM' ;
DELETE FROM mart.stock_profiles WHERE tic = 'TSM' ;
DELETE FROM mart.stock_scores WHERE tic = 'TSM' ;
DELETE FROM mart.valuation_metrics WHERE tic = 'TSM' ;   