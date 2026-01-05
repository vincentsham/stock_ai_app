'use client';

import { Calendar } from 'lucide-react';
import { EarningsCallCard } from './EarningsCallCard';
import { useState, useEffect } from 'react';
import { EarningsCallAnalysis } from '@/types';
import { searchEarningsCalls, getLatestEarningsCallDate} from "@/lib/db/earningsCallQueries";

export const EarningsCallsSection: React.FC<{ tic: string }> = ( {tic} ) => {
    const [earningsCallAnalysis, setEarningsCallAnalysis] = useState<EarningsCallAnalysis[]>([]);
    const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const updatedAt = await getLatestEarningsCallDate(tic.trim().toUpperCase());
            setLastUpdatedAt(updatedAt);
            const data = await searchEarningsCalls(tic);
            setEarningsCallAnalysis(data);
        };
        fetchData();
    }, [tic]);


    // Sort earnings by year then quarter descending
    const sortedEarnings = [...earningsCallAnalysis].sort((a, b) => {
        if (a.calendar_year !== b.calendar_year) return b.calendar_year - a.calendar_year;
        return b.calendar_quarter - a.calendar_quarter;
    });

    return (
      <div className="animate-slide-up-fade" style={{ animationDuration: '0.4s' }}>
          <div className="flex items-center justify-between mb-6">
            <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Calendar size={16}/>
                    Earnings Call Analysis
                    <span className="text-xs font-normal text-gray-500 bg-gray-800/50 px-2 py-1 rounded-full border border-gray-700">
                        AI Generated
                    </span>
                </h2>
                <div className="text-xs text-gray-500 flex items-center gap-1">
                    Key takeaways from last {sortedEarnings.length} earnings calls
                </div>
            </div>
                 <div className="text-xs text-gray-500 flex flex-col md:flex-row items-start md:items-center gap-1 md:justify-end mt-2 md:mt-0">
                    {lastUpdatedAt ? (
                        <>
                            <span>Last updated:</span>
                            <span className="font-mono">{new Date(lastUpdatedAt).toLocaleDateString()}</span>
                        </>
                    ) : null}
                </div>
          </div>

          <div className="space-y-4">
            {sortedEarnings.map((report) => (
                <EarningsCallCard key={report.inference_id} report={report} />
            ))}
          </div>

          {sortedEarnings.length === 0 && (
              <div className="py-12 flex flex-col items-center justify-center text-gray-500 border border-dashed border-gray-800 rounded-xl">
                  <div className="w-12 h-12 bg-gray-800/50 rounded-full flex items-center justify-center mb-3">
                    <Calendar size={24} className="text-gray-600" />
                  </div>
                  <p>No earnings data available for this ticker.</p>
              </div>
          )}
      </div>
    )
}