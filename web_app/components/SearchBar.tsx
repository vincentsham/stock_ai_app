import {
  Calculator,
  Calendar,
  Smile,
} from "lucide-react"

import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"

const SearchBar = () => {
  return (
    <Command className="group rounded-lg border shadow-md md:min-w-[450px]">
      <CommandInput
        placeholder="Search for a stock by symbol or name..."
      />
      {/* Hidden by default, visible when any child in Command is focused */}
      <CommandList className="hidden group-focus-within:block">
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>
            <Calendar className="mr-2 h-4 w-4" />
            <span>Calendar</span>
          </CommandItem>
          <CommandItem>
            <Smile className="mr-2 h-4 w-4" />
            <span>Search Emoji</span>
          </CommandItem>
          <CommandItem disabled>
            <Calculator className="mr-2 h-4 w-4" />
            <span>Calculator</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </Command>
  )
}

export default SearchBar