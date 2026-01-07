import yahooFinance from '@/lib/yahoo';

let instance: any;

// 1. Check if the default import is already an instance (has .quote function)
// This is usually true on Localhost
if (typeof (yahooFinance as any).quote === 'function') {
    instance = yahooFinance;
} 
// 2. If not, it's the Class Constructor (Common on Vercel)
// So we must instantiate it manually.
else {
    // @ts-ignore: Bypass TS check to allow instantiation of default export
    instance = new yahooFinance();
}

// 3. Now we can safely suppress notices on the valid instance
if (instance && typeof instance.suppressNotices === 'function') {
    instance.suppressNotices(['yahooSurvey', 'ripHistorical']);
}

export default instance;