/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["supports-color"],
  experimental: {
		serverComponentsExternalPackages: ["llamaindex"],
	},
}


module.exports = nextConfig
