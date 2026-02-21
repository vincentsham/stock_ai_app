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

