"use client"

import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { Search, BarChart2 } from "lucide-react"

const HeaderNavOptions = () => {
  const router = useRouter()
  const pathname = usePathname() ?? "/"

  const onHomePage = pathname === "/"
  const onStockPage = pathname.startsWith("/stocks/")
  const onComparePage = pathname === "/compare" || pathname.startsWith("/compare/")

  const searchDisabled = onHomePage || onStockPage
  const searchActive = !onComparePage
  const compareActive = onComparePage

  return (
    <div className="flex justify-center bg-black p-1 rounded-lg border border-gray-800">
      <button
        type="button"
        onClick={() => router.push("/")}
        disabled={searchDisabled}
        aria-disabled={searchDisabled ? "true" : "false"}
        className={cn(
          "flex items-center gap-1 px-3 py-1 text-xs sm:text-sm font-medium rounded-md transition-all",
          searchActive
            ? "bg-gray-700 text-white shadow-sm"
            : "text-gray-400 border-transparent hover:text-gray-200 hover:bg-gray-800/50"
        )}
      >
        <Search className="w-4 h-4 mr-1" />
        Search
      </button>

      <button
        type="button"
        onClick={() => router.push("/compare")}
        className={cn(
          "flex items-center gap-1 px-3 py-1 text-xs sm:text-sm font-medium rounded-md transition-all",
          compareActive
            ? "bg-gray-700 text-white shadow-sm"
            : "text-gray-400 border-transparent hover:text-gray-200 hover:bg-gray-800/50"
        )}
      >
        <BarChart2 className="w-4 h-4 mr-1" />
        Compare
      </button>
    </div>
  )
}

export default HeaderNavOptions
