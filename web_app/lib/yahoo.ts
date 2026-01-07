// lib/yahoo.ts
import { YahooFinance } from 'yahoo-finance2'; // 1. Import the Class (named export)

const yahooFinance = new YahooFinance(); // 2. Create a specific instance

// Force the suppression by casting to 'any' to bypass the TypeScript error
// @ts-ignore
if (typeof yahooFinance.suppressNotices === 'function') {
    // @ts-ignore
    yahooFinance.suppressNotices(['yahooSurvey', 'ripHistorical']);
}

export default yahooFinance;