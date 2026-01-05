"use client"

import { TrendingUp } from "lucide-react"
import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandList,
} from "@/components/ui/command"
import { useDebounce } from "@/hooks/useDebounce"
import React, { useState, useEffect, useCallback, useRef } from "react"
import { searchStocks } from "@/lib/db/stockQueries" // Ensure this path is correct
import Link from "next/link";
import { StockProfile } from "@/types"; // Ensure this path is correct
import type { KeyboardEvent } from "react"
import { useRouter, usePathname, useSearchParams } from "next/navigation"
import { MAX_COMPARE_STOCKS } from "@/lib/constants";

const SearchBar = () => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  
  // 1. Detect if we are in "Compare Mode"
  const isCompareMode = pathname.startsWith('/compare');
  const isSearchMode = pathname === "/" || pathname.startsWith('/stock');

  // 2. Ref for Focus Handling (from your previous request)
  const inputRef = useRef<HTMLInputElement>(null);

  const [placeholder, setPlaceholder] = useState("Search Stocks (e.g. NVDA or Nvidia)");
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [stocks, setStocks] = useState<StockProfile[]>([]);

  // --- EFFECT: Responsive Placeholder ---
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const updatePlaceholder = () => {
      setPlaceholder(window.innerWidth < 640 ? "e.g. NVDA, Nvidia" : "Search Stocks (e.g. NVDA or Nvidia)");
    };
    updatePlaceholder();
    window.addEventListener('resize', updatePlaceholder);
    return () => window.removeEventListener('resize', updatePlaceholder);
  }, []);

  // --- EFFECT: Listen for "focus-search" event ---
  useEffect(() => {
    const handleFocus = () => {
      // Small timeout to ensure the CommandInput is mounted/ready
      setTimeout(() => inputRef.current?.focus(), 50);
    };
    window.addEventListener('focus-search', handleFocus);
    return () => window.removeEventListener('focus-search', handleFocus);
  }, []);

  // --- LOGIC: Generate Destination URL ---
  const getDestination = useCallback((ticker: string) => {
  if (isCompareMode) {
      // 1. Get current stocks from URL
      const currentParams = new URLSearchParams(Array.from(searchParams.entries()));
      
      // FIX: Add .filter(Boolean) to remove empty strings caused by "?stocks="
      const rawParam = currentParams.get('stocks');
      const existingStocks = rawParam ? rawParam.split(',').filter(Boolean) : [];
      
      // 2. Add ticker if not present
      if (!existingStocks.includes(ticker)) {
        existingStocks.push(ticker);
        
        // 3. Limit to MAX_COMPARE_STOCKS (Check limit BEFORE saving)
        if (existingStocks.length > MAX_COMPARE_STOCKS) {
            // Optional: alert user or just ignore the add
            // For now, let's just keep the list at max size
            return `${pathname}?${currentParams.toString()}`; 
        }

        currentParams.set('stocks', existingStocks.join(','));
      }

      return `${pathname}?${currentParams.toString()}`;
    }
    // Default behavior: Go to single stock page
    return `/stocks/${ticker}`;
  }, [isCompareMode, pathname, searchParams]);

  // --- LOGIC: Search ---
  const handleSearch = useCallback(async () => {
    if (!searchTerm.trim()) return;
    try {
      const results = await searchStocks(searchTerm.trim());
      setStocks(results);
    } catch {
      setStocks([]);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  const debouncedSearch = useDebounce(handleSearch, 400);

  useEffect(() => {
    if (!searchTerm.trim()) return setSearching(false);
    setSearching(true);
    setLoading(true);
    debouncedSearch();
  }, [searchTerm, debouncedSearch]);

  const handleSelectStock = useCallback(() => {
    setSearching(false);
    setLoading(false);
    setSearchTerm("");
    setStocks([]);
  }, []);

  // --- LOGIC: Enter Key ---
  const handleEnterKey = useCallback((event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== "Enter" || loading || stocks.length === 0) {
      return;
    }

    event.preventDefault();
    const [firstStock] = stocks;
    if (!firstStock) return;

    handleSelectStock();

    // Use the helper to determine where to go
    const destination = getDestination(firstStock.tic);
    router.push(destination);
  }, [loading, stocks, getDestination, router, handleSelectStock]);

  return (
    <Command className="group rounded-lg border shadow-md md:min-w-[450px] focus-within:border-white">
      <CommandInput
        ref={inputRef}
        value={searchTerm}
        onValueChange={setSearchTerm}
        placeholder={placeholder}
        className="text-xs sm:text-sm placeholder:text-ellipsis"
        onKeyDown={handleEnterKey}
      />

      <CommandList className="hidden group-focus-within:block">
        {!searching ? null : loading ? (
          <CommandEmpty className="search-list-empty">Loading stocks...</CommandEmpty>
        ) : stocks.length === 0 ? (
          <CommandEmpty className="search-list-empty">No results found.</CommandEmpty>
        ) : (
          <ul>
            {stocks.map((stock) => (
              <li key={stock.tic} className="search-item hover:bg-slate-800 hover:scale-[1.02] transition-transform">
                <Link
                  href={getDestination(stock.tic)} // Dynamic HREF based on page
                  onClick={handleSelectStock}
                  scroll={!isCompareMode} // Don't scroll to top if we are just adding to list
                  className="search-item-link"
                >
                  <TrendingUp className="h-4 w-4 text-gray-500" />
                  <div className="flex-1">
                    <div className="search-item-name">{stock.name}</div>
                    <div className="text-sm text-gray-500">
                      {stock.tic} | {stock.exchange} | {stock.sector} | {stock.industry}
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CommandList>
    </Command>
  )
}

export default SearchBar