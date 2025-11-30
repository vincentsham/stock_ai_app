import { Pool } from 'pg';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../../../.env')});

// 1. Configure the pool with environment variables
const pool = new Pool({
  user: process.env.PGUSER,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  password: process.env.PGPASSWORD,
  port: parseInt(process.env.PGPORT || '5432', 10),
  // 2. Set key pooling parameters:
  max: 20, // Maximum number of clients (connections) in the pool
  idleTimeoutMillis: 30000, // How long a client can remain idle before being closed
  connectionTimeoutMillis: 2000, // How long the client should wait for a connection to be available
});

// 3. Optional: Add error logging for the pool itself
pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  // Process will exit if this error is not handled
});

export default pool;