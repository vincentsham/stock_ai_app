'use client';

import { StockScores } from '@/types';
import { useState, useEffect } from 'react';
import { searchStockScores } from '@/lib/db/metricsQueries';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

type StockRadarChartProps = {
    tic: string;
    height?: number;
    className?: string;
};

const StockRadarChart: React.FC<StockRadarChartProps> = ({ tic, height = 400 }) => {
    const [scores, setScores] = useState<StockScores | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const data = await searchStockScores(tic);
            setScores(data);
        };
        fetchData();
    }, [tic]);

    // Data ordered specifically: Valuation -> Profitability -> Efficiency -> Fin. Health -> Growth
    const data = [
        { subject: 'Valuation', score: Math.round(scores?.valuation_score ?? 0) },
        { subject: 'Profitability', score: Math.round(scores?.profitability_score ?? 0) },
        { subject: 'Efficiency', score: Math.round(scores?.efficiency_score ?? 0) },
        { subject: 'Fin. Health', score: Math.round(scores?.financial_health_score ?? 0) },
        { subject: 'Growth', score: Math.round(scores?.growth_score ?? 0) },
    ];

    // Custom Tick Component to render Label + Score
    interface CustomTickProps {
        payload: { value: string };
        x?: number;
        y?: number;
        cx?: number;
        cy?: number;
    }

    const CustomTick = ({ payload, x, y, cx, cy }: CustomTickProps) => {
        const metric = data.find(d => d.subject === payload.value);

        // logic to push labels outward based on their position relative to center
        const isTop = y !== undefined && cy !== undefined && y < cy;

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
                    className="uppercase tracking-wider font-sans"
                >
                    {payload.value}
                </text>
                <text
                    x={0}
                    y={0}
                    dy={isTop ? 5 : 30}
                    textAnchor="middle"
                    fill="white"
                    fontSize={10}
                    fontWeight={700}
                    className="font-sans"
                >
                    {metric?.score}
                </text>
            </g>
        );
    };

    return (
        <div className="w-full" style={{ height: `${height}px` }}>
            {/* Main Card Container */}
            <div className="h-full w-full bg-[#0c0e15] rounded-3xl border border-gray-800 shadow-2xl overflow-hidden relative">
                {/* Overall Score - Top Right */}
                <div className="absolute top-4 right-4 flex items-center space-x-2 z-10">
                    <div className="flex flex-col text-[12px] leading-tight text-slate-500 font-medium text-right">
                        <span>OVERALL</span>
                        <span>SCORE</span>
                    </div>
                    <span className="text-3xl font-bold text-white">{Math.round(scores?.total_score ?? 0)}</span>
                </div>

                {/* Chart Area */}
                <div className="h-full w-full flex justify-center items-center py-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="65%" data={data}>
                            <defs>
                                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                                    <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                                    <feMerge>
                                        <feMergeNode in="coloredBlur" />
                                        <feMergeNode in="SourceGraphic" />
                                    </feMerge>
                                </filter>
                            </defs>

                            <PolarGrid gridType="polygon" stroke="#334155" strokeDasharray="4 4" />

                            <PolarAngleAxis
                                dataKey="subject"
                                tick={(props) => <CustomTick {...(props as CustomTickProps)} />}
                            />

                            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />

                            <Radar
                                name="Stock"
                                dataKey="score"
                                stroke="#38bdf8"
                                strokeWidth={3}
                                fill="none"
                                filter="url(#glow)"
                                isAnimationActive={true}
                                dot={{ r: 4, fill: '#0c0e15', stroke: '#38bdf8', strokeWidth: 2 }}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default StockRadarChart;