import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}



export const coerceNumber = (value: unknown): number | null => {
      if (value === null || value === undefined) return null;
      if (typeof value === 'number') return Number.isFinite(value) ? value : null;
      if (typeof value === 'string') {
            const trimmed = value.trim();
            if (trimmed === '') return null;
            const parsed = Number(trimmed);
            return Number.isFinite(parsed) ? parsed : null;
      }
      return null;
};

export const fixQuotes = (str: string): string => {
        // Convert single-quote delimiters to double quotes, but keep
        // apostrophes inside words (e.g., they're, it's).
        str = str.replace(/'+/g, "'").replace(/"+/g, '"');
        return str.replace(/'/g, (_match, index: number) => {
                  const prev = index > 0 ? str.charAt(index - 1) : '';
                  const next = index < str.length - 1 ? str.charAt(index + 1) : '';
                  const isPrevWord = /[A-Za-z0-9]/.test(prev);
                  const isNextWord = /[A-Za-z0-9]/.test(next);
                  if (isPrevWord && isNextWord) {
                              // Likely an apostrophe within a word; keep as single quote.
                              return "'";
                  }
                  // Otherwise, treat as a quote delimiter and convert to double quote.
                  return '"';
        });
};