import requests
from typing import Dict, List, Optional
from datetime import datetime


class TfLClient:
    """Transport for London API client."""
    
    BASE_URL = "https://api.tfl.gov.uk"
    
    @staticmethod
    def get_line_status(line: Optional[str] = None) -> str:
        """Get status of TfL lines.
        
        Args:
            line: Specific line name (e.g., 'victoria', 'central') or None for all
            
        Returns:
            Line status information
        """
        try:
            if line:
                url = f"{TfLClient.BASE_URL}/Line/{line}/Status"
            else:
                url = f"{TfLClient.BASE_URL}/Line/Mode/tube/Status"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data:
                line_name = item.get('name', 'Unknown')
                statuses = item.get('lineStatuses', [])
                
                if statuses:
                    status = statuses[0].get('statusSeverityDescription', 'Unknown')
                    reason = statuses[0].get('reason', '')
                    
                    result_text = f"{line_name}: {status}"
                    if reason:
                        result_text += f" - {reason}"
                    results.append(result_text)
            
            return "\n".join(results) if results else "No status information available"
            
        except Exception as e:
            return f"TfL status check failed: {str(e)}"
    
    @staticmethod
    def plan_journey(from_location: str, to_location: str) -> str:
        """Plan a journey between two locations.
        
        Args:
            from_location: Starting location
            to_location: Destination
            
        Returns:
            Journey plan information
        """
        try:
            url = f"{TfLClient.BASE_URL}/Journey/JourneyResults/{from_location}/to/{to_location}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            journeys = data.get('journeys', [])
            
            if not journeys:
                return "No journey found"
            
            # Get the first journey option
            journey = journeys[0]
            duration = journey.get('duration', 0)
            
            results = [f"Journey Duration: {duration} minutes\n"]
            
            legs = journey.get('legs', [])
            for i, leg in enumerate(legs, 1):
                mode = leg.get('mode', {}).get('name', 'Unknown')
                instruction = leg.get('instruction', {}).get('summary', '')
                duration_leg = leg.get('duration', 0)
                
                results.append(f"Step {i}: {instruction} ({mode}, {duration_leg} min)")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Journey planning failed: {str(e)}"


class ONSClient:
    """Office for National Statistics API client."""
    
    BASE_URL = "https://api.beta.ons.gov.uk/v1"
    
    @staticmethod
    def search_datasets(query: str) -> str:
        """Search for ONS datasets.
        
        Args:
            query: Search query
            
        Returns:
            Dataset information
        """
        try:
            url = f"{ONSClient.BASE_URL}/datasets"
            params = {"q": query}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            
            if not items:
                return f"No datasets found for '{query}'"
            
            results = []
            for i, item in enumerate(items[:5], 1):
                title = item.get('title', 'Unknown')
                description = item.get('description', 'No description')
                
                results.append(f"{i}. {title}\n   {description[:150]}...")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"ONS search failed: {str(e)}"
    
    @staticmethod
    def get_population_stats() -> str:
        """Get UK population statistics.
        
        Returns:
            Population statistics
        """
        try:
            # This is a simplified example - ONS API structure is complex
            # In practice, you'd need to know specific dataset IDs
            return "Population data available through ONS datasets. Use search_datasets('population') for specific datasets."
            
        except Exception as e:
            return f"Failed to get population stats: {str(e)}"


class YahooFinanceClient:
    """Yahoo Finance API client (using unofficial API)."""
    
    @staticmethod
    def get_stock_price(symbol: str) -> str:
        """Get current stock price.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            
        Returns:
            Stock price information
        """
        try:
            # Using Yahoo Finance query API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "interval": "1d",
                "range": "1d"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get('chart', {}).get('result', [])
            if not result:
                return f"No data found for symbol '{symbol}'"
            
            meta = result[0].get('meta', {})
            current_price = meta.get('regularMarketPrice', 'N/A')
            previous_close = meta.get('previousClose', 'N/A')
            currency = meta.get('currency', 'USD')
            
            if current_price != 'N/A' and previous_close != 'N/A':
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
                
                return (f"{symbol}: {currency} {current_price:.2f}\n"
                       f"Change: {change:+.2f} ({change_percent:+.2f}%)\n"
                       f"Previous Close: {previous_close:.2f}")
            else:
                return f"{symbol}: {currency} {current_price}"
            
        except Exception as e:
            return f"Stock price fetch failed: {str(e)}"
    
    @staticmethod
    def get_crypto_price(symbol: str) -> str:
        """Get current cryptocurrency price.
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC-USD', 'ETH-USD')
            
        Returns:
            Crypto price information
        """
        try:
            # Ensure symbol has -USD suffix if not provided
            if '-' not in symbol:
                symbol = f"{symbol}-USD"
            
            return YahooFinanceClient.get_stock_price(symbol)
            
        except Exception as e:
            return f"Crypto price fetch failed: {str(e)}"
    
    @staticmethod
    def search_ticker(company_name: str) -> str:
        """Search for a stock ticker symbol by company name.
        
        Args:
            company_name: Company name to search
            
        Returns:
            Ticker information
        """
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {"q": company_name}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            quotes = data.get('quotes', [])
            
            if not quotes:
                return f"No ticker found for '{company_name}'"
            
            results = []
            for i, quote in enumerate(quotes[:5], 1):
                symbol = quote.get('symbol', 'N/A')
                name = quote.get('longname', quote.get('shortname', 'Unknown'))
                exchange = quote.get('exchange', 'N/A')
                
                results.append(f"{i}. {symbol} - {name} ({exchange})")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Ticker search failed: {str(e)}"