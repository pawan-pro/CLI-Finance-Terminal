
import { AIChatMessage, MarketContext } from "../types";
import { CONFIG } from "../config";

export const sendMessageToGemini = async (
  history: AIChatMessage[],
  newMessage: string,
  marketContext: MarketContext
): Promise<string> => {
  try {
    // Technical context for the model to provide high-quality financial analysis
    const context = {
      symbol: marketContext.symbol,
      assetName: marketContext.quote?.name || 'N/A',
      price: marketContext.quote?.price,
      percentChange: marketContext.quote?.percent_change,
      selectedRange: {
        start: marketContext.selectedRange.startDate || 'All',
        end: marketContext.selectedRange.endDate || 'Present'
      },
      recentPriceAction: marketContext.recentHistory.slice(-10),
      visionAnalysis: marketContext.visionAnalysis
    };

    // Route message through our Backend Bridge to manage quotas and caching
    const response = await fetch(`${CONFIG.BACKEND_API_BASE}/api/ai/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: newMessage,
        history: history.map(m => ({ role: m.role, content: m.content })),
        context: context
      }),
    });

    if (!response.ok) {
      throw new Error(`AI Bridge Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.response || "I'm having trouble processing that data.";
  } catch (error: any) {
    console.error("Gemini Bridge Error:", error);
    return `The Strategist is currently reviewing deep-book liquidity. System Note: ${error.message}`;
  }
};
