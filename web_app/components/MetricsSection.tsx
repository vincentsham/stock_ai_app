'use client';

import { useState, useEffect, useMemo } from 'react';
import { BarChart3 } from 'lucide-react';
import {
  searchValuationMetrics,
  searchProfitabilityMetrics,
  searchGrowthMetrics,
  searchEfficiencyMetrics,
  searchFinancialHealthMetrics,
} from '@/lib/db/metricsQueries';
import { MetricList } from '@/types';
import { MetricCard } from './MetricCard';

interface AllMetrics {
    valuation: MetricList | null;
    profitability: MetricList | null;
    growth: MetricList | null;
    efficiency: MetricList | null;
    financialHealth: MetricList | null;
}

export const MetricsSection: React.FC<{ tic: string }> = ({ tic }) => {
    const [allMetrics, setAllMetrics] = useState<AllMetrics>({
        valuation: null,
        profitability: null,
        growth: null,
        efficiency: null,
        financialHealth: null,
    });

    
    useEffect(() => {
      const fetchAllData = async () => {
        try {
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

          setAllMetrics({
            valuation,
            profitability,
            growth,
            efficiency,
            financialHealth
          });
        } catch (error) {
          console.error("Failed to fetch metrics", error);
        }
      };
      fetchAllData();
      console.log("Fetched metrics for", tic);
    }, [tic]);
    
  
    const splitIntoColumns = (items: MetricList[], columnCount: number) => {
      const result: MetricList[][] = Array.from({ length: columnCount }, () => []);
      items.forEach((item, index) => {
        result[index % columnCount].push(item);
      });
      return result;
    };

    const columns = useMemo(() => Object.values(allMetrics), [allMetrics]);
    const baseCols = useMemo(() => splitIntoColumns(columns, 1), [columns]);
    const mdCols = useMemo(() => splitIntoColumns(columns, 2), [columns]);
    const lgCols = useMemo(() => splitIntoColumns(columns, 3), [columns]);

    return (
      <div className="animate-slide-up-fade" style={{ animationDuration: '0.4s' }}>
        <div className="flex items-center justify-between mb-6">
          <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <BarChart3 size={16}/>
                  Fundamental Metrics
              </h2>
              <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                  <span>Percentile rankings vs 100+ Selected Stocks</span>
              </div>
          </div>
          
        </div>

        <div className="grid grid-cols-1 gap-6 items-start md:hidden">
          {baseCols[0]?.map((colItem, index) => (
            colItem && (
            <div key={`${tic}-metrics-base-${index}`} className="w-full">
              <MetricCard key={`${tic}-metrics-base-${index}`} 
                          category={colItem.category} 
                          tic={colItem.tic} 
                          score={colItem.score}
                          metrics={colItem.metrics} 
                          defaultVisibleCount={colItem.defaultVisibleCount} />
            </div>
          )
          ))}
        </div>

        <div className="hidden md:grid md:grid-cols-2 md:gap-6 md:items-start lg:hidden">
          {mdCols.map((col, colIndex) => (
            <div key={`${tic}-metrics-md-col-${colIndex}`} className="flex flex-col gap-6 w-full">
              {col.map((colItem, index) => (
                colItem && (
                <MetricCard key={`${tic}-metrics-md-${colIndex}-${index}`} 
                            category={colItem.category} 
                            tic={colItem.tic} 
                            score={colItem.score}
                            metrics={colItem.metrics} 
                            defaultVisibleCount={colItem.defaultVisibleCount} />
              )
              ))}
            </div>
          ))}
        </div>

        <div className="hidden lg:grid lg:grid-cols-3 lg:gap-6 lg:items-start">
          {lgCols.map((col, colIndex) => (
            <div key={`${tic}-metrics-lg-col-${colIndex}`} className="flex flex-col gap-6 w-full">
              {col.map((colItem, index) => (
                colItem && (
                <MetricCard key={`${tic}-metrics-lg-${colIndex}-${index}`} 
                            category={colItem.category} 
                            tic={colItem.tic} 
                            score={colItem.score}
                            metrics={colItem.metrics} 
                            defaultVisibleCount={colItem.defaultVisibleCount} />
              )
              ))}
            </div>
          ))}
        </div>
        
      </div>
    );
};