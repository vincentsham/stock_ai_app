'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { MetricItem } from './MetricItem';
import { MetricList } from '@/types';



const getColorTheme = (percentile: number | null, inverse: boolean | null): string | null=> {
  if (percentile === null) {
      return null;
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




export const MetricCard: React.FC<MetricList> = ({ category, score, metrics, defaultVisibleCount}) => {
  const [showAll, setShowAll] = useState(false);

  // Determine visible items based on expansion state and defaultVisibleCount
  const visibleItems = (defaultVisibleCount && !showAll) 
    ? metrics.slice(0, defaultVisibleCount) 
    : metrics;

  const hasHiddenItems = defaultVisibleCount !== undefined && metrics.length > defaultVisibleCount;
  const scoreColorTheme = score !== null ? getColorTheme(score, false) : null;

  const scoreBadgeClassNameByColor: Record<string, string> = {
    green: 'border-emerald-500/30 bg-emerald-950 text-emerald-400',
    yellow: 'border-amber-500/30 bg-amber-950 text-amber-400',
    red: 'border-rose-500/30 bg-rose-950 text-rose-400',
    gray: 'border-gray-700 bg-gray-800/50 text-gray-300',
  };
  const scoreBadgeClassName = scoreColorTheme ? (scoreBadgeClassNameByColor[scoreColorTheme] ?? scoreBadgeClassNameByColor.gray) : scoreBadgeClassNameByColor.gray;

  return (
    <div 
      className="bg-[#111218] border border-gray-800 rounded-xl overflow-hidden transition-all duration-300 hover:border-gray-700 flex flex-col h-fit"
    >
      <div className="px-4 pt-4 pb-3 border-b border-gray-700/70 bg-gray-700">
        <h3 className="text-white font-bold text-lg leading-none flex items-center justify-between gap-3">
          <span className="min-w-0 truncate">{category.toUpperCase()}</span>
          {score !== null && (
            <span className={`px-2 py-1 text-xs font-bold rounded-full whitespace-nowrap border shadow-sm ${scoreBadgeClassName}`}>
              SCORE: {Number(score).toFixed(0)}
            </span>
          )}
        </h3>
      </div>

      <div className="p-4 space-y-2 bg-[#111218] animate-in fade-in slide-in-from-top-1 duration-200 flex-1 flex flex-col">
        {visibleItems.map((item, index) => (
          <MetricItem
            key={`${item.label}-${index}`}
            name={item.name}
            value={item.value}
            percentile={item.percentile}
            colorTheme={getColorTheme(item.percentile, item.inverse)}
          />
        ))}

        {hasHiddenItems && (
            <button 
              onClick={(e) => {
                  e.stopPropagation();
                  setShowAll((prev) => !prev);
              }}
              className="w-full py-2 text-xs font-medium text-gray-500 hover:text-white transition-colors flex items-center justify-center gap-1 hover:bg-gray-800/30 rounded-lg mt-1"
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