import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone",
  reactCompiler: true,
  // Unique deployment ID helps Next.js distinguish between deployments
  // and produce clearer errors when clients reference stale server actions
  deploymentId: process.env.DEPLOYMENT_ID || `build-${Date.now()}`,
};

export default nextConfig;
