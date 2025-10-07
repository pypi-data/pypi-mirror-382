import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://os-forge:8000/:path*',
      },
    ];
  },
};

export default nextConfig;