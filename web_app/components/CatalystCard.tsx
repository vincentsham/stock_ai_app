'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Zap, TrendingUp, TrendingDown, ExternalLink} from 'lucide-react';
import { Catalyst, CatalystSentiment, ImpactMagnitude } from '@/types';

interface CatalystCardProps {
  catalyst: Catalyst;
}

const ensureDoubleQuotes = (str: string) => {
  str = str.trim();

  // If wrapped in single quotes → convert to double quotes
  if (str.startsWith("'") && str.endsWith("'")) {
    str = `"${str.slice(1, -1)}"`;
  } else if (str.startsWith('"') && str.endsWith('"')) {
    // If already wrapped in double quotes → return as-is
    // do nothing
  } else {
    // Otherwise wrap in double quotes
    str = `"${str}"`;
  }
  return str.replace(/'+/g, "'").replace(/"+/g, '"');
}

// Truncate a string to a max number of words, appending '...' if truncated
const truncateWords = (str: string, maxWords: number) => {
  const words = str.split(/\s+/);
  if (words.length > maxWords) {
    return words.slice(0, maxWords).join(' ') + '...';
  }
  return str;
};


export const CatalystCard: React.FC<CatalystCardProps> = ({ catalyst }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const isBullish = catalyst.sentiment === CatalystSentiment.Bullish;
  const isHighImpact = catalyst.impact_magnitude === ImpactMagnitude.Major;

  // Formatting date
  const dateObj = new Date(catalyst.date);
  const formattedDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  // Styles based on sentiment
  const borderColor = isBullish 
    ? 'border-emerald-500/20 hover:border-emerald-500/40' 
    : 'border-rose-500/20 hover:border-rose-500/40';
  
  const bgColor = isBullish 
    ? 'bg-emerald-500/5' 
    : 'bg-rose-500/5';
    
  const accentColor = isBullish ? 'text-emerald-400' : 'text-rose-400';
  const badgeBg = isBullish ? 'bg-emerald-500/10 text-emerald-300' : 'bg-rose-500/10 text-rose-300';
  
  // High Impact Glow Effect
  const glowClass = isHighImpact 
    ? isBullish ? 'shadow-[0_0_15px_-3px_rgba(16,185,129,0.15)]' : 'shadow-[0_0_15px_-3px_rgba(244,63,94,0.15)]'
    : '';

  const evidenceList = Array.isArray(catalyst.evidences)
    ? catalyst.evidences.slice(0, 5)
    : [];

  const sourceTypeList = Array.isArray(catalyst.source_types)
    ? catalyst.source_types.slice(0, 5)
    : [];

  const urlList = Array.isArray(catalyst.urls)
    ? catalyst.urls.slice(0, 5)
    : [];

  return (
    <div 
      className={`relative w-full rounded-lg border ${borderColor} ${bgColor} ${glowClass} p-4 transition-all duration-300 ease-in-out animate-slide-up-fade`}
      >
      {/* High Impact Badge */}
      {isHighImpact && (
        <div className="absolute -top-3 right-4">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border ${isBullish ? 'border-emerald-500/30 bg-emerald-950 text-emerald-400' : 'border-rose-500/30 bg-rose-950 text-rose-400'} shadow-sm`}>
            <Zap size={10} className="fill-current" />
            HIGH IMPACT
          </span>
        </div>
      )}

      <div className="flex flex-col gap-3">
        {/* Header: Date and Type */}
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span className="font-mono">{formattedDate}</span>
          <span className={`px-2 py-0.5 rounded uppercase tracking-wider text-[10px] font-semibold ${badgeBg}`}>
            {catalyst.catalyst_type.replace('_', ' ')}
          </span>
        </div>

        {/* Title */}
        <div className="flex gap-3">
          <div className={`mt-1 shrink-0 ${accentColor}`}>
            {isBullish ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
          </div>
          <div>
            <h3 className={`font-semibold text-base leading-tight ${isHighImpact ? 'text-gray-100' : 'text-gray-200'}`}>
              {catalyst.title}
            </h3>
          </div>
        </div>

        {/* Summary */}
        <p className="text-sm text-gray-400 leading-relaxed">
          {catalyst.summary}
        </p>

        {/* Evidence Toggle */}
        <div className="pt-2 border-t border-gray-800/50">
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors w-full cursor-pointer"
          >
            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {isExpanded ? 'Hide Evidence' : 'View Evidence'}
          </button>
          
          {isExpanded && (
            <div className="mt-2 bg-black/20 p-2 rounded border border-gray-800">
              {evidenceList.length > 0 ? (
                <ul className="list-disc space-y-1 pl-4">
                {evidenceList.map((item, index) => {
                    const url = urlList[index];
                    const sourceType = sourceTypeList[index];

                    return (
                    <li
                        key={`catalyst-${catalyst.catalyst_id}-evidence-${index}`}
                        className="mb-2 last:mb-0 text-xs text-gray-400"
                        >
                        <span className="italic">{ensureDoubleQuotes(truncateWords(item, 50))}</span>
                        {<a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-2 inline-flex items-center gap-1 text-[11px] text-sky-400 hover:text-sky-300"
                            >
                            <ExternalLink size={12} />
                            <span>{sourceType || 'Reference'}</span>
                        </a>}
                    </li>
                    );
                })}
                </ul>
              ) : (
                <p className="text-xs text-gray-400 italic">
                  No evidence provided.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};