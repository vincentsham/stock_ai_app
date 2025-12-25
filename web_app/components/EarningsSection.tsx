'use client';

import { useState, useEffect } from 'react';
import { DollarSign } from 'lucide-react';
import { EarningsGraph, EarningsLegend } from './EarningsGraph';
import { EarningsGrowthGraph, EarningsGrowthLegend } from './EarningsGrowthGraph';
import { EarningsTag } from './EarningsTag';
import { searchEarnings, searchEarningsRegimes, searchEPSRegimes, searchRevenueRegimes } from '@/lib/db/earningsQueries';
import { Earnings, EarningsRegime, EPSRegime, RevenueRegime } from '@/types';
import { EARNINGS_TAG_METADATA } from '@/lib/constants';


export const EarningsSection: React.FC<{ tic: string }> = ({ tic }) => {
    const [isMounted, setIsMounted] = useState(false);
    const [activeTab, setActiveTab] = useState<'trend' | 'growth' | 'acceleration'>('trend');
    const [chartData, setChartData] = useState<(Earnings & { name: string })[]>([]);
    const [earningsRegimes, setEarningsRegimes] = useState<EarningsRegime | null>(null);
    const [epsRegimes, setEPSRegimes] = useState<EPSRegime | null>(null);
    const [revenueRegimes, setRevenueRegimes] = useState<RevenueRegime | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const data = await searchEarnings(tic);
            const dataWithNames = data.slice(-9).map(item => ({
              name: `${item.calendar_year.toString().slice(-2)}Q${item.calendar_quarter}`,
              ...item,
            }));
            setChartData(dataWithNames);
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
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setIsMounted(true);
    }, []);


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
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
              <div className="w-full md:w-1/3">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <DollarSign size={16}/>
                  Earnings History
                  {/* <span className="text-xs font-normal text-gray-500 bg-gray-800/50 px-2 py-1 rounded-full border border-gray-700">
                      Quarterly vs Est
                  </span> */}
                </h2>
                <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                  <span>Last 8 Quarters + Next Quarter Estimate</span>
                </div>
              </div>
            
            
              {/* View Tabs */}
                <div className="flex justify-center bg-gray-900/50 p-1 rounded-lg border border-gray-800 w-full md:w-1/3 md:items-center">
                  {['Trend', 'Growth', 'Acceleration'].map((tab) => (
                      <button
                          key={tab}
                          onClick={() => setActiveTab(tab.toLowerCase() as 'trend' | 'growth' | 'acceleration')}
                          className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                              activeTab === tab.toLowerCase()
                              ? 'bg-gray-700 text-white shadow-sm'
                              : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                          }`}
                      >
                          {tab}
                      </button>
                  ))}
              </div>



              {/* Legend */}
              <div className="md:w-1/3 md:ml-auto">
                {activeTab === 'trend'? <EarningsLegend />: <EarningsGrowthLegend />}
              </div>
              </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* EPS Chart */}
              <div className="bg-[#111218] p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-6 gap-4">
                  <h3 className="font-bold text-gray-200 flex items-center gap-2 text-sm w-30">
                    {activeTab === 'trend' ? 'EPS Trend' : activeTab === 'growth' ? 'EPS YoY Growth' : 'EPS YoY Acceleration'}
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
                {activeTab === 'trend' && <EarningsGraph data={chartData} metric="eps" />}
                {activeTab === 'growth' && <EarningsGrowthGraph data={chartData} metric="eps" type='growth' />}
                {activeTab === 'acceleration' && <EarningsGrowthGraph data={chartData} metric="eps" type='acceleration' />}
              </div>

              {/* Revenue Chart */}
              <div className="bg-[#111218] p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-6 gap-4">
                  <h3 className="font-bold text-gray-200 flex items-center gap-2 text-sm w-40">
                    {activeTab === 'trend' ? 'Revenue Trend' : activeTab === 'growth' ? 'Revenue YoY Growth' : 'Revenue YoY Acceleration'}
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
                {activeTab === 'trend' && <EarningsGraph data={chartData} metric="revenue" />}
                {activeTab === 'growth' && <EarningsGrowthGraph data={chartData} metric="revenue" type='growth' />}
                {activeTab === 'acceleration' && <EarningsGrowthGraph data={chartData} metric="revenue" type='acceleration' />}
              </div>

            </div>
      </div>
    );
  }
