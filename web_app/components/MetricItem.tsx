'use client';

import React from 'react';
import { Star } from "lucide-react";


interface MetricRowProps {
  name: string;
  value: string;
  percentile: number | null;
  colorTheme: string | null;
  highlight?: boolean | null;
  compact?: boolean;
}

export const MetricItem: React.FC<MetricRowProps> = ({ name, value, percentile, colorTheme, highlight=null, compact=false }) => {
  // Determine text and background color based on the provided theme
  const getThemeClasses = (theme: string | null) => {
    switch (theme) {
      case 'yellow':
        return { text: 'text-yellow-400', bg: 'bg-yellow-400' };
      case 'red':
        return { text: 'text-red-500', bg: 'bg-red-500' };
      case 'gray':
        return { text: 'text-gray-400', bg: 'bg-gray-400' };
      case 'green':
        return { text: 'text-emerald-500', bg: 'bg-emerald-500' };
      default:
        return { text: '', bg: '' };
    }
  };
  

  const { text: textColor, bg: bgColor } = getThemeClasses(colorTheme);
  const displayedPercentile = percentile !== null ? Math.round(percentile) : null;
  if (compact) {
    return (
      <div className="flex flex-col px-2 py-0.5 border-b border-gray-800/50 last:border-0 group text-gray-500 hover:bg-gray-700 hover:text-white transition-colors">
        {/* Top Row: Label and Value */}
        <div className="flex justify-between items-center w-full mb-0">
          {/* 1. Added 'truncate' (single line + ...) 
              2. Added 'flex-1 min-w-0' (allows it to shrink and take available space)
              3. Added 'mr-2' (prevents text from hitting the star/value directly) */}
          <span className="text-[10px] font-medium truncate flex-1 min-w-0 mr-2">
            {name}
          </span>

          {/* Added 'shrink-0' so the value/star never gets squished */}
          <span className="shrink-0 inline-flex items-center gap-1 whitespace-nowrap text-[10px] font-bold tracking-wide text-white">
              {highlight ? <Star className="h-[10px] w-[10px]" fill="white" strokeWidth={0} /> : null} {value}
          </span>
        </div>

        {/* Bottom Row: Progress Bar */}
        <div className="w-full relative mt-0">
          <div className="h-4 flex items-center relative w-full">
            {/* Background Track */}
            <div className="absolute w-full h-[3px] bg-gray-700/50 rounded-full"></div>
            
            {/* Active Bar with Discrete Color - Hidden if percentile is null */}
            {percentile !== null && (
              <div 
                  className={`absolute h-[5px] rounded-full shadow-[0_0_12px_rgba(255,255,255,0.15)] transition-all duration-1000 ease-out ${bgColor}`}
                  style={{ 
                  width: `${percentile}%`
                  }}
              >
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="flex flex-col px-4 py-1.5 border-b border-gray-800/50 last:border-0 group text-gray-500 hover:bg-gray-700 hover:text-white transition-colors">
      {/* Top Row: Label and Value */}
      <div className="flex justify-between items-center w-full mb-2">
        <span className="text-sm md:text-base font-medium">{name}</span>
        <span className="text-sm md:text-base font-semibold tracking-wide">{value}</span>
      </div>

      {/* Bottom Row: Progress Bar */}
      <div className="w-full relative mt-2">
        <div className="h-4 flex items-center relative w-full">
          {/* Background Track */}
          <div className="absolute w-full h-[3px] bg-gray-700/50 rounded-full"></div>
          
          {/* Active Bar with Discrete Color - Hidden if percentile is null */}
          {percentile !== null && (
            <div 
                className={`absolute h-[5px] rounded-full shadow-[0_0_12px_rgba(255,255,255,0.15)] transition-all duration-1000 ease-out ${bgColor}`}
                style={{ 
                width: `${percentile}%`
                }}
            >
                {/* The Vertical Tick Marker at the end of the bar */}
                <div className="absolute right-0 top-1/2 -translate-y-1/2 h-3 w-[3px] rounded-full bg-white shadow-sm"></div>
                
                {/* Percentage Label floating above */}
                <div className={`absolute -top-6 right-0 translate-x-1/3 text-xs font-bold ${textColor}`}>
                {displayedPercentile}%
                </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};