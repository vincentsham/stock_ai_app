import { Pool, PoolConfig } from 'pg';
import '@/lib/loadEnv';

declare global {
  var postgres: Pool | undefined;
}

// Lazy singleton — the pool is created on first use so that `next build`
// can statically analyse pages without requiring a live connection string.

function createPool(): Pool {
  // Return existing singleton if available (prevents re-creation in production)
  if (global.postgres) return global.postgres;

  // 1. Identify Environment (set APP_ENV in each environment: 'local' | 'vercel' | 'aws')
  const appEnv = process.env.APP_ENV || (process.env.VERCEL ? 'vercel' : 'local');
  const isAWS = appEnv === 'aws';
  const isLocal = appEnv === 'local';

  // 2. Select Connection String based on environment
  //   - AWS:    PGCONNECTION_TRANSACTION → RDS (injected by ECS / Secrets Manager)
  //   - Vercel: SUPABASE_TRANSACTION     → Supabase (set in Vercel env vars)
  //   - Local:  SUPABASE_TRANSACTION     → Supabase (loaded from .env.local)
  const connectionString = isAWS
    ? process.env.PGCONNECTION_TRANSACTION
    : process.env.SUPABASE_TRANSACTION;
  const connectionSource = isAWS ? 'PGCONNECTION_TRANSACTION' : 'SUPABASE_TRANSACTION';

  if (!connectionString) {
    throw new Error(
      `❌ FATAL: Connection string missing. APP_ENV=${appEnv}, ` +
      `expected ${connectionSource} env var to be set.`
    );
  }

  // 3. Environment-Specific Config
  const connectionTimeoutMillis = process.env.DB_CONNECTION_TIMEOUT_MS
    ? Number(process.env.DB_CONNECTION_TIMEOUT_MS)
    : 60000;

  const config: PoolConfig = {
    connectionString,
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis,
    ssl: isLocal ? false : { rejectUnauthorized: false },
  };
  console.log(`🔌 Using ${connectionSource} for APP_ENV=${appEnv} (timeout=${connectionTimeoutMillis}ms)`);

  // 4. Create & cache the singleton
  console.log(`🔌 Initializing ${isAWS ? 'AWS RDS' : 'Local/Supabase'} pool (max=${config.max})...`);
  const pool = new Pool(config);
  pool.on('error', (err) => console.error('❌ DB Pool Error:', err));

  global.postgres = pool;
  return pool;
}

// Proxy that defers pool creation until a property/method is actually accessed.
const pool: Pool = new Proxy({} as Pool, {
  get(_target, prop, receiver) {
    // Lazily create / retrieve the real pool on first access
    if (!global.postgres) {
      createPool();
    }
    return Reflect.get(global.postgres!, prop, receiver);
  },
});

export default pool;