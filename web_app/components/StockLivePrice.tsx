'use client';

import { useStockLivePrice } from '@/hooks/useYahooFinance';

interface StockLivePriceProps {
  tic: string;
}

export const StockLivePrice: React.FC<StockLivePriceProps> = ({ tic }) => {
    const { data, isLoading, error } = useStockLivePrice(tic, null);

    if (error) {
        return (
            <div className="w-full">
                <div className="text-xs font-medium font-mono text-gray-500">
                    Not available
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="w-full">
                <div className="text-xs font-medium font-mono text-gray-500 animate-pulse">
                    Loading...
                </div>
            </div>
        );
    }

    const isPositive = (data.changePercent ?? 0) >= 0;
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';

    return (
        <div className="w-full">
            <div className="text-sm font-medium font-mono text-gray-300">
                ${data.price?.toFixed(2)}
                <span className={`text-[10px] font-small ml-1 mt-1 ${colorClass}`}>
                    {isPositive ? '▲' : '▼'}{Math.abs(data.changePercent ?? 0).toFixed(2)}%
                </span>
            </div>
        </div>
    );
}