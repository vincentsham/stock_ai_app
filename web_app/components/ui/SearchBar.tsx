"use client";

import { useState } from "react";
// ✅ Correct: Import from your local components folder
import {
  CommandDialog,
  CommandEmpty,
  CommandInput,
  CommandList,
} from "@/components/ui/command"; 
import { Button } from "@/components/ui/button";

const SearchBar = () => {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  return (
    <>
      <Button onClick={() => setOpen(true)} className="search-btn">
        Search
      </Button>
      <CommandDialog open={open} onOpenChange={setOpen} className="search-dialog">
        <div className="search-field">
          <CommandInput
            value={searchTerm}
            onValueChange={setSearchTerm}
            placeholder="Search..."
            className="search-input"
          />
        </div>
        <CommandList className="search-list">
          <CommandEmpty>No results found.</CommandEmpty>
        </CommandList>
      </CommandDialog>
    </>
  );
};

export default SearchBar;