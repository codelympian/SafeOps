import type { NextConfig } from "next";

// cacheComponents / partialPrefetching are off on purpose (ADR-017): every page's
// data comes from the FastAPI backend, fetched in the browser with the session
// cookie, so Next's server-side caching has nothing to cache.
const nextConfig: NextConfig = {
  poweredByHeader: false,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
