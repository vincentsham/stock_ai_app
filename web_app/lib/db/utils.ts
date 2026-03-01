import { Pool, PoolConfig } from 'pg';
import '@/lib/loadEnv';

declare global {
  var postgres: Pool | undefined;
}

// 1. Identify Environment
const appEnv = process.env.APP_ENV || 'local';
const isAWS = appEnv === 'aws';

// 2. Select Connection String based on environment
//   - AWS:   PGCONNECTION_TRANSACTION → RDS (injected by ECS / Secrets Manager)
//   - Local: SUPABASE_TRANSACTION     → Supabase (loaded from .env.local)
const connectionString = isAWS
  ? process.env.PGCONNECTION_TRANSACTION
  : process.env.SUPABASE_TRANSACTION;

if (!connectionString) {
  throw new Error(
    `❌ FATAL: Connection string missing. APP_ENV=${appEnv}, ` +
    `expected ${isAWS ? 'PGCONNECTION_TRANSACTION' : 'SUPABASE_TRANSACTION'}`
  );
}

// 3. Environment-Specific Config
const config: PoolConfig = {
  connectionString: connectionString,
  max: isAWS ? 20 : 10, // Higher pool limit for production AWS
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: isAWS ? 10000 : 5000,

  // 4. SSL — required for both RDS and Supabase
  ssl: { rejectUnauthorized: false },
};

// 5. Singleton Pattern
let pool: Pool;

if (process.env.NODE_ENV === 'production' || isAWS) {
  pool = new Pool(config);
} else {
  if (!global.postgres) {
    console.log(`🔌 Initializing ${isAWS ? 'AWS RDS' : 'Local/Supabase'} pool...`);
    global.postgres = new Pool(config);
  }
  pool = global.postgres;
}

pool.on('error', (err) => console.error('❌ DB Pool Error:', err));

export default pool;