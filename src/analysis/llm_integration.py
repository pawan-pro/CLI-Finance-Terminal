"""
LLM Integration Module for AI-Powered Executive Summaries
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMExecutiveSummaryGenerator:
    """Class to generate AI-powered executive summaries using Krutrim's Phi-4-reasoning-plus model"""
    
    def __init__(self):
        """Initialize the LLM generator with API credentials and model details"""
        # Load API key from file
        self.api_key = self._load_api_key()
        self.model_name = "Phi-4-reasoning-plus"
        self.base_url = "https://cloud.olakrutrim.com/v1/chat/completions"
        
        # Recommended generation parameters from model card
        self.default_params = {
            "temperature": 0.8,
            "top_k": 50,
            "top_p": 0.95,
            "do_sample": True,
            "max_tokens": 2048
        }
        
        # System prompt from model card
        self.system_prompt = (
            "You are Phi, a language model trained by Microsoft to help users. "
            "Your role as an assistant involves thoroughly exploring questions through a systematic thinking process "
            "before providing the final precise and accurate solutions. This requires engaging in a comprehensive "
            "cycle of analysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to "
            "develop well-considered thinking process. Please structure your response into two main sections: "
            "Thought and Solution using the specified format: "
            "{Thought section}  "
            "{Solution section}. "
            "In the Thought section, detail your reasoning process in steps. Each step should include detailed "
            "considerations such as analysing questions, summarizing relevant findings, brainstorming new ideas, "
            "verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. "
            "In the Solution section, based on various attempts, explorations, and reflections from the Thought "
            "section, systematically present the final solution that you deem correct. The Solution section should "
            "be logical, accurate, and concise and detail necessary steps needed to reach the conclusion."
        )
    
    def _load_api_key(self) -> str:
        """Load API key from the LLM directory"""
        try:
            # Construct path relative to the project root
            from pathlib import Path
            BASE_DIR = Path(__file__).resolve().parent.parent.parent
            api_key_path = BASE_DIR / "LLM" / "api key.txt"
            with open(api_key_path, 'r') as f:
                api_key = f.read().strip()
            return api_key
        except Exception as e:
            logger.error(f"Error loading API key: {e}")
            raise
    
    def _format_market_data_as_text(self, indices_data: pd.DataFrame, currency_data: pd.DataFrame, 
                                   commodities_data: pd.DataFrame, top_movers: pd.DataFrame, 
                                   calendar_data: pd.DataFrame) -> str:
        """Format market data as text for LLM input"""
        market_text = []
        
        # Add header
        market_text.append("=== DAILY MARKET DATA ===")
        
        # Major Indices
        if not indices_data.empty:
            market_text.append("\nMAJOR INDICES PERFORMANCE:")
            for _, row in indices_data.head(10).iterrows():
                name = row.get('name', 'N/A')
                price = row.get('Price', 'N/A')
                pct_change = row.get('pct_change_24h', 0)
                direction = "+" if pct_change >= 0 else ""
                market_text.append(f"  {name}: Price={price}, 24h Change={direction}{pct_change:.2f}%")
        
        # Major Currencies
        if not currency_data.empty:
            market_text.append("\nMAJOR CURRENCY MARKETS:")
            for _, row in currency_data.head(10).iterrows():
                name = row.get('name', 'N/A')
                price = row.get('Price', 'N/A')
                pct_change = row.get('pct_change_24h', 0)
                direction = "+" if pct_change >= 0 else ""
                market_text.append(f"  {name}: Price={price}, 24h Change={direction}{pct_change:.2f}%")
        
        # Commodities
        if not commodities_data.empty:
            market_text.append("\nCOMMODITIES MARKETS:")
            for _, row in commodities_data.head(10).iterrows():
                name = row.get('name', 'N/A')
                price = row.get('Price', 'N/A')
                pct_change = row.get('pct_change_24h', 0)
                direction = "+" if pct_change >= 0 else ""
                market_text.append(f"  {name}: Price={price}, 24h Change={direction}{pct_change:.2f}%")
        
        # Top Movers
        if not top_movers.empty:
            market_text.append("\nTOP MARKET MOVERS (24H):")
            for _, row in top_movers.head(10).iterrows():
                name = row.get('name', 'N/A')
                price = row.get('Price', 'N/A')
                pct_change = row.get('pct_change', 0)
                direction = "+" if pct_change >= 0 else ""
                market_text.append(f"  {name}: Price={price}, 24h Change={direction}{pct_change:.2f}%")
        
        # Economic Calendar Highlights
        if not calendar_data.empty:
            market_text.append("\nECONOMIC CALENDAR HIGHLIGHTS:")
            # Filter for high impact events
            if 'Impact' in calendar_data.columns:
                high_impact_events = calendar_data[
                    calendar_data['Impact'].isin(['High', 'Very High'])
                ].head(5)
            else:
                high_impact_events = calendar_data.head(5)
            
            for _, row in high_impact_events.iterrows():
                event_name = row.get('Name', row.get('Event', 'N/A'))
                currency = row.get('Currency', 'N/A')
                actual = row.get('Actual', 'N/A')
                forecast = row.get('Forecast', 'N/A')
                previous = row.get('Previous', 'N/A')
                market_text.append(f"  {event_name} ({currency}): Actual={actual}, Forecast={forecast}, Previous={previous}")
        
        return "\n".join(market_text)
    
    def _create_prompt(self, market_data_text: str) -> List[Dict]:
        """Create the prompt for the LLM"""
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": (
                    f"Based on the following daily market data, provide a concise executive summary "
                    f"with 3-5 key bullet points highlighting the most important market movements and insights:\n\n"
                    f"{market_data_text}\n\n"
                    f"Provide only the final summary points without any additional explanations or formatting. "
                    f"Each point should be a concise bullet point starting with '• '."
                )
            }
        ]
        return messages
    
    def _call_llm_api(self, messages: List[Dict]) -> Optional[str]:
        """Call the Krutrim LLM API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            **self.default_params
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extract the assistant's response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                assistant_response = response_data["choices"][0]["message"]["content"]
                return assistant_response
            else:
                logger.error("No choices in LLM response")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling LLM API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in LLM API call: {e}")
            return None
    
    def _extract_bullet_points(self, llm_response: str) -> List[str]:
        """Extract bullet points from the LLM response"""
        if not llm_response:
            return []
        
        # Split into lines and extract bullet points
        lines = llm_response.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            # Look for bullet points
            if line.startswith('• ') or line.startswith('- ') or line.startswith('* '):
                # Extract the actual bullet point text
                bullet_text = line[2:].strip()  # Remove the bullet character and spaces
                if bullet_text:
                    bullet_points.append(bullet_text)
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Handle cases where there might not be a space after the bullet
                bullet_text = line[1:].strip()
                if bullet_text:
                    bullet_points.append(bullet_text)
        
        # If no bullet points found, try to split by sentences that seem like summary points
        if not bullet_points:
            # Simple heuristic: split by periods and look for capitalized sentences
            sentences = [s.strip() for s in llm_response.split('.') if s.strip()]
            for sentence in sentences[:5]:  # Take first 5 sentences
                if sentence and (sentence[0].isupper() or sentence.startswith('"')):
                    bullet_points.append(sentence + '.')
        
        return bullet_points[:5]  # Limit to 5 points
    
    def generate_executive_summary(self, indices_data: pd.DataFrame, currency_data: pd.DataFrame,
                                  commodities_data: pd.DataFrame, top_movers: pd.DataFrame,
                                  calendar_data: pd.DataFrame) -> List[str]:
        """
        Generate an AI-powered executive summary based on market data
        
        Args:
            indices_data: DataFrame with major indices data
            currency_data: DataFrame with currency data
            commodities_data: DataFrame with commodities data
            top_movers: DataFrame with top market movers
            calendar_data: DataFrame with economic calendar data
            
        Returns:
            List of bullet points representing the executive summary
        """
        try:
            # Format market data as text
            market_data_text = self._format_market_data_as_text(
                indices_data, currency_data, commodities_data, top_movers, calendar_data
            )
            
            # Create prompt
            messages = self._create_prompt(market_data_text)
            
            # Call LLM API
            llm_response = self._call_llm_api(messages)
            
            if not llm_response:
                logger.warning("Failed to get response from LLM API - using fallback summary")
                return self._get_fallback_summary(indices_data, currency_data, commodities_data, top_movers)
            
            # Extract bullet points from response
            bullet_points = self._extract_bullet_points(llm_response)
            
            if not bullet_points:
                logger.warning("Failed to extract bullet points from LLM response - using fallback summary")
                return self._get_fallback_summary(indices_data, currency_data, commodities_data, top_movers)
            
            return bullet_points
            
        except requests.exceptions.Timeout:
            logger.error("LLM API request timed out - using fallback summary")
            return self._get_fallback_summary(indices_data, currency_data, commodities_data, top_movers)
        except requests.exceptions.ConnectionError:
            logger.error("LLM API connection error - using fallback summary")
            return self._get_fallback_summary(indices_data, currency_data, commodities_data, top_movers)
        except Exception as e:
            logger.error(f"Error generating executive summary: {e} - using fallback summary")
            return self._get_fallback_summary(indices_data, currency_data, commodities_data, top_movers)
    
    def _get_fallback_summary(self, indices_data: pd.DataFrame, currency_data: pd.DataFrame,
                             commodities_data: pd.DataFrame, top_movers: pd.DataFrame) -> List[str]:
        """Generate a fallback summary if LLM fails"""
        fallback_points = [
            "⚠️ LLM EXECUTIVE SUMMARY UNAVAILABLE ⚠️",
            "Markets are currently stable with mixed sentiment.",
            "Key indices showing moderate volatility.",
            "Currency markets reflecting ongoing macroeconomic developments.",
            "Commodities sector showing divergent trends.",
            "Economic calendar highlights upcoming key events."
        ]
        return fallback_points