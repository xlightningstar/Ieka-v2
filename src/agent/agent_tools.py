import requests
from typing import Any, Dict
from src.config import Config
import json


class ToolExecutor:
    """Executes tools based on agent decisions."""
    
    @staticmethod
    def search(query: str) -> str:
        """Perform a web search using DuckDuckGo API.
        
        Args:
            query: The search query
            
        Returns:
            Search results as a formatted string
        """
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            results = []
            
            # Add abstract if available
            if data.get("Abstract"):
                results.append(f"Summary: {data['Abstract']}")
            
            # Add related topics
            if data.get("RelatedTopics"):
                results.append("\nRelated Information:")
                for i, topic in enumerate(data["RelatedTopics"][:3], 1):
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append(f"{i}. {topic['Text']}")
            
            if not results:
                return f"No detailed results found for '{query}'. Try a different search term."
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    @staticmethod
    def calculate(expression: str) -> str:
        """Safely evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The result of the calculation
        """
        try:
            # Remove any potentially dangerous characters
            allowed_chars = "0123456789+-*/(). "
            cleaned = "".join(c for c in expression if c in allowed_chars)
            
            if not cleaned:
                return "Invalid expression"
            
            # Safely evaluate the expression
            result = eval(cleaned, {"__builtins__": {}}, {})
            return f"Result: {result}"
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Calculation failed: {str(e)}"
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        tools = {
            "search": self.search,
            "calculate": self.calculate
        }
        
        if tool_name not in tools:
            return f"Unknown tool: {tool_name}"
        
        try:
            return tools[tool_name](**kwargs)
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
            # Try to extract JSON from the response
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