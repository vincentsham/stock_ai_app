'use client';

import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Catalyst } from '@/types';
import { CatalystCard } from './CatalystCard';
import { Zap, TrendingUp, TrendingDown, Info, Loader2, ChevronDown} from 'lucide-react';
import { searchCatalysts, countCatalysts} from "@/lib/db/catalystQueries";


export const CatalystSection: React.FC<{ tic: string }> = ( {tic} ) => {
    const [catalystsBull, setCatalystsBull] = useState<Catalyst[]>([]);
    const [catalystsBear, setCatalystsBear] = useState<Catalyst[]>([]);

    const pageBull = useRef(2);
    const pageBear = useRef(2);

    const [hasMore, setHasMore] = useState(true);
    const [hasMoreBull, setHasMoreBull] = useState(true);
    const [hasMoreBear, setHasMoreBear] = useState(true);

    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const loadingRef = useRef(false);
    const observerTarget = useRef<HTMLDivElement>(null);

    const [catalystCountBull, setCatalystCountBull] = useState<number | null>(null);
    const [catalystCountBear, setCatalystCountBear] = useState<number | null>(null);


    useEffect(() => {
        const fetchInitialData = async () => {
            const [initialCountBull, initialCountBear] = await Promise.all([
                countCatalysts(tic.trim().toUpperCase(), 1),
                countCatalysts(tic.trim().toUpperCase(), -1),
            ]);
            setCatalystCountBull(initialCountBull);
            setCatalystCountBear(initialCountBear);

            const [initialDataBull, initialDataBear] = await Promise.all([
                searchCatalysts(tic.trim().toUpperCase(), 1, 5, 1),
                searchCatalysts(tic.trim().toUpperCase(), 1, 5, -1),
            ]);
            setCatalystsBull(initialDataBull);
            setCatalystsBear(initialDataBear);
        };
        fetchInitialData();
    }, [tic]);

    const loadMore = useCallback(async (sentiment: Number) => {
        // const res = await fetch(`/api/catalysts?tic=${tic}&page=${page.current}&limit=10`);
        // const json = await res.json();
        // const newData = json.data;

        if (sentiment === 0 || sentiment === 1) {
            const newDataBull = await searchCatalysts(tic.trim().toUpperCase(), pageBull.current, 5, 1);
            setCatalystsBull(prev => {
                const next = [...prev, ...newDataBull];
                return next;
            });
            pageBull.current += 1;
        }

        if (sentiment === 0 || sentiment === -1) {
            const newDataBear = await searchCatalysts(tic.trim().toUpperCase(), pageBear.current, 5, -1);
            setCatalystsBear(prev => {
                const next = [...prev, ...newDataBear];
                return next;
            });
            pageBear.current += 1;
        }

        loadingRef.current = false;
    }, [tic, pageBull, pageBear]);

 

    useEffect(() => {
        if (catalystCountBull == null || catalystCountBear == null) return;

        const bullLoaded = catalystsBull.length;
        const bearLoaded = catalystsBear.length;

        const bullHasMore = bullLoaded < catalystCountBull;
        const bearHasMore = bearLoaded < catalystCountBear;

        setHasMoreBull(bullHasMore);
        setHasMoreBear(bearHasMore);
        setHasMore(bullHasMore || bearHasMore);
    }, [catalystsBull, catalystsBear, catalystCountBull, catalystCountBear]);


    const handleLoadMore = (sentiment: Number) => {
        loadingRef.current = true;
        setIsLoadingMore(true);
        // Simulate network query delay
        setTimeout(() => {
            loadMore(sentiment);
            setIsLoadingMore(false);
        }, 600);
    };



    return (
        <>
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Zap size={16}/>
                    Catalyst Events
                {/* <span className="text-xs font-normal text-gray-500 bg-gray-800/50 px-2 py-1 rounded-full border border-gray-700">
                    AI Generated
                </span> */}
                </h2>
                {/* <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Info size={12}/>
                    <span>Sorted by Impact & Recency</span>
                </div> */}
            </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
            {/* Vertical Divider for large screens */}
            <div className="hidden md:block absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-gray-800 via-gray-800 to-transparent -translate-x-1/2" />

            {/* BULL CASE COLUMN */}
            <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-2 border-b border-emerald-500/20 mb-2">
                <div className="p-1.5 bg-emerald-500/10 rounded-md">
                <TrendingUp size={18} className="text-emerald-400" />
                </div>
                <div>
                <h3 className="text-lg font-bold text-emerald-400 tracking-tight">The Bull Case</h3>
                <p className="text-xs text-emerald-500/60 font-medium">Positive Drivers & Growth</p>
                </div>
                <div className="ml-auto text-xs font-mono text-emerald-500/50">
                {catalystsBull.length} ITEMS
                </div>
            </div>

            <div className="space-y-4">
                {catalystsBull.map((catalyst) => (
                <CatalystCard 
                    key={catalyst.catalyst_id} 
                    catalyst={catalyst} 
                />
                ))}
                {catalystsBull.length === 0 && (
                <div className="text-center py-10 text-gray-600 italic border border-dashed border-gray-800 rounded-lg">
                    No bullish catalysts detected recently.
                </div>
                )}
            </div>
            {/* Load More Button */}
            <div className="flex sm:hidden w-full py-8 flex items-center justify-center">
                {hasMoreBull ? (
                    <button
                        onClick={() => handleLoadMore(1)}
                        disabled={isLoadingMore}
                        className="group flex items-center gap-2 px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm font-medium rounded-lg transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none hover:shadow-lg hover:shadow-blue-500/10 border border-gray-700 hover:border-gray-600"
                    >
                        {isLoadingMore ? (
                            <>
                                <Loader2 className="animate-spin" size={16} />
                                Loading...
                            </>
                        ) : (
                            <>
                                Load More Bull Catalysts
                                <ChevronDown size={16} className="transition-transform group-hover:translate-y-0.5" />
                            </>
                        )}
                    </button>
                ) : (
                    (catalystsBull.length > 0 || catalystsBear.length > 0) && (
                        <span className="text-xs text-gray-700 uppercase tracking-widest font-semibold">End of Bull Analysis</span>
                    )
                )}
            </div>
            </div>

            {/* BEAR CASE COLUMN */}
            <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 pb-2 border-b border-rose-500/20 mb-2">
                <div className="p-1.5 bg-rose-500/10 rounded-md">
                <TrendingDown size={18} className="text-rose-400" />
                </div>
                <div>
                <h3 className="text-lg font-bold text-rose-400 tracking-tight">The Bear Case</h3>
                <p className="text-xs text-rose-500/60 font-medium">Risk Factors & Headwinds</p>
                </div>
                <div className="ml-auto text-xs font-mono text-rose-500/50">
                {catalystsBear.length} ITEMS
                </div>
            </div>

            <div className="space-y-4">
                {catalystsBear.map((catalyst) => (
                <CatalystCard 
                    key={catalyst.catalyst_id} 
                    catalyst={catalyst} 
                />
                ))}
                {catalystsBear.length === 0 && (
                <div className="text-center py-10 text-gray-600 italic border border-dashed border-gray-800 rounded-lg">
                    No bearish catalysts detected recently.
                </div>
                )}
            </div>
            {/* Load More Button */}
            <div className="flex sm:hidden w-full py-8 flex items-center justify-center">
                {hasMoreBear ? (
                    <button
                        onClick={() => handleLoadMore(-1)}
                        disabled={isLoadingMore}
                        className="group flex items-center gap-2 px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm font-medium rounded-lg transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none hover:shadow-lg hover:shadow-blue-500/10 border border-gray-700 hover:border-gray-600"
                    >
                        {isLoadingMore ? (
                            <>
                                <Loader2 className="animate-spin" size={16} />
                                Loading...
                            </>
                        ) : (
                            <>
                                Load More Bear Catalysts
                                <ChevronDown size={16} className="transition-transform group-hover:translate-y-0.5" />
                            </>
                        )}
                    </button>
                ) : (
                    (catalystsBull.length > 0 || catalystsBear.length > 0) && (
                        <span className="text-xs text-gray-700 uppercase tracking-widest font-semibold">End of Bear Analysis</span>
                    )
                )}
            </div>
            </div>
        </div>

        {/* Load More Button */}
            <div className="hidden sm:flex w-full py-8 flex items-center justify-center">
                {hasMore ? (
                    <button
                        onClick={() => handleLoadMore(0)}
                        disabled={isLoadingMore}
                        className="group flex items-center gap-2 px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm font-medium rounded-lg transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none hover:shadow-lg hover:shadow-blue-500/10 border border-gray-700 hover:border-gray-600"
                    >
                        {isLoadingMore ? (
                            <>
                                <Loader2 className="animate-spin" size={16} />
                                Loading...
                            </>
                        ) : (
                            <>
                                Load More Catalysts
                                <ChevronDown size={16} className="transition-transform group-hover:translate-y-0.5" />
                            </>
                        )}
                    </button>
                ) : (
                    (catalystsBull.length > 0 || catalystsBear.length > 0) && (
                        <span className="text-xs text-gray-700 uppercase tracking-widest font-semibold">End of Analysis</span>
                    )
                )}
            </div>
        </>
    );
};