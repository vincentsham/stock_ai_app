import { Pool, PoolConfig } from 'pg';
import '@/lib/loadEnv';

// 1. Extend global type for Singleton
declare global {
  var postgres: Pool | undefined;
}

// 2. Strict Connection Setup
// We ONLY use the connection string. No fallbacks.
const connectionString = process.env.PGCONNECTION_TRANSACTION;

if (!connectionString) {
  throw new Error('❌ FATAL: PGCONNECTION_TRANSACTION is missing from environment variables.');
}

const config: PoolConfig = {
  connectionString: connectionString,
  
  // Standard Pool Settings
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,

  // 3. SSL Logic
  // Supabase requires SSL. We enable it if the URL looks like a cloud URL or we are in production.
  ssl: (process.env.NODE_ENV === 'production' || connectionString.includes('supabase')) 
    ? { rejectUnauthorized: false } 
    : undefined,
};

let pool: Pool;

// 4. Singleton Pattern (Prevents connection leaks during Hot Reloads)
if (process.env.NODE_ENV === 'production') {
  pool = new Pool(config);
} else {
  if (!global.postgres) {
    console.log("🔌 Initializing database pool...");
    global.postgres = new Pool(config);
  }
  pool = global.postgres;
}

// 5. Error Listener
pool.on('error', (error: Error) => {
  console.error('❌ Unexpected error on idle client', error);
});

export default pool;



// import { Pool } from 'pg';
// // import '@/lib/loadEnv'; // Next.js loads .env automatically, usually not needed unless you have a custom setup.

// // 1. Extend the global type to include our pool (prevents TS errors)
// declare global {
//   var postgres: Pool | undefined;
// }

// // 2. Create the config object
// const config = {
//   user: process.env.PGUSER,
//   host: process.env.PGHOST,
//   database: process.env.PGDATABASE,
//   password: process.env.PGPASSWORD,
//   port: parseInt(process.env.PGPORT || '5432', 10),
//   max: 20,
//   idleTimeoutMillis: 30000,
//   connectionTimeoutMillis: 2000, // Warning: 2s is very short (see note below)
//   // 3. SSL is often required for production cloud DBs (Neon, Supabase, AWS RDS)
//   ssl: process.env.ENV === 'production' ? { rejectUnauthorized: false } : undefined,
// };

// let pool: Pool;

// // 4. The Singleton Check
// if (process.env.ENV === 'production') {
//   pool = new Pool(config);
// } else {
//   // In development, use a global variable so the pool survives hot reloads
//   if (!global.postgres) {
//     global.postgres = new Pool(config);
//   }
//   pool = global.postgres;
// }

// // 5. Error handling
// pool.on('error', (error: Error) => {
//   console.error('Unexpected error on idle client', error);
// });

// export default pool;


