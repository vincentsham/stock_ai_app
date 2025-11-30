import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

const candidates = [
  path.resolve(process.cwd(), '.env'),
  path.resolve(process.cwd(), '../.env'),
];

const envPath = candidates.find((candidate) => fs.existsSync(candidate));

if (envPath) {
  dotenv.config({ path: envPath, quiet: true });
} else {
  console.warn('No .env file found relative to process.cwd()');
}
