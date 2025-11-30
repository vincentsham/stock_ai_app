import pool from '@/lib/db/utils';


async function testDbConnection() {
  try {
    // Test the connection by running a simple query
    const res = await pool.query('SELECT NOW() AS current_time');
    console.log('Database connection successful:', res.rows[0].current_time);
  } catch (err) {
    console.error('Database connection failed:', err);
  } finally {
    // End the pool to close all connections
    await pool.end();
  }
}

testDbConnection();