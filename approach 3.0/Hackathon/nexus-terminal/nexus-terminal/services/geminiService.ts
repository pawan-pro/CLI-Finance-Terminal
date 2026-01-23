
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { AIChatMessage, MarketContext } from "../types";
import { CONFIG } from "../config";

// Always initialize with process.env.API_KEY using named parameters
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const sendMessageToGemini = async (
  history: AIChatMessage[],
  newMessage: string,
  marketContext: MarketContext
): Promise<string> => {
  try {
    // Technical context for the model to provide high-quality financial analysis
    const contextStr = `
[MARKET CONTEXT]
Current Asset: ${marketContext.symbol} (${marketContext.quote?.name || 'N/A'})
Current Price: $${marketContext.quote?.price.toFixed(2)} (${marketContext.quote?.percent_change.toFixed(2)}%)
User Selection on Chart: ${marketContext.selectedRange.startDate || 'All'} to ${marketContext.selectedRange.endDate || 'Present'}
Recent Price Action: ${JSON.stringify(marketContext.recentHistory.slice(-5))}
`;

    // Map internal message format to the SDK's Content format
    const chatHistory = history.map(m => ({
      role: m.role,
      parts: [{ text: m.content }]
    }));

    // Generate content using the correct SDK pattern: ai.models.generateContent
    // Using the model defined in CONFIG (recommended: gemini-3-flash-preview for faster responses)
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: CONFIG.AI_MODEL,
      contents: [
        ...chatHistory,
        { role: 'user', parts: [{ text: `${contextStr}\n\nUser Question: ${newMessage}` }] }
      ],
      config: {
        tools: [{ googleSearch: {} }],
        systemInstruction: "You are Nexus Terminal AI, a world-class financial analyst. Provide high-density technical analysis. If a date range is selected, focus on the price movements within that window. Use Google Search to find relevant macro events or news explaining market volatility."
      }
    });

    // Access the .text property directly (it's a getter, not a method)
    let text = response.text || "I'm having trouble processing that data.";
    
    // Extract website URLs from groundingChunks when Google Search tool is utilized
    const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
    if (chunks && chunks.length > 0) {
      text += "\n\nSources:";
      const seen = new Set();
      chunks.forEach((c: any) => {
        if (c.web?.uri && !seen.has(c.web.uri)) {
          text += `\n• [${c.web.title || 'Market Source'}](${c.web.uri})`;
          seen.add(c.web.uri);
        }
      });
    }

    return text;
  } catch (error: any) {
    console.error("Gemini Error:", error);
    return `Analysis Interrupted: ${error.message}`;
  }
};
