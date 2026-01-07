"use client";

import { useState, useMemo, useEffect } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { StockCompareCard } from '@/components/StockCompareCard';
import { StockEmptyCard } from './StockEmptyCard';
import { StockProfile, StockScores, AllMetrics } from '@/types';
import { MultiStockRadarChart } from './MultiStockRadarChart';
import { searchStock } from '@/lib/db/stockQueries';
import { searchValuationMetrics, searchProfitabilityMetrics, 
         searchGrowthMetrics, searchEfficiencyMetrics, 
         searchFinancialHealthMetrics } from '@/lib/db/metricsQueries';
import { searchStockScores, getLatestStockScoresDate } from '@/lib/db/metricsQueries';
import { MAX_COMPARE_STOCKS, NUM_STOCKS } from '@/lib/constants';



export const CompareMain = () => {
    const [viewMode, setViewMode] = useState<'metrics' | 'radar'>('metrics');
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);

    // 1. URL is the Driver (Order & Existence)
    const urlTickers = useMemo(() => {
        const param = searchParams.get('stocks');
        return param ? param.split(',').filter(Boolean) : [];
    }, [searchParams]);

    useEffect(() => {
        const fetchLatestDate = async () => {
            const updatedAt = await getLatestStockScoresDate(null);
            setLastUpdatedAt(updatedAt);
        };
        fetchLatestDate();
    }, []);

    // --- EFFECT: Ensure at least 3 stocks in URL on first load ---
    useEffect(() => {
        const defaultTics = ['NVDA', 'AAPL', 'TSLA'];
        if (!searchParams.has('stocks')) {
            const params = new URLSearchParams();
            params.set('stocks', defaultTics.join(',')); // Join by comma
            router.replace(`${pathname}?${params.toString()}`);
        }
    }, [searchParams, pathname, router]);

    // 2. State is just a "Cache" of data we have fetched
    // We use a Record (Object) for O(1) lookups.
    const [stockCache, setStockCache] = useState<Record<string, {profile: StockProfile, metrics: AllMetrics, scores: StockScores}>>({});
    const [expandedStates, setExpandedStates] = useState<boolean[]>([false, false, false, false, false]);
   
    const toggleMetric = (targetIndex: number) => {
      // 1. Force targetIndex to be a number (Safety check)
      const safeIndex = Number(targetIndex);
      setExpandedStates((prev) => 
        prev.map((item, index) => {
          // 2. Debug the comparison (Check your console after clicking!)
          if (index === safeIndex) {
              return !item;
          }
          return item;
        })
      );
    };


    // 3. Sync Effect: Fetch missing data
    useEffect(() => {
        let isMounted = true;
        const fetchMissing = async () => {
            // Find which tickers in URL are missing from our cache
            const missing = urlTickers.filter(tic => !stockCache[tic]?.profile);

            if (missing.length === 0) return;

            const newProfiles: Record<string, {profile: StockProfile, metrics: AllMetrics, scores: StockScores}> = {};
            
            await Promise.all(missing.map(async (tic) => {
              try {
                const profile = await searchStock(tic);
                const [
                      valuation, 
                      profitability, 
                      growth, 
                      efficiency, 
                      financialHealth
                      ] = await Promise.all([
                              searchValuationMetrics(tic),
                              searchProfitabilityMetrics(tic),
                              searchGrowthMetrics(tic),
                              searchEfficiencyMetrics(tic),
                              searchFinancialHealthMetrics(tic),
                          ]);
                const allMetrics: AllMetrics = {
                              valuation,
                              profitability,
                              growth,
                              efficiency,
                              financialHealth,
                      };
                const scores = await searchStockScores(tic);
                if (profile) {
                  newProfiles[tic] = { profile, metrics: allMetrics, scores };
                }
              } catch (e) {
                console.error(`Failed to load ${tic}`, e);
              }
            }));

            // FIX: Only update state if we actually got new data
            // This prevents the infinite loop if a stock fails to load
            if (Object.keys(newProfiles).length > 0) {
                setStockCache(prev => ({ ...prev, ...newProfiles }));
            }
        };

        fetchMissing();
        return () => { isMounted = false; };
    }, [urlTickers, stockCache]);

    const processedStockDate = useMemo(() => {
        if (Object.keys(stockCache).length === 0) return {};
        // Compare the metrics acrooss all stocks to determine which metrics get highlighted
      
        // 1. Create a DEEP COPY. Now 'newCache' shares NO references with 'stockCache'.
        const newCache = structuredClone(stockCache);
        const allMetricsKeys = ['valuation', 'profitability', 'growth', 'efficiency', 'financialHealth'] as const;

        allMetricsKeys.forEach((metricKey, metricIndex) => {
            // Gather all metric lists for this key
            const metricLists = urlTickers.map(tic => newCache[tic]?.metrics[metricKey]).filter(Boolean);

            if (metricLists.length === 0) return;

            // For each metric in the first stock's list, compare across others
            const baseMetrics = metricLists[0]?.metrics;
            const baseScore = metricLists[0]?.score;

            if (!baseMetrics) return;

            let bestScore: number | null = baseScore ?? null;
            metricLists.forEach((ml) => {
                if (ml && ml.score !== null) {
                    if (bestScore === null) {
                        bestScore = ml.score;
                    } 
                    if (ml.score > bestScore) {
                        bestScore = ml.score;
                    }
                }
            });
            // Mark the best overall score
            metricLists.forEach((ml) => {
                if (ml) {
                    if (ml.score === bestScore && bestScore !== null) {
                        ml.highlight = true;
                    } else {
                        ml.highlight = false;
                    }
                }
            });

            // Now determine best metrics within this category

            baseMetrics.forEach((baseMetric) => {
                let bestPercentile: number | null = baseMetric.percentile;

                metricLists.forEach((ml) => {
                    const compareMetric = ml && ml.metrics ? ml.metrics.find(m => m.name === baseMetric.name) : undefined;
                    if (compareMetric) {
                        // Determine if we are looking for max or min based on inverse
                        if (bestPercentile === null) {
                            bestPercentile = compareMetric.percentile;
                        } 
                        if (baseMetric.inverse) {
                            if (compareMetric.percentile !== null && bestPercentile !== null && compareMetric.percentile < bestPercentile) {
                                bestPercentile = compareMetric.percentile;
                            }
                        } else {
                            // Higher is better
                            if (compareMetric.percentile !== null && bestPercentile !== null && compareMetric.percentile > bestPercentile) {
                                bestPercentile = compareMetric.percentile;
                            }
                        }
                    }
                });

                // Now mark the best metrics
                metricLists.forEach((ml) => {
                    if (ml && ml.metrics) {
                        const metricToMark = ml.metrics.find(m => m.name === baseMetric.name);
                        if (metricToMark) {
                            if (metricToMark.percentile === bestPercentile && bestPercentile !== null) {
                                metricToMark.highlight = true;
                            } else {
                                metricToMark.highlight = false;
                            }
                        }
                    }
                });
            });
        });
        // Only update state if we made changes
        return newCache;

    }, [stockCache, urlTickers]);




    // 4. Helper to remove (Writes to URL)
    const onRemove = (ticToRemove: string) => {
        const newTickers = urlTickers.filter(Boolean).filter(t => t !== ticToRemove);
        const params = new URLSearchParams();

        if (newTickers.length > 0) {
            params.set('stocks', newTickers.join(','));
        } else {
            params.set('stocks', '');
        }
        
        router.push(`${pathname}?${params.toString()}`);
    };

    const isLimitReached = urlTickers.length >= MAX_COMPARE_STOCKS;

    return (
        <div className="w-full bg-[#0c0e15] border border-gray-800 rounded-xl p-6 pt-1">
            {/* View Tabs */}
            <div>
              <div className="relative flex flex-col md:flex-row justify-center items-center w-full">
                <div className="flex bg-black rounded-lg p-1">
                  {['Metrics', 'Radar'].map((tab, idx) => (
                    <button
                      key={tab}
                      onClick={() => setViewMode(tab.toLowerCase() as 'metrics' | 'radar')}
                      className={`px-3 py-1 text-xs font-medium rounded-md transition-all mx-0.5 ${
                        viewMode === tab.toLowerCase()
                        ? 'bg-gray-600 text-white shadow-sm'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700 cursor-pointer'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
                <div className="mt-2 md:mt-0 md:absolute md:right-0 text-xs text-gray-500 flex items-center gap-1">
                    {lastUpdatedAt ? (
                        <>Last updated: <span className="font-mono">{new Date(lastUpdatedAt).toLocaleDateString()}</span></>
                    ) : (
                        null
                    )}
                </div>
            </div>
            
          </div>

        {/* Main Comparison Area */}
        <div className="w-full overflow-x-auto pt-2 pb-6 scrollbar-hide">
          <div className="flex space-x-2 md:space-x-4 w-fit mx-auto justify-start px-2 items-stretch">
            {urlTickers.length > 0 ? (
              <>
                {urlTickers.map((tic) => {
                const data = processedStockDate[tic]; // Lookup data
                
                // 5. Pass distinct loading state to each card
                // If data is undefined, it means we are still fetching it.
                return (
                    <StockCompareCard
                        key={tic} 
                        tic={tic}          // Pass ticker even if loading
                        stockProfile={data?.profile}         // Pass data (might be undefined)
                        stockScores={data?.scores}           // Pass scores (might be undefined)
                        stockMetrics={data?.metrics}         // Pass metrics (might be undefined)
                        showMetrics={viewMode === 'metrics'} // Show metrics only in 'metrics' view
                        onRemove={() => onRemove(tic)}
                        expandedStates={expandedStates}  // Pass current expanded states
                        toggleMetric={toggleMetric}      // Pass toggle function
                        isLoading={!data}      // True if data is missing
                    />
                  );
              })}
                
                {!isLimitReached && (
                  <StockEmptyCard />
                )}
              </>
            ) : (
              <StockEmptyCard />
            )}
          </div>
          {viewMode === 'radar' && urlTickers.length > 0 && (
            <div className="w-full h-[500px] px-4">
              <MultiStockRadarChart tics={urlTickers} height={500} />
            </div>
          )}
        </div>
        {viewMode == 'metrics' && (<div className="w-full text-xs text-gray-500 flex items-center justify-end gap-1 mt-1">
			    <span>* Percentile rankings vs {NUM_STOCKS}+ Selected Stocks</span>
		    </div>)}
      </div>
    );
}

