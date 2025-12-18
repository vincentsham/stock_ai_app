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