'use client';

import { useState, useEffect, useMemo } from 'react';
import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer,
    Legend,
    Tooltip
} from 'recharts';
import { StockScores } from '@/types';
import { searchStockScores } from '@/lib/db/metricsQueries';
import { Radar as RadarIcon } from 'lucide-react'


// --- Constants ---
const COLORS = [
    '#38bdf8', // Sky Blue
    '#a855f7', // Purple
    '#4ade80', // Green
    '#f472b6', // Pink
    '#fbbf24', // Amber
    '#ef4444', // Red
];


export const MultiStockRadarChart: React.FC<{tics: string[], height?: number}> = ({ tics, height = 500 }) => {
    const [dataset, setDataset] = useState<StockScores[]>([]);

useEffect(() => {
        let isMounted = true;

        const fetchScores = async () => {
            try {
                // 1. Fire all requests simultaneously
                const promises = tics.map(tic => searchStockScores(tic));
                
                // 2. Wait for all of them to finish
                const results = await Promise.all(promises);

                // 3. Filter out nulls and update state
                if (isMounted) {
                    const validResults = results.filter((r): r is StockScores => r !== null);
                    setDataset(validResults);
                }
            } catch (error) {
                console.error("Failed to fetch stock scores:", error);
            }
        };

        if (tics.length > 0) {
            fetchScores();
        } else {
            setDataset([]);
        }

        return () => { isMounted = false; };
    }, [tics]);

    
    // Transform data for Recharts: Array of subjects, with keys for each ticker
    const chartData = useMemo(() => {
        const subjects = ['Valuation', 'Profitability', 'Efficiency', 'Fin. Health', 'Growth'] as const;
        const keyMap: Record<string, keyof StockScores> = {
            'Valuation': 'valuation_score',
            'Profitability': 'profitability_score',
            'Efficiency': 'efficiency_score',
            'Fin. Health': 'financial_health_score',
            'Growth': 'growth_score',
        };

        return subjects.map((subject) => {
            const entry: any = { subject };
            dataset.forEach((item) => {
                entry[item.tic] = Math.round(Number(item[keyMap[subject]] ?? 0));
            });
            return entry;
        });
    }, [dataset]);

    const chartHeight = Math.max(1, height - 32);

    // Custom Tick Component for the axis labels
    const CustomTick = ({ payload, x, y, cy }: any) => {
        const isTop = y < cy;
        return (
            <g transform={`translate(${x},${y})`}>
                <text
                    x={0}
                    y={0}
                    dy={isTop ? -10 : 15}
                    textAnchor="middle"
                    fill="#94a3b8"
                    fontSize={11}
                    fontWeight={600}
                    className="uppercase tracking-wider font-sans select-none"
                >
                    {payload.value}
                </text>
            </g>
        );
    };

    // Custom Tooltip to show a clean list of scores
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-[#0f172a]/95 border border-slate-700 p-3 rounded-xl shadow-xl backdrop-blur-sm">
                    <p className="text-slate-200 font-bold mb-2 text-sm uppercase tracking-wider">{label}</p>
                    {payload.map((entry: any, index: number) => (
                        <div key={index} className="flex items-center gap-2 text-xs mb-1">
                            <div 
                                className="w-2 h-2 rounded-full" 
                                style={{ backgroundColor: entry.color }}
                            />
                            <span className="text-slate-400 font-medium w-12">{entry.name}:</span>
                            <span className="text-white font-mono">{entry.value}</span>
                        </div>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="h-full w-full mt-2" style={{ height }}>
            <div className="h-full w-full max-w-[560px] mx-auto bg-[#0c0e15] rounded-3xl border border-gray-800 shadow-2xl overflow-hidden relative flex flex-col">
                <div className="absolute top-4 left-6 z-10 pointer-events-none">
                    <h3 className="text-white font-bold text-lg tracking-tight"><RadarIcon className="inline-block mr-2" />Multi-Factor Stock Comparison</h3>
                    <p className="text-slate-500 text-xs font-medium">
                        Compare stocks across valuation, growth, profitability, efficiency, and financial health.
                    </p>
                </div>

                <div className="flex-1 w-full py-2 pt-8">
                    <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
                            <PolarGrid 
                                gridType="polygon" 
                                stroke="#334155" 
                                strokeDasharray="4 4" 
                                strokeWidth={1}
                            />
                            
                            <PolarAngleAxis 
                                dataKey="subject" 
                                tick={(props) => <CustomTick {...props} />} 
                            />
                            
                            <PolarRadiusAxis 
                                angle={90} 
                                domain={[0, 100]} 
                                tick={false} 
                                axisLine={false} 
                            />

                            {dataset.map((item, index) => (
                                <Radar
                                    key={item.tic}
                                    name={item.tic}
                                    dataKey={item.tic}
                                    stroke={COLORS[index % COLORS.length]}
                                    strokeWidth={3}
                                    fill={COLORS[index % COLORS.length]}
                                    fillOpacity={0.15}
                                    isAnimationActive={true}
                                    dot={{ r: 3, fillOpacity: 1, strokeWidth: 0 }}
                                    activeDot={{ r: 4, strokeWidth: 0 }}
                                />
                            ))}

                            <Legend 
                                wrapperStyle={{ paddingTop: '10px' }}
                                iconType="circle"
                                formatter={(value) => <span className="text-sm text-slate-300 font-medium ml-1">{value}</span>}
                            />
                            
                            <Tooltip content={<CustomTooltip />} />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
