import { coerceNumber } from './utils';

                //   const n = coerceNumber(value);
                //   return n === null ? 'N/A' : n.toFixed(2);

export function formatNumber(value: unknown): string {
    const n = coerceNumber(value);
    if (n === null || typeof n !== 'number' || isNaN(n)) {
        return 'N/A';
    }
    if (Math.abs(n) >= 1e12) {
        return (n / 1e12).toFixed(2) + 'T';
    }
    if (Math.abs(n) >= 1e9) {
        return (n / 1e9).toFixed(2) + 'B';
    }
    if (Math.abs(n) >= 1e6) {
        return (n / 1e6).toFixed(1) + 'M';
    }
    if (Math.abs(n) >= 1e3) {
        return (n / 1e3).toFixed(1) + 'K';
    }
    if (Math.abs(n) < 1) {
        return n.toFixed(2);
    }
    return n.toFixed(1);
}

export function formatInteger(value: unknown): string {
    const n = coerceNumber(value);
    if (n === null || typeof n !== 'number' || isNaN(n)) {
        return 'N/A';
    }
    if (Math.abs(n) >= 1e12) {
        return (n / 1e12).toFixed(2) + 'T';
    }
    if (Math.abs(n) >= 1e9) {
        return (n / 1e9).toFixed(2) + 'B';
    }
    if (Math.abs(n) >= 1e6) {
        return (n / 1e6).toFixed(1) + 'M';
    }
    if (Math.abs(n) >= 1e3) {
        return (n / 1e3).toFixed(1) + 'K';
    }
    return n.toFixed(0);
}



export function formatCurrency(value: unknown): string {
    const n = coerceNumber(value);
    if (n === null || typeof n !== 'number' || isNaN(n)) {
        return 'N/A';
    }
    if (n < 0) {
        return `-$${formatNumber(Math.abs(n))}`;
    }
    return `$${formatNumber(n)}`;
};


export function formatRatio(value: unknown): string {
    const n = coerceNumber(value);
    if (n === null || typeof n !== 'number' || isNaN(n)) {
        return 'N/A';
    }
    return `${formatNumber(n)}x`;
};

export function formatPercentage(value: unknown): string {
    const n = coerceNumber(value);
    if (n === null || typeof n !== 'number' || isNaN(n)) {
        return 'N/A';
    }
    if (Math.abs(n) >= 0.1) {
        return `${(n * 100).toFixed(1)}%`;
    }
    return `${(n * 100).toFixed(2)}%`;
}
