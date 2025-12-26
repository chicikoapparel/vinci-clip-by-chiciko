/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '2gb',
    },
  },
};

module.exports = nextConfig;
