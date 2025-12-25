"use client";

import React, { useState, useMemo, useEffect, useRef } from 'react';
import { Share2, Plus, TrendingUp, Sun, Moon, Search, X, AlertCircle } from 'lucide-react';
// import StockCard from './components/StockCard';

const MAX_STOCKS = 5;
export const CompareSection = () => {
  const [stocks, setStocks] = useState<[]>([]);
  const [viewMode, setViewMode] = useState<'Percentile' | 'Value'>('Percentile');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [valuationExpanded, setValuationExpanded] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchDropdownRef = useRef<HTMLDivElement>(null);


  const isLimitReached = stocks.length >= MAX_STOCKS;
  return (
      <>
      <div className="flex justify-center mb-8 shrink-0">
        <div className="flex bg-gray-200 dark:bg-gray-800 p-1 rounded-lg w-full max-w-xs shadow-inner">
          <button 
            onClick={() => setViewMode('Percentile')}
            className={`flex-1 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'Percentile' ? 'bg-black dark:bg-white text-white dark:text-black shadow-md' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-700'}`}
          >
            Rankings
          </button>
          <button 
            onClick={() => setViewMode('Value')}
            className={`flex-1 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'Value' ? 'bg-black dark:bg-white text-white dark:text-black shadow-md' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-700'}`}
          >
            Raw Values
          </button>
        </div>
      </div>

      {/* Main Comparison Area */}
      <div className="w-full overflow-x-auto pb-8 scrollbar-hide">
        <div className="flex space-x-2 md:space-x-4 w-fit mx-auto justify-start px-4 items-stretch">
          {stocks.length > 0 ? (
            <>
              {stocks.map((stock) => (
                <div  className="flex-shrink-0">
                  {/* <StockCard 
                    stock={stock} 
                    onRemove={() => {}}
                    maxStats={maxStats}
                    isLeaderIn={true}
                    valuationExpanded={valuationExpanded}
                    onToggleValuation={() => setValuationExpanded(!valuationExpanded)}
                  /> */}
                </div>
              ))}
              
              {!isLimitReached && (
                <div 
                  onClick={() => {}}
                  className="w-[160px] md:w-[250px] border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg flex flex-col items-center justify-center space-y-4 flex-shrink-0 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800/50 hover:border-black dark:hover:border-gray-500 transition-all group min-h-[500px]"
                >
                  <div className="relative">
                    <div className="w-8 h-8 md:w-16 md:h-16 rounded-full border-2 border-gray-200 dark:border-gray-700 flex items-center justify-center text-gray-400 dark:text-gray-600 group-hover:text-black dark:group-hover:text-white group-hover:border-black dark:group-hover:border-white transition-colors">
                      <Plus size={20} className="md:w-8 md:h-8" />
                    </div>
                  </div>
                  <p className="text-gray-500 dark:text-gray-500 text-[8px] md:text-[10px] font-bold uppercase tracking-widest text-center px-1">Compare Ticker</p>
                </div>
              )}
            </>
          ) : (
            <div className="w-full py-20 flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                <TrendingUp className="text-gray-400 opacity-40" size={40} />
              </div>
              <h3 className="text-xl font-bold text-gray-400">Start by searching for a ticker</h3>
            </div>
          )}
        </div>
      </div>
    </>
  )
}


