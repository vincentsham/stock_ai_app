"use client";

import { StockProfile, StockScores } from '@/types';
import { X, Loader2 } from 'lucide-react';
import { fetchStockLogo } from '@/lib/actions/finnhub.actions';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { StockLivePrice } from './StockLivePrice';

// 1. Update Interface: stockProfile is OPTIONAL (?)
interface StockProfileCardProps {
    tic: string;
    stockProfile: StockProfile; 
    stockScores?: StockScores;
    onRemove?: (tic: string) => void;
}

export const StockProfileCard: React.FC<StockProfileCardProps> = ({ tic, stockProfile, stockScores, onRemove }) => {
    
    // Safety: Use Optional Chaining (?.) for initial state
    const [logoUrl, setLogoUrl] = useState<string | null>(stockProfile?.logo || null);
    const router = useRouter();

    useEffect(() => {
        // 2. CRITICAL FIX: Stop execution if profile is missing
        if (!stockProfile) return;

        let isMounted = true;
        setLogoUrl(null);

        const loadLogo = async () => {
            // Safe to access properties now because of the check above
            if (stockProfile.logo) {
                setLogoUrl(stockProfile.logo);
                return;
            }

            try {
                // Use tic prop or stockProfile.tic (both are safe now)
                const fetchedUrl = await fetchStockLogo(stockProfile.tic);

                if (fetchedUrl) {
                    const img = new Image();
                    img.src = fetchedUrl;
                    img.onload = () => {
                        if (isMounted) {
                            setLogoUrl(fetchedUrl);
                        }
                    };
                }
            } catch (err) {
                console.error("Failed to load logo", err);
            }
        };

        loadLogo();

        return () => { isMounted = false; };
        
    // 3. Add stockProfile to dependencies so it re-runs when data arrives
    }, [tic, stockProfile]); 

    return (
            <div className={`relative h-32 bg-gray-600 text-white overflow-hidden shrink-0`}>
                <div className="relative z-10 h-full p-3 flex flex-col justify-between">
                    <div className="flex justify-between items-start">
                        <div className="rounded-lg shadow-lg shrink-0 w-7 h-7 md:w-11 md:h-11 flex items-center justify-center overflow-hidden">
                            {logoUrl ? (
                                <img 
                                    src={logoUrl} 
                                    alt={tic} 
                                    className="w-full h-full object-contain animate-in fade-in duration-300" 
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-gray-700 text-[10px] font-bold">
                                    {tic.substring(0,4)}
                                </div>
                            )}
                        </div>
                        { onRemove && (
                            <button 
                                onClick={() => onRemove(tic)}
                                className="flex items-center gap-1 text-[8px] font-extrabold text-gray-300 bg-black/20 px-2 py-0.5 rounded-full hover:scale-[1.05] transition-transform cursor-pointer"
                            >
                                Remove <X size={8} strokeWidth={3} />
                            </button>
                        )}

                    </div>

                    <div className="flex justify-between items-end text-gray-300">
                        <div
                            className="flex flex-col overflow-hidden pr-2 hover:text-white hover:scale-[1.05] transition-transform cursor-pointer"
                            onClick={() => router.push(`/stocks/${stockProfile.tic}`)}
                            title={`Go to ${stockProfile.tic} details`}
                        >
                            <h3 className="font-bold text-lg leading-none tracking-tighter mb-1">
                                {stockProfile.tic}
                            </h3>
                            <p className="text-[8px] font-bold tracking-tight truncate opacity-90 uppercase">
                                {stockProfile.name}
                            </p>
                            <StockLivePrice tic={stockProfile.tic} />    
                        </div>
                        <div className="flex flex-col items-center shrink-0">
                            {
                                stockScores?.total_score !== undefined ? (
                                    <>
                                        <span className="text-3xl font-black leading-none tracking-tighter">{Math.round(Number(stockScores.total_score))}</span>
                                        <span className="text-[8px] font-black tracking-[0.2em] opacity-80 uppercase">Score</span>
                                    </>
                                ) : null
                            }
                        </div>
                    </div>
                </div>
            </div>
    );
};
