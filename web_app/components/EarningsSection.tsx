'use client';

import { useState, useMemo, useEffect } from 'react';
import { TrendingUp, DollarSign, Activity } from 'lucide-react';
import { EarningsGraph } from './EarningsGraph';
import { EarningsTag } from './EarningsTag';
import { searchEarnings, searchEarningsRegimes, searchEPSRegimes, searchRevenueRegimes } from '@/lib/db/earningsQueries';
import { Earnings, EarningsRegime, EPSRegime, RevenueRegime } from '@/types';
import { EARNINGS_TAG_METADATA } from '@/lib/constants';


export const EarningsSection: React.FC<{ tic: string }> = ({ tic }) => {
    const [isMounted, setIsMounted] = useState(false);
    const [earningsData, setEarningsData] = useState<Earnings[]>([]);
    const [earningsRegimes, setEarningsRegimes] = useState<EarningsRegime | null>(null);
    const [epsRegimes, setEPSRegimes] = useState<EPSRegime | null>(null);
    const [revenueRegimes, setRevenueRegimes] = useState<RevenueRegime | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const data = await searchEarnings(tic);
            setEarningsData(data);
            const earningsRegimes = await searchEarningsRegimes(tic);
            setEarningsRegimes(earningsRegimes);
            const epsRegimes = await searchEPSRegimes(tic);
            setEPSRegimes(epsRegimes);
            const revenueRegimes = await searchRevenueRegimes(tic);
            setRevenueRegimes(revenueRegimes);
        };
        fetchData();
    }, [tic]);

    // Ensure charts only render on client to avoid hydration mismatch
    useEffect(() => {
      setIsMounted(true);
    }, []);

    // Process data for charts
    const chartData = useMemo(() => {
      // Slice to show the last 9 quarters (2 years + 1 future quarter)
      // const sortedEarningsData = [...earningsData].sort((a, b) => {
      //   if (a.tic !== b.tic) return a.tic.localeCompare(b.tic);
      //   if (a.calendar_year !== b.calendar_year) return a.calendar_year - b.calendar_year;
      //   return a.calendar_quarter - b.calendar_quarter;
      // });
      return earningsData.slice(-9).map(item => ({
        // Format as YYQ# (e.g., 23Q4)
        name: `${item.calendar_year.toString().slice(-2)}Q${item.calendar_quarter}`,
        ...item,
      }));
    }, [earningsData]);

    if (!isMounted) {
      return (
          <div className="min-h-[400px] w-full flex items-center justify-center text-gray-500 animate-pulse">
              Loading Market Data...
          </div>
      );
    }

    return (
      <div className="animate-slide-up-fade" style={{ animationDuration: '0.4s' }}>
            
            {/* Header Area */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  Earnings History
                  {/* <span className="text-xs font-normal text-gray-500 bg-gray-800/50 px-2 py-1 rounded-full border border-gray-700">
                      Quarterly vs Est
                  </span> */}
                </h2>
                <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                  <Activity size={12}/>
                  <span>Last 8 Quarters + Next Quarter Estimate</span>
                </div>
              </div>

              {/* Legend */}
              <div className="flex gap-4 text-[10px] uppercase font-bold tracking-wider bg-[#111218] px-3 py-2 rounded-lg border border-gray-800 w-fit">
                <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[#10b981]"></div>
                    <span className="text-gray-400">Beat</span>
                </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[#3b82f6]"></div>
                    <span className="text-gray-400">In-Line</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[#f43f5e]"></div>
                    <span className="text-gray-400">Miss</span>
                </div>
                <div className="flex items-center gap-1.5 border-l border-gray-700 pl-3 ml-1">
                    <div className="w-2 h-2 rounded-full bg-[#64748b]"></div>
                    <span className="text-gray-400">Estimate</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* EPS Chart */}
              <div className="bg-[#111218] p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
                  <h3 className="font-bold text-gray-200 flex items-center gap-2 text-sm">
                    {/* <div className="p-1 bg-blue-500/10 rounded">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                    </div> */}
                    EPS Trend
                  </h3>
                  {/* EPS Summary Labels */}
                  <div className="flex flex-wrap gap-2">
                    {earningsRegimes?.eps_surprise_regime && EARNINGS_TAG_METADATA[earningsRegimes.eps_surprise_regime] && (
                      <EarningsTag
                        label={EARNINGS_TAG_METADATA[earningsRegimes.eps_surprise_regime]?.label}
                        description={ `EPS: ${EARNINGS_TAG_METADATA[earningsRegimes.eps_surprise_regime]?.description}` }
                        className={EARNINGS_TAG_METADATA[earningsRegimes.eps_surprise_regime]?.className}
                      />
                    )}
                    {epsRegimes?.yoy_growth_regime && EARNINGS_TAG_METADATA[epsRegimes.yoy_growth_regime] && (
                      <EarningsTag
                        label={EARNINGS_TAG_METADATA[epsRegimes.yoy_growth_regime]?.label}
                        description={ `EPS: ${EARNINGS_TAG_METADATA[epsRegimes.yoy_growth_regime]?.description}` }
                        className={EARNINGS_TAG_METADATA[epsRegimes.yoy_growth_regime]?.className}
                      />
                    )}
                    {epsRegimes?.yoy_accel_regime && EARNINGS_TAG_METADATA[epsRegimes.yoy_accel_regime] && (
                      <EarningsTag
                        label={EARNINGS_TAG_METADATA[epsRegimes.yoy_accel_regime]?.label}
                        description={ `EPS: ${EARNINGS_TAG_METADATA[epsRegimes.yoy_accel_regime]?.description}` }
                        className={EARNINGS_TAG_METADATA[epsRegimes.yoy_accel_regime]?.className}
                      />
                    )}
                  </div>
                </div>
                
                <EarningsGraph data={chartData} metric="eps" />
              </div>

              {/* Revenue Chart */}
              <div className="bg-[#111218] p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
                  <h3 className="font-bold text-gray-200 flex items-center gap-2 text-sm">
                    {/* <div className="p-1 bg-emerald-500/10 rounded">
                      <DollarSign className="w-4 h-4 text-emerald-400" />
                    </div> */}
                    Revenue Trend
                  </h3>
                  {/* Revenue Summary Labels */}
                  <div className="flex flex-wrap gap-2">
                    {earningsRegimes?.revenue_surprise_regime && EARNINGS_TAG_METADATA[earningsRegimes.revenue_surprise_regime] && (
                      <EarningsTag
                        label={EARNINGS_TAG_METADATA[earningsRegimes.revenue_surprise_regime]?.label}
                        description={ `Revenue: ${EARNINGS_TAG_METADATA[earningsRegimes.revenue_surprise_regime]?.description}` }
                        className={EARNINGS_TAG_METADATA[earningsRegimes.revenue_surprise_regime]?.className}
                      />
                    )}
                    {revenueRegimes?.yoy_growth_regime && EARNINGS_TAG_METADATA[revenueRegimes.yoy_growth_regime] && (
                      <EarningsTag
                        label={EARNINGS_TAG_METADATA[revenueRegimes.yoy_growth_regime]?.label}
                        description={ `Revenue: ${EARNINGS_TAG_METADATA[revenueRegimes.yoy_growth_regime]?.description}` }
                        className={EARNINGS_TAG_METADATA[revenueRegimes.yoy_growth_regime]?.className}
                      />
                    )}
                    {revenueRegimes?.yoy_accel_regime && EARNINGS_TAG_METADATA[revenueRegimes.yoy_accel_regime] && (
                      <EarningsTag
                        label={EARNINGS_TAG_METADATA[revenueRegimes.yoy_accel_regime]?.label}
                        description={ `Revenue: ${EARNINGS_TAG_METADATA[revenueRegimes.yoy_accel_regime]?.description}` }
                        className={EARNINGS_TAG_METADATA[revenueRegimes.yoy_accel_regime]?.className}
                      />
                    )}
                  </div>
                </div>
                <EarningsGraph data={chartData} metric="revenue" />
              </div>

            </div>
      </div>
    );
  }
