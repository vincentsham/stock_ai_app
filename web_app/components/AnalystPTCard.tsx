'use client';


import { AnalystAnalysis } from '@/types';
import { Info } from 'lucide-react';

export const AnalystPTCard: React.FC<{ data: AnalystAnalysis }> = ({ data }) => {
    return (
        <div className="h-full bg-[#111218] rounded-xl border border-gray-800 p-5 flex flex-col relative">
            {/* Background Gradient (Clipped to prevent bleed) */}
            <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
                <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-500/5 rounded-full blur-3xl"></div>
            </div>

            <div className="mb-2 relative z-10 flex justify-between items-start">
                <div>
                    <h3 className="text-gray-100 font-bold text-lg">Analyst Price Targets</h3>
                    <p className="text-xs text-gray-500">(12-month price forecasts)</p>
                </div>

                {/* Tooltip Trigger */}
                <div className="group relative">
                    <Info size={16} className="text-gray-500 hover:text-gray-300 cursor-help transition-colors" />
                    
                    {/* Tooltip Content */}
                    <div className="absolute right-0 top-6 w-48 bg-[#1f2937] border border-gray-700 rounded-lg shadow-xl p-3 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none group-hover:pointer-events-auto">
                        <div className="text-[10px] uppercase font-bold text-gray-500 mb-2 pb-1 border-b border-gray-700"><div>Analyst PT Actions</div> <div>(past 365d)</div></div>
                        <div className="space-y-1.5">
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-emerald-400 font-medium">PT Raise</span>
                                <span className="text-sm font-mono font-bold text-emerald-400">{data.pt_upgrade_n}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-amber-400 font-medium">PT Maintain</span>
                                <span className="text-sm font-mono font-bold text-amber-400">{data.pt_reiterate_n}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-rose-400 font-medium">PT Cut</span>
                                <span className="text-sm font-mono font-bold text-rose-400">{data.pt_downgrade_n}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-gray-400 font-medium">PT Init</span>
                                <span className="text-sm font-mono font-bold text-gray-400">{data.pt_init_n}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex flex-col justify-center flex-1 gap-4 relative z-10">
                
                {/* Median Highlight */}
                <div className="flex flex-col items-center justify-center -mt-2">
                    <span className="text-yellow-500 text-m font-bold uppercase tracking-widest mb-1">Median</span>
                    <span className="text-yellow-500 text-4xl font-bold tracking-tight">${data.pt_median}</span>
                </div>

                <div className="space-y-4">
                    {/* Price Stats Grid */}
                    <div className="grid grid-cols-4 text-center max-w-sm mx-auto w-full">
                        <div className="flex flex-col gap-0.5">
                            <span className="text-red-500 text-[10px] font-bold uppercase">Low</span>
                            <span className="text-red-500 text-lg font-mono font-semibold">${data.pt_low}</span>
                        </div>
                        <div className="flex flex-col gap-0.5">
                            <span className="text-[#6366f1ff] text-[10px] font-bold uppercase">25th %</span>
                            <span className="text-[#6366f1ff] text-lg font-mono font-semibold">${data.pt_p25}</span>
                        </div>
                        <div className="flex flex-col gap-0.5">
                            <span className="text-[#6366f1ff] text-[10px] font-bold uppercase">75th %</span>
                            <span className="text-[#6366f1ff] text-lg font-mono font-semibold">${data.pt_p75}</span>
                        </div>
                        <div className="flex flex-col gap-0.5">
                            <span className="text-emerald-500 text-[10px] font-bold uppercase">High</span>
                            <span className="text-emerald-500 text-lg font-mono font-semibold">${data.pt_high}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};