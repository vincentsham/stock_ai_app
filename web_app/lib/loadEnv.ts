import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

// 1. Check for the toggle (defaults to 'local')
const appEnv = process.env.APP_ENV || 'local';

// 2. In AWS, environment variables are injected by ECS task definition
//    (via Secrets Manager + plain env vars). No file loading needed.
if (appEnv === 'aws') {
  console.log('☁️  Running in AWS — using ECS-injected environment variables.');
} else {
  // 3. Local development: load .env.local
  const fileName = '.env.local';

  const candidates = [
    path.resolve(process.cwd(), fileName),
    path.resolve(process.cwd(), `../${fileName}`),
  ];

  const envPath = candidates.find((candidate) => fs.existsSync(candidate));

  if (envPath) {
    dotenv.config({ path: envPath, override: true });
    console.log(`✅ Web App loaded: ${fileName}`);
  } else {
    console.warn(`⚠️ No ${fileName} found. Using system environment variables.`);
  }
}