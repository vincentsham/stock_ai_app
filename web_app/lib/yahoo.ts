// lib/yahoo.ts
import yahooFinance from 'yahoo-finance2';

// Force the suppression by casting to 'any' to bypass the TypeScript error
// @ts-ignore
if (typeof yahooFinance.suppressNotices === 'function') {
    // @ts-ignore
    yahooFinance.suppressNotices(['yahooSurvey', 'ripHistorical']);
}

export default yahooFinance;