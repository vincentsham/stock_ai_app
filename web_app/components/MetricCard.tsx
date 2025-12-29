'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { MetricItem } from './MetricItem';
import { MetricList } from '@/types';




const getColorTheme = (percentile: number | null, inverse: boolean | null, highlight?: boolean | null): string | null=> {
  if (percentile === null) {
      return null;
  }
  if (typeof(highlight) === 'boolean') {
      if (highlight === true) {
          return 'green';
      } else {
          return 'gray';
      }
  }
  if (inverse === null) {
      return 'gray';
  }
  if (inverse === true) {
      if (percentile >= 100 * 2/3) return 'red';
      if (percentile >= 100 * 1/3) return 'yellow';
      return 'green';
  }
  if (inverse === false) {
      if (percentile >= 100 * 2/3) return 'green';
      if (percentile >= 100 * 1/3) return 'yellow';
      return 'red';
  }
  return 'gray'; 
}



interface MetricCardProps extends MetricList {
  expandedState?: [boolean, () => void] | null;
  compact?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
    category, score, metrics, defaultVisibleCount, 
    highlight = null, expandedState = null, 
    compact = false }) => {
      // 1. Setup internal state (fallback) 
      const [internalShowAll, setInternalShowAll] = useState(false);

      const toggleInternal = () => setInternalShowAll(prev => !prev);

      // 2. Determine the active state in one line
      // Logic: If expandedState exists, use it. If not (??), use the internal state.
      const [showAll, toggleShowAll] = expandedState ?? [internalShowAll, toggleInternal];


      // Determine visible items based on expansion state and defaultVisibleCount
      const visibleItems = (defaultVisibleCount && !showAll) 
        ? metrics.slice(0, defaultVisibleCount) 
        : metrics;

      const hasHiddenItems = defaultVisibleCount !== undefined && metrics.length > defaultVisibleCount;
      const scoreColorTheme = score !== null ? getColorTheme(score, false, highlight) : null;

      const scoreBadgeClassNameByColor: Record<string, string> = {
        green: 'border-emerald-500/30 bg-emerald-950 text-emerald-400',
        yellow: 'border-amber-500/30 bg-amber-950 text-amber-400',
        red: 'border-rose-500/30 bg-rose-950 text-rose-400',
        gray: 'border-gray-700 bg-gray-800/50 text-gray-300',
      };
      const scoreBadgeClassName = scoreColorTheme ? (scoreBadgeClassNameByColor[scoreColorTheme] ?? scoreBadgeClassNameByColor.gray) : scoreBadgeClassNameByColor.gray;
      if (compact) {
      return (
          <div 
            className="bg-[#111218] rounded-xl overflow-hidden transition-all duration-300 flex flex-col h-fit"
          >
            <div className="px-2 pt-1 pb-1 mb-2 bg-gray-700">
              <h3 className="text-white font-bold text-xs leading-none flex items-center justify-between gap-3">
                <span className="min-w-0 truncate">{category}</span>
                {score !== null && (
                  <span className={`px-2 py-1 text-[8px] font-bold rounded-full whitespace-nowrap border shadow-sm ${scoreBadgeClassName}`}>
                    SCORE: {Number(score).toFixed(0)}
                  </span>
                )}
              </h3>
            </div>

            <div className="bg-[#111218] animate-in fade-in slide-in-from-top-1 duration-200 flex-1 flex flex-col">
              {visibleItems.map((item, index) => (
                <MetricItem
                  key={`${item.label}-${index}`}
                  name={item.name}
                  value={item.value}
                  percentile={item.percentile}
                  colorTheme={getColorTheme(item.percentile, item.inverse, item.highlight)}
                  highlight={item.highlight ?? null}
                  compact={compact}
                />
              ))}

              {hasHiddenItems && (
                  <button 
                      onClick={toggleShowAll}
                      className="w-full py-1 text-[8px] font-bold text-gray-500 hover:text-white transition-colors flex items-center justify-center gap-1 hover:bg-gray-700  rounded-b-lg mt-1 uppercase tracking-widest cursor-pointer"
                    >
                      {showAll ? (
                          <>
                              Less <ChevronUp size={12} />
                          </>
                      ) : (
                          <>
                              More <ChevronDown size={12} />
                          </>
                      )}
                  </button> 
                  
              )}
            </div>
            
          </div>
      );
    };
    return (
          <div 
            className="bg-[#111218]  rounded-xl overflow-hidden transition-all duration-300 flex flex-col h-fit"
          >
            <div className="px-4 pt-4 pb-3 mb-2 bg-gray-700">
              <h3 className="text-white font-bold text-lg leading-none flex items-center justify-between gap-3">
                <span className="min-w-0 truncate">{category}</span>
                {score !== null && (
                  <span className={`px-2 py-1 text-xs font-bold rounded-full whitespace-nowrap border shadow-sm ${scoreBadgeClassName}`}>
                    SCORE: {Number(score).toFixed(0)}
                  </span>
                )}
              </h3>
            </div>

            <div className="bg-[#111218] animate-in fade-in slide-in-from-top-1 duration-200 flex-1 flex flex-col">
              {visibleItems.map((item, index) => (
                <MetricItem
                  key={`${item.label}-${index}`}
                  name={item.name}
                  value={item.value}
                  percentile={item.percentile}
                  colorTheme={getColorTheme(item.percentile, item.inverse, item.highlight)}
                  highlight={item.highlight ?? null}
                  compact={compact}
                />
              ))}

              {hasHiddenItems && (
                  <button 
                      onClick={toggleShowAll}
                      className="w-full py-2 text-xs font-bold text-gray-500 hover:text-white transition-colors flex items-center justify-center gap-1 hover:bg-gray-700 rounded-b-lg mt-1 uppercase tracking-widest cursor-pointer"
                    >
                      {showAll ? (
                          <>
                              Show Less <ChevronUp size={12} />
                          </>
                      ) : (
                          <>
                              Show {metrics.length - defaultVisibleCount} More <ChevronDown size={12} />
                          </>
                      )}
                  </button> 
                  
              )}
            </div>
            
          </div>
      );
};