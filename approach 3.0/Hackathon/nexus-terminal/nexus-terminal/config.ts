
/**
 * NEXUS TERMINAL CONFIGURATION
 */

export const CONFIG = {
  // LOCAL BACKEND API
  BACKEND_API_BASE: 'http://localhost:8000',

  // GEMINI CONFIGURATION
  // Updated to gemini-3-flash-preview for faster responses
  AI_MODEL: 'gemini-3-flash-preview',

  // REFRESH INTERVALS (ms)
  // Using backend bridge for all market data
  POLLING: {
    ACTIVE_ASSET: 15000,    // 15 seconds for live updates
    WATCHLIST: 15000,       // 15 seconds for live updates
    NEWS: 120000,           // 120 seconds
    MACRO_TICKER: 3000      // Local Simulation
  }
};
