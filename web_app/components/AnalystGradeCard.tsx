
'use client';


import { AnalystAnalysis } from '@/types';
import { Info } from 'lucide-react';

export const AnalystGradeCard: React.FC<{ data: AnalystAnalysis }> = ({ data }) => {
    // Mock Data
    const ratings = {
        sell: data.grade_sell_n,
        hold: data.grade_hold_n,
        buy: data.grade_buy_n
    };
    
    // Gauge Value (0 to 1)
    const gaugeValue = ((ratings.buy ?? 0) + (ratings.hold ?? 0) / 2) / ((ratings.sell ?? 0) + (ratings.hold ?? 0) + (ratings.buy ?? 0) + 0.0001); 

    let finalRating;
    let finalRatingColor;
    if (gaugeValue <= 0.2) {
        finalRating = 'Strong Sell';
        finalRatingColor = '#ef4444'; 
    } else if (gaugeValue <= 0.4) {
        finalRating = 'Sell';
        finalRatingColor = '#ef4444';
    } else if (gaugeValue <= 0.6) {
        finalRating = 'Hold';
        finalRatingColor = '#f59e0b';
    } else if (gaugeValue <= 0.8) {
        finalRating = 'Buy';
        finalRatingColor = '#10b981';
    } else {
        finalRating = 'Strong Buy';
        finalRatingColor = '#10b981'; 
    }

    // Gauge Geometry
    const width = 200;
    const height = 130;
    const center = width / 2; // 100
    const centerY = 90;       // Moved up to allow space below
    const radius = 65;        // Slightly smaller radius to fit text
    const strokeWidth = 10;
    const labelRadius = 82;   // Distance for text labels
    
    // Needle Rotation: -90deg to 90deg
    const needleAngle = -90 + (gaugeValue * 180);

    // Helper to get coordinates on circle
    const getCoord = (angleInDegrees: number, r: number) => {
        // SVG uses 0 degrees at 3 o'clock, clockwise.
        const angleRad = (angleInDegrees * Math.PI) / 180;
        return {
        x: center + r * Math.cos(angleRad),
        y: centerY + r * Math.sin(angleRad)
        };
    };

    return (
        <div className="h-full bg-[#111218] rounded-xl border border-gray-800 p-6 flex flex-col justify-between relative">
            {/* Background Gradient (Clipped to prevent bleed) */}
            <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>
            </div>

            <div className="mb-2 relative z-10 flex justify-between items-start">
                <h3 className="text-gray-100 font-bold text-lg">Analyst Grades</h3>

                {/* Tooltip Trigger */}
                <div className="group relative">
                    <Info size={16} className="text-gray-500 hover:text-gray-300 cursor-help transition-colors" />
                    
                    {/* Tooltip Content */}
                    <div className="absolute right-0 top-6 w-52 bg-[#1f2937] border border-gray-700 rounded-lg shadow-xl p-3 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none group-hover:pointer-events-auto">
                        <div className="text-[10px] uppercase font-bold text-gray-500 mb-2 pb-1 border-b border-gray-700">Analyst Grade Actions (past 365d)</div>
                        <div className="space-y-1.5">
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-emerald-400 font-medium">Grade Upgrade</span>
                                <span className="text-sm font-mono font-bold text-emerald-400">{data.grade_upgrade_n}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-amber-400 font-medium">Grade Reiterate</span>
                                <span className="text-sm font-mono font-bold text-amber-400">{data.grade_reiterate_n}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-rose-400 font-medium">Grade Downgrade</span>
                                <span className="text-sm font-mono font-bold text-rose-400">{data.grade_downgrade_n}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-gray-400 font-medium">Grade Init</span>
                                <span className="text-sm font-mono font-bold text-gray-400">{data.grade_init_n}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Gauge Visualization */}
            <div className="relative flex justify-center items-center h-48 -mt-2">
                <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
                    <defs>
                        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#ef4444" />   {/* Red/Sell */}
                            <stop offset="50%" stopColor="#f59e0b" />  {/* Amber/Neutral */}
                            <stop offset="100%" stopColor="#10b981" /> {/* Emerald/Buy */}
                        </linearGradient>
                    </defs>
                    
                    {/* Background Track */}
                    <path 
                        d={`M ${center - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${center + radius} ${centerY}`} 
                        fill="none" 
                        stroke="#1f2937" 
                        strokeWidth={strokeWidth} 
                        strokeLinecap="round"
                    />

                    {/* Colored Arc */}
                    <path 
                        d={`M ${center - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${center + radius} ${centerY}`} 
                        fill="none" 
                        stroke="url(#gaugeGradient)" 
                        strokeWidth={strokeWidth} 
                        strokeLinecap="round"
                    />

                    {/* Labels around the arc (Outside/Above) */}
                    {/* We map angles manually for perfect placement */}
                    
                    {/* Strong Sell - Left */}
                    <text x={getCoord(190, labelRadius + 40).x} y={getCoord(190, labelRadius + 5).y} fill={finalRating === "Strong Sell" ? "#ef4444" : "#6b7280"} fontSize="8" fontWeight="600" textAnchor="start">Strong sell</text>
                    
                    {/* Sell - Top Left (~135 deg) */}
                    <text x={getCoord(225, labelRadius).x} y={getCoord(225, labelRadius).y} fill={finalRating === "Sell" ? "#ef4444" : "#6b7280"} fontSize="8" fontWeight="600" textAnchor="middle">Sell</text>
                    
                    {/* Neutral - Top (-90 deg / 270 deg) */}
                    <text x={center} y={centerY - labelRadius + 5} fill={finalRating === "Hold" ? "#f59e0b" : "#6b7280"} fontSize="8" fontWeight="600" textAnchor="middle">Hold</text>
                    
                    {/* Buy - Top Right (~45 deg / 315 deg) */}
                    <text x={getCoord(315, labelRadius).x} y={getCoord(315, labelRadius).y} fill={finalRating === "Buy" ? "#10b981" : "#6b7280"} fontSize="8" fontWeight="600" textAnchor="middle">Buy</text>
                    
                    {/* Strong Buy - Right */}
                    <text x={getCoord(350, labelRadius + 40).x} y={getCoord(350, labelRadius).y} fill={finalRating === "Strong Buy" ? "#10b981" : "#6b7280"} fontSize="8" fontWeight="600" textAnchor="end">Strong buy</text>

                    {/* Needle */}
                    <g transform={`translate(${center}, ${centerY}) rotate(${needleAngle})`}>
                        <line x1="0" y1="0" x2="0" y2={-radius + 8} stroke="#e5e7eb" strokeWidth="3" strokeLinecap="round" />
                        <circle cx="0" cy="0" r="4" fill="#e5e7eb" stroke="#111218" strokeWidth="2" />
                    </g>

                    {/* Buy Signal Text - Centered Below Needle */}
                    <text x={center} y={centerY + 25} textAnchor="middle" className="text-xl font-bold" fill={finalRatingColor}>
                        {finalRating}
                    </text>
                </svg>
            </div>

            {/* Legend / Stats */}
            <div className="flex justify-center gap-8 pt-0">
                <div className="flex flex-col items-center">
                    <span className="text-red-500 text-[10px] font-medium uppercase tracking-wider mb-0.5">Sell</span>
                    <span className="text-red-500 font-mono font-bold text-lg">{ratings.sell}</span>
                </div>
                <div className="flex flex-col items-center">
                    <span className="text-[#f59e0b] text-[10px] font-medium uppercase tracking-wider mb-0.5">Hold</span>
                    <span className="text-[#f59e0b] font-mono font-bold text-lg">{ratings.hold}</span>
                </div>
                <div className="flex flex-col items-center">
                    <span className="text-emerald-500 text-[10px] font-medium uppercase tracking-wider mb-0.5">Buy</span>
                    <span className="text-emerald-500 font-mono font-bold text-lg">{ratings.buy}</span>
                </div>
            </div>
        </div>
    );
};
