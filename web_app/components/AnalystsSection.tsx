'use client';

import { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import { AnalystPTGraph } from './AnalystPTGraph';
import { AnalystGradeCard } from './AnalystGradeCard';
import { AnalystPTCard } from './AnalystPTCard';
import { AnalystAnalysis } from '@/types';
import { searchAnalystAnalysis, getLatestAnalystAnalysisDate } from '@/lib/db/analystQueries';


export const AnalystsSection: React.FC<{ tic: string }> = ({ tic }) => {
    const [analystData, setAnalystData] = useState<AnalystAnalysis[]>([]);
    const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
    
    useEffect(() => {
        const fetchData = async () => {
            const updatedAt = await getLatestAnalystAnalysisDate(tic.trim().toUpperCase());
            setLastUpdatedAt(updatedAt);
            const data = await searchAnalystAnalysis(tic);
            setAnalystData(data);
        };
        fetchData();
    }, [tic]);


    return (
        analystData.length && (
        <div className="animate-slide-up-fade" style={{ animationDuration: '0.4s' }}>
          {/* Main Section Header */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Users size={16}/>
                  Analyst Analysis
                  {/* <span className="text-xs font-normal text-gray-500 bg-gray-800/50 px-2 py-1 rounded-full border border-gray-700">
                      AI Generated
                  </span> */}
              </h2>
              <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                  Aggregated ratings & 12-month price forecasts from Wall Street analysts
              </div>
            </div>
                <div className="text-xs text-gray-500 flex flex-col md:flex-row items-start md:items-center gap-1 md:justify-end mt-2 md:mt-0">
                    {lastUpdatedAt ? (
                        <>Last updated: <span className="font-mono">{new Date(lastUpdatedAt).toLocaleDateString()}</span></>
                    ) : null}
                </div>
          </div>

          {/* Top Cards Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <AnalystGradeCard data={analystData[0]}/>
            <AnalystPTCard data={analystData[0]}/>
          </div>

          {/* Graph Container */}
          <div className="bg-[#111218] p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-colors">
            <AnalystPTGraph data={analystData} />
          </div>
        </div>
    ))
};


