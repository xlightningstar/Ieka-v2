import requests
from typing import Any, Dict
from src.config import Config
from src.agent.web_scraper import get_scraper
from src.agent.api_clients import TfLClient, ONSClient, YahooFinanceClient
import json
import asyncio


class ToolExecutor:
    """Executes tools based on agent decisions."""
    
    def __init__(self):
        self.tfl = TfLClient()
        self.ons = ONSClient()
        self.yahoo = YahooFinanceClient()
    
    # ============= WEB & SEARCH TOOLS =============
    
    @staticmethod
    async def web_search(query: str) -> str:
        """Perform a web search or fetch a specific URL using headless browser.
        
        Args:
            query: Search query or URL (http://... or https://...)
            
        Returns:
            Search results or page content
        """
        scraper = get_scraper()
        return await scraper.search_web(query)

    
    @staticmethod
    async def get_weather(location: str = "London") -> str:
        """Get current weather for a location.
        
        Args:
            location: City or location name (default: London)
            
        Returns:
            Current weather information
        """
        scraper = get_scraper()
        return await scraper.get_weather(location)
    
    @staticmethod
    def calculate(expression: str) -> str:
        """Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression (e.g., "25 * 48 + 100")
            
        Returns:
            Calculation result
        """
        try:
            allowed_chars = "0123456789+-*/(). "
            cleaned = "".join(c for c in expression if c in allowed_chars)
            
            if not cleaned:
                return "Invalid expression"
            
            result = eval(cleaned, {"__builtins__": {}}, {})
            return f"Result: {result}"
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Calculation failed: {str(e)}"
    
    # ============= TRANSPORT (TfL) TOOLS =============
    
    def tfl_line_status(self, line: str = None) -> str:
        """Get Transport for London tube line status.
        
        Args:
            line: Specific line name (e.g., 'victoria', 'central', 'northern') 
                  or leave empty for all lines
            
        Returns:
            Line status information
        """
        return self.tfl.get_line_status(line)
    
    def tfl_journey_plan(self, from_location: str, to_location: str) -> str:
        """Plan a journey in London using TfL.
        
        Args:
            from_location: Starting point (station name or postcode)
            to_location: Destination (station name or postcode)
            
        Returns:
            Journey plan with steps and duration
        """
        return self.tfl.plan_journey(from_location, to_location)
    
    # ============= STATISTICS (ONS) TOOLS =============
    
    def ons_search(self, query: str) -> str:
        """Search UK Office for National Statistics datasets.
        
        Args:
            query: Search term (e.g., 'population', 'employment', 'gdp')
            
        Returns:
            Available datasets matching the query
        """
        return self.ons.search_datasets(query)
    
    def ons_population(self) -> str:
        """Get UK population statistics.
        
        Returns:
            Population statistics information
        """
        return self.ons.get_population_stats()
    
    # ============= FINANCE (Yahoo Finance) TOOLS =============
    
    def stock_price(self, symbol: str) -> str:
        """Get current stock price.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'GOOGL', 'MSFT', 'TSLA')
            
        Returns:
            Current price, change, and previous close
        """
        return self.yahoo.get_stock_price(symbol)
    
    def crypto_price(self, symbol: str) -> str:
        """Get current cryptocurrency price.
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH', 'BTC-USD')
            
        Returns:
            Current crypto price and change
        """
        return self.yahoo.get_crypto_price(symbol)
    
    def search_stock(self, company_name: str) -> str:
        """Search for stock ticker by company name.
        
        Args:
            company_name: Company name (e.g., 'Apple', 'Microsoft', 'Tesla')
            
        Returns:
            List of matching tickers
        """
        return self.yahoo.search_ticker(company_name)
    
    # ============= TOOL EXECUTION =============
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        tools = {
            # Web & Search
            "web_search": self.web_search,
            "get_weather": self.get_weather,
            "calculate": self.calculate,
            
            # Transport
            "tfl_line_status": self.tfl_line_status,
            "tfl_journey_plan": self.tfl_journey_plan,
            
            # Statistics
            "ons_search": self.ons_search,
            "ons_population": self.ons_population,
            
            # Finance
            "stock_price": self.stock_price,
            "crypto_price": self.crypto_price,
            "search_stock": self.search_stock,
        }
        
        if tool_name not in tools:
            return f"Unknown tool: {tool_name}"
        
        try:
            tool = tools[tool_name]
            if asyncio.iscoroutinefunction(tool):
                return await tool(**kwargs)
            else:
                return tool(**kwargs)
        except Exception as e:
            return f"Tool execution failed: {str(e)}"


class ToolDefinitions:
    """Defines available tools for the agent."""

    @staticmethod
    def parse_tool_request(response: str) -> Dict[str, Any]:
        """Parse the agent's tool request.
        
        Args:
            response: The agent's response
            
        Returns:
            Dictionary with tool name and arguments
        """
        try:
            response = response.strip()
            
            # Handle markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else ""
            
            data = json.loads(response)
            
            return {
                "tool": data.get("tool", "none"),
                "args": data.get("args", {})
            }
            
        except json.JSONDecodeError:
            return {"tool": "none", "args": {}}