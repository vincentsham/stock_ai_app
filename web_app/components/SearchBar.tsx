"use client"

import {
  Loader2, TrendingUp
} from "lucide-react"

import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandList,
} from "@/components/ui/command"

import { useDebounce } from "@/hooks/useDebounce"
import { useState, useEffect, useCallback } from "react"
import { searchStocks } from "@/lib/db/stockQueries"
import Link from "next/link";
import { StockProfile } from "@/types";
import type { KeyboardEvent } from "react"
import { useRouter } from "next/navigation"

const SearchBar = () => {
  const router = useRouter();
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [stocks, setStocks] = useState<StockProfile[]>([]);  

  const handleSearch = async () => {
    if(!searchTerm.trim()) return;
    try {
      const results = await searchStocks(searchTerm.trim());
      setStocks(results);
    } catch {
      setStocks([]);
    } finally {
      setLoading(false);
    }
  }

  const debouncedSearch = useDebounce(handleSearch, 400);

  useEffect(() => {
    if(!searchTerm.trim()) return setSearching(false);
    setSearching(true);
    setLoading(true);
    debouncedSearch();
  }, [searchTerm]);

  const handleSelectStock = useCallback(() => {
    setSearching(false);
    setLoading(false);
    setSearchTerm("");
    setStocks([]);
  }, []);

  const handleEnterKey = useCallback((event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== "Enter" || loading || stocks.length === 0) {
      return;
    }

    event.preventDefault();
    const [firstStock] = stocks;
    if (!firstStock) {
      return;
    }

    handleSelectStock();
    router.push(`/stocks/${firstStock.tic}`);
  }, [handleSelectStock, loading, router, stocks]);

  return (
    <Command className="group rounded-lg border shadow-md md:min-w-[450px]">
      {/* <CommandInput
        placeholder="Search for a stock by symbol or name..."
      /> */}
      <div className="search-field">
          <CommandInput value={searchTerm} onValueChange={setSearchTerm} placeholder="Search for a stock by symbol or name..." className="search-input" onKeyDown={handleEnterKey} />
          {searching && loading && <Loader2 className="search-loader" />}
      </div>

      {/* Hidden by default, visible when any child in Command is focused */}
      <CommandList className="hidden group-focus-within:block">
        { 
          !searching ? (
            null
          ) : loading ? (
            <CommandEmpty className="search-list-empty">Loading stocks...</CommandEmpty>
          ) : stocks.length === 0 ? (
            <CommandEmpty className="search-list-empty">No results found.</CommandEmpty>
          ) : stocks.length > 0 ? (
            <ul>
              {stocks?.map((stock, i) => (
                  <li key={stock.tic} className="search-item">
                    <Link
                        href={`/stocks/${stock.tic}`}
                        onClick={handleSelectStock}
                        className="search-item-link"
                    >
                      <TrendingUp className="h-4 w-4 text-gray-500" />
                      <div  className="flex-1">
                        <div className="search-item-name">
                          {stock.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {stock.tic} | {stock.exchange } | {stock.sector} | {stock.industry}
                        </div>
                      </div>
                    {/*<Star />*/}
                    </Link>
                  </li>
              ))}
            </ul>
          ) : null
        }
      </CommandList>
    </Command>
  )
}

export default SearchBar