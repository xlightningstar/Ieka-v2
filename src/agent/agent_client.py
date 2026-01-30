import requests
from src.settings import LLM_API_KEY
from src.config import Config
from src.agent.agent_tools import ToolDefinitions, ToolExecutor
from typing import Dict, List


class AgentClient:
    """Agent that decides which tools to use and manages tool execution."""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        self.tool_executor = ToolExecutor()
        self.tool_definitions = ToolDefinitions()
        self.memory = {}  # Store information across tool calls

    def _load_system_context(self, filepath: str = Config.AGENT_TOOLS_CONTEXT_FILEPATH) -> str:
        """Load system context from file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using empty system context.")
            return ""
    
    def _build_agent_prompt(self, user_message: str, history: List[Dict] = None) -> str:
        """Build a prompt for the agent to decide which tools to use.
        
        Args:
            user_message: The current user message
            history: Conversation history
            
        Returns:
            Formatted prompt for the agent
        """
        prompt_parts = [
            "You are an AI agent that decides which tools to use to help answer user queries.",
            "",
            self._load_system_context(Config.AGENT_TOOLS_CONTEXT_FILEPATH),
            "",
            "Analyze the following user message and determine if any tools are needed:",
            f"User message: {user_message}",
        ]
        
        # Add memory if available
        if self.memory:
            prompt_parts.insert(3, f"Previous tool results: {self.memory}")
            prompt_parts.insert(4, "")
        
        return "\n".join(prompt_parts)
    
    def _call_llm(self, messages: List[Dict]) -> str:
        """Call the LLM API.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            LLM response text
        """
        payload = {
            "model": Config.MODEL,
            "messages": messages
        }
        
        response = requests.post(Config.API_URL, headers=self.headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def process_request(self, user_message: str, history: List[Dict] = None) -> Dict:
        """Process a user request and execute any necessary tools.
        
        Args:
            user_message: The user's message
            history: Conversation history
            
        Returns:
            Dictionary with tool results and updated memory
        """
        # Clear previous memory for new request
        self.memory = {}
        
        max_iterations = 1
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Build prompt for agent
            agent_prompt = self._build_agent_prompt(user_message, history)
            
            # Ask agent what to do
            messages = [
                {"role": "system", "content": "You are a helpful AI agent that uses tools to answer questions."},
                {"role": "user", "content": agent_prompt}
            ]
            
            agent_response = self._call_llm(messages)
            
            # Parse tool request
            tool_request = self.tool_definitions.parse_tool_request(agent_response)
            
            # If no tool needed, we're done
            if tool_request["tool"] == "none":
                break
            
            # Execute the tool
            tool_name = tool_request["tool"]
            tool_args = tool_request["args"]
            
            result = await self.tool_executor.execute_tool(tool_name, **tool_args)
            
            # Store result in memory
            self.memory[tool_name] = {
                "args": tool_args,
                "result": result
            }
            
            # Check if we should continue (for multi-step tasks)
            # For now, we'll stop after one tool execution
            break
        
        return {
            "tool_results": self.memory,
            "iterations": iteration
        }
    
    def get_memory_summary(self) -> str:
        """Get a formatted summary of tool execution results.
        
        Returns:
            Formatted string of tool results
        """
        if not self.memory:
            return ""
        
        summary_parts = ["Tool Execution Results:"]
        
        for tool_name, data in self.memory.items():
            summary_parts.append(f"\n{tool_name.upper()}:")
            if "args" in data:
                summary_parts.append(f"  Arguments: {data['args']}")
            if "result" in data:
                summary_parts.append(f"  Result: {data['result']}")
        
        return "\n".join(summary_parts)