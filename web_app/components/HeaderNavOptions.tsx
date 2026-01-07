"use client"

import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { Search, BarChart2, LucideIcon, GitCompare } from "lucide-react"

type NavItem = {
  label: string
  icon: LucideIcon
  route: string
  isActive: boolean
}

const HeaderNavOptions = () => {
  const router = useRouter()
  const pathname = usePathname() ?? "/"

  // 1. Determine Context
  // logic: If we are on /compare or /compare/*, we are in Compare mode.
  // Otherwise, we default to Search mode.
  const isCompareMode = pathname.startsWith("/compare")
  const isSearchMode = !isCompareMode
  // const isSearchMode = pathname === "/" || pathname.startsWith("/stocks")

  const navItems: NavItem[] = [
    {
      label: "Search",
      icon: Search,
      route: "/",
      isActive: isSearchMode,
    },
    {
      label: "Compare",
      icon: GitCompare,
      route: "/compare",
      isActive: isCompareMode,
    },
  ]

  return (
    <div className="flex justify-center bg-black p-1 rounded-lg border border-gray-800">
      {navItems.map((item) => (
        <button
          key={item.label}
          type="button"
          // If the tab is active, we disable the button to prevent redirection
          disabled={item.isActive}
          onClick={() => router.push(item.route)}
          className={cn(
            "flex items-center gap-1 px-3 py-1 text-xs sm:text-sm font-medium rounded-md transition-all",
            item.isActive
              ? "bg-gray-600 text-white shadow-sm cursor-default" // Active state (non-clickable)
              : "text-gray-400 border-transparent hover:text-white hover:bg-gray-700 cursor-pointer" // Inactive state
          )}
        >
          <item.icon className="w-4 h-4 mr-1 hidden sm:inline-block" />
          {item.label}
        </button>
      ))}
    </div>
  )
}

export default HeaderNavOptions