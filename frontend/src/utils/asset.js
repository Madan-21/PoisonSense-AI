// Helper to resolve public asset paths with the correct base URL
// Works both in dev (base="/") and production (base="/PoisonSense-AI/")
const BASE = import.meta.env.BASE_URL || '/';

export function asset(path) {
  // Remove leading slash from path if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${BASE}${cleanPath}`;
}

export default asset;
