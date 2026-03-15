import type { NextConfig } from "next";

const isVercel = process.env.VERCEL === "1";

const nextConfig: NextConfig = {
  /* config options here */
  // standalone output is needed for Docker/ECS but not compatible with Vercel
  ...(isVercel ? {} : { output: "standalone" }),
  reactCompiler: true,
  // Vercel manages deploymentId automatically; only set for self-hosted (ECS)
  ...(!isVercel && { deploymentId: process.env.DEPLOYMENT_ID || `build-${Date.now()}` }),
};

export default nextConfig;
