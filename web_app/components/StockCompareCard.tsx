import { AllMetrics, StockProfile, StockScores } from '@/types';
import { X, Loader2 } from 'lucide-react';
import { fetchStockLogo } from '@/lib/actions/finnhub.actions';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { StockProfileCard } from './StockProfileCard';
import { StockLoadingCard } from './StockLoadingCard';
import { MetricCard } from './MetricCard';
 
// 1. Update Interface: stockProfile is OPTIONAL (?)
interface StockCompareCardProps {
    tic: string;
    stockProfile?: StockProfile; 
    stockScores?: StockScores;
    stockMetrics?: AllMetrics;
    showMetrics?: boolean;
    onRemove: (tic: string) => void;
    expandedStates: boolean[];
    toggleMetric: (index: number) => void;
    isLoading?: boolean;
}

export const StockCompareCard: React.FC<StockCompareCardProps> = ({ tic, stockProfile, stockScores, stockMetrics, showMetrics = true, onRemove, expandedStates, toggleMetric, isLoading }) => {
    
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

    // -----------------------------------------------------------------
    // SKELETON UI (Runs if loading OR profile is undefined)
    // -----------------------------------------------------------------
    if (isLoading || !stockProfile) {
        return (
            <StockLoadingCard tic={tic} onRemove={onRemove} />
        );
    }

    // -----------------------------------------------------------------
    // REAL UI (Only runs when stockProfile is guaranteed to exist)
    // -----------------------------------------------------------------
    return (
        <div className="w-[200px] bg-[#111218] rounded-xl border border-gray-800 shadow-sm flex-shrink-0 flex flex-col overflow-hidden transition-all">
            <StockProfileCard 
                tic={tic} 
                stockProfile={stockProfile} 
                stockScores={stockScores} 
                onRemove={onRemove} 
            />
            <div className="bg-gray-700">
            {
                showMetrics && stockMetrics && Object.values(stockMetrics).map((item, index) => (
                    item ? (
                        <MetricCard
                            key={`${tic}-${item.category}`}
                            category={item.category}
                            tic={item.tic}
                            score={item.score}
                            metrics={item.metrics}
                            defaultVisibleCount={item.defaultVisibleCount}
                            highlight={item.highlight ?? null}
                            expandedState={(expandedStates && typeof expandedStates[index] === 'boolean') ? [expandedStates[index], () => toggleMetric(index)] : null}
                            compact={true}
                        />
                    ) : null
                ))
            }
            </div>

        </div>
    );
};
