import { TrendingUp, Users } from 'lucide-react';
import { searchStock } from '@/lib/db/stockQueries';
import { searchStockScores, searchTopStocks } from '@/lib/db/metricsQueries';
import { POPULAR_STOCKS } from '@/lib/constants';
import { StockProfileCard } from '@/components/StockProfileCard';
import { StockProfile } from '@/types';
import { StockScores } from '@/types/metrics';
import Link from 'next/link';
import { Wallpaper } from '@/components/Wallpaper';
import { MAX_DISPLAY_STOCKS, NUM_STOCKS } from '@/lib/constants';

export const dynamic = 'force-dynamic';

// Helper function to fetch details for a list of tickers
async function getStockDetails(tickers: string[]) {
  const results = await Promise.all(
    tickers.map(async (tic) => {
      try {
        // Run both queries in parallel for efficiency
        const [profile, scores] = await Promise.all([
          searchStock(tic),
          searchStockScores(tic)
        ]);

        if (profile && scores) {
          return { tic, profile, scores };
        }
      } catch (e) {
        console.error(`Failed to load ${tic}`, e);
      }
      return null;
    })
  );

  // Filter out any failed requests (nulls)
  return results.filter((item): item is { tic: string, profile: StockProfile, scores: StockScores } => item !== null);
}

export default async function Home() {
    // 1. Fetch Top Tickers
    const topTics = await searchTopStocks(MAX_DISPLAY_STOCKS);
    
    // 2. Fetch full data for both categories in parallel
    const [topStocksData, popularStocksData] = await Promise.all([
        getStockDetails(topTics),
        getStockDetails(POPULAR_STOCKS)
    ]);

    return (
        <div className="relative flex flex-col items-center justify-center w-full min-h-screen overflow-hidden"> 
            
            {/* 1. The Background Wallpaper */}
            <Wallpaper />

            {/* 2. Main Content - Wrapped in z-10 to sit on top of the background */}
            <div className="relative z-10 flex flex-col items-center w-full pt-20 pb-20">
                <h1 className="text-5xl font-extrabold mb-10 text-center text-transparent bg-clip-text bg-gradient-to-b from-gray-100 to-gray-500 tracking-tight">
                    Unlock AI Stock Analysis
                </h1>
                
                <div className="text-base leading-relaxed text-center max-w-2xl text-gray-400 mb-32 px-4">
                    <strong>Over {NUM_STOCKS}+ stock analysis reports</strong> are powered by a 
                    <strong className="text-yellow-300"> Multi-AI Agent System</strong>, delivering collaborative and precise insights to give you an unparalleled edge in the markets.
                </div>

                {/* Stock Selection Section */}
                <div className="w-full max-w-5xl space-y-12 px-4">
                    
                    {/* Top Performing Category */}
                    <div className="space-y-6">
                        <div className="flex items-center justify-center space-x-3 px-2">
                            <TrendingUp className="text-yellow-400" size={24} />
                            <h2 className="text-2xl font-bold text-gray-300">Top Stocks</h2>
                        </div>
                        <div className="flex flex-wrap justify-center gap-4">
                            {topStocksData.map(({ tic, profile, scores }) => (
                                <Link 
                                    key={tic} 
                                    href={`/stocks/${tic}`} 
                                    className="w-[200px] bg-[#111218] rounded-xl border border-gray-800 shadow-sm flex-shrink-0 flex flex-col overflow-hidden transition-all hover:scale-[1.02] hover:shadow-lg hover:border-gray-500"
                                >
                                    <StockProfileCard 
                                        tic={tic} 
                                        stockProfile={profile} 
                                        stockScores={scores} 
                                    />
                                </Link>
                            ))}
                        </div>
                    </div>

                    {/* Popular Category */}
                    <div className="space-y-6">
                        <div className="flex items-center justify-center space-x-3 px-2">
                            <Users className="text-blue-400" size={24} />
                            <h2 className="text-2xl font-bold text-gray-300">Most Popular</h2>
                        </div>
                        <div className="flex flex-wrap justify-center gap-4">
                            {popularStocksData.map(({ tic, profile, scores }) => (
                                <Link 
                                    key={tic} 
                                    href={`/stocks/${tic}`} 
                                    className="w-[200px] bg-[#111218] rounded-xl border border-gray-800 shadow-sm flex-shrink-0 flex flex-col overflow-hidden transition-all hover:scale-[1.02] hover:shadow-lg hover:border-gray-500"
                                >
                                    <StockProfileCard 
                                        tic={tic} 
                                        stockProfile={profile} 
                                        stockScores={scores} 
                                    />
                                </Link>
                            ))}
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}