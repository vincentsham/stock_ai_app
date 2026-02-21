import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

// 1. Check for the toggle (defaults to 'local')
const appEnv = process.env.APP_ENV || 'local';

// 2. Map the environment to the specific file name
const fileName = appEnv === 'aws' ? '.env.aws' : '.env.local';

// 3. Resolve the path (looking in the current folder or one folder up)
const candidates = [
  path.resolve(process.cwd(), fileName),
  path.resolve(process.cwd(), `../${fileName}`),
];

const envPath = candidates.find((candidate) => fs.existsSync(candidate));

if (envPath) {
  // 4. Use 'override: true' to match your Python logic
  dotenv.config({ path: envPath, override: true });
  console.log(`✅ Web App loaded: ${fileName}`);
} else {
  console.warn(`⚠️ No ${fileName} found. Using system environment variables.`);
}