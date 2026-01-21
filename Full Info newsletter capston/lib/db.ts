import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';

// TODO: Replace with your actual Neon database URL in .env.local
// Get your database URL from: https://console.neon.tech/
const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is not set. Please check your .env.local file.');
}

const sql = neon(connectionString);
export const db = drizzle(sql);
