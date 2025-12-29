import { Pool } from 'pg';
// import '@/lib/loadEnv'; // Next.js loads .env automatically, usually not needed unless you have a custom setup.

// 1. Extend the global type to include our pool (prevents TS errors)
declare global {
  var postgres: Pool | undefined;
}

// 2. Create the config object
const config = {
  user: process.env.PGUSER,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  password: process.env.PGPASSWORD,
  port: parseInt(process.env.PGPORT || '5432', 10),
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000, // Warning: 2s is very short (see note below)
  // 3. SSL is often required for production cloud DBs (Neon, Supabase, AWS RDS)
  ssl: process.env.ENV === 'production' ? { rejectUnauthorized: false } : undefined,
};

let pool: Pool;

// 4. The Singleton Check
if (process.env.ENV === 'production') {
  pool = new Pool(config);
} else {
  // In development, use a global variable so the pool survives hot reloads
  if (!global.postgres) {
    global.postgres = new Pool(config);
  }
  pool = global.postgres;
}

// 5. Error handling
pool.on('error', (error: Error) => {
  console.error('Unexpected error on idle client', error);
});

export default pool;




// import { Pool } from 'pg';
// import '@/lib/loadEnv';

// // 1. Configure the pool with environment variables
// const pool = new Pool({
//   user: process.env.PGUSER,
//   host: process.env.PGHOST,
//   database: process.env.PGDATABASE,
//   password: process.env.PGPASSWORD,
//   port: parseInt(process.env.PGPORT || '5432', 10),
//   // 2. Set key pooling parameters:
//   max: 20, // Maximum number of clients (connections) in the pool
//   idleTimeoutMillis: 30000, // How long a client can remain idle before being closed
//   connectionTimeoutMillis: 2000, // How long the client should wait for a connection to be available
// });

// // 3. Optional: Add error logging for the pool itself
// pool.on('error', (error: Error) => {
//   console.error('Unexpected error on idle client', error);
//   // Process will exit if this error is not handled
// });

// export default pool;