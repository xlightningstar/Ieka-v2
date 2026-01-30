import discord
import asyncio
from src.chatbot import ChatbotClient
from src.agent import AgentClient
from src.settings import BOT_API_KEY
from src.config import Config
from src.conversation_history import ConversationHistory

class DiscordBot:
    """Main Discord bot class."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.client = discord.Client(intents=intents)
        self.llm = ChatbotClient()
        self.agent = AgentClient()
        self.history = ConversationHistory()
        
        self.request_queue = asyncio.Queue(maxsize=Config.QUEUE_MAX_SIZE)
        self.processing_lock = asyncio.Lock()
        
        self._register_events()
    
    def _register_events(self):
        """Register Discord event handlers."""
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"Logged in as {self.client.user}")
        asyncio.create_task(self.queue_worker())
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if message starts with command prefix
        if not message.content.startswith("!"):
            return
        
        command_content = message.content[1:].strip()
        
        # Handle special commands
        if command_content.lower() == "clear":
            self.history.clear_history(message.channel.id)
            await message.reply("🗑️ Conversation history cleared!")
            return
        
        # Add user message to history
        self.history.add_message(
            message.channel.id,
            message.author.name,
            command_content
        )
        
        # Check if queue is full
        if self.request_queue.full():
            await message.reply("please dont spam ;-;")
            return
        
        # Add request to queue
        await self.request_queue.put((message, command_content))
    
    async def queue_worker(self):
        """Process messages from the queue."""
        while True:
            message, user_prompt = await self.request_queue.get()
            
            async with self.processing_lock:
                try:
                    # Get conversation history
                    history = self.history.get_history(message.channel.id)
                    
                    # Step 1: Agent decides and executes tools
                    await self.agent.process_request(user_prompt, history)
                    
                    # Step 2: Add tool results to history if any tools were used
                    tool_summary = self.agent.get_memory_summary()
                    if tool_summary:
                        # Add tool results as a system message for context
                        self.history.add_message(
                            message.channel.id,
                            "System",
                            f"[Tool Results]\n{tool_summary}",
                            is_bot=True
                        )
                    print(tool_summary)
                    
                    # Step 3: Get updated history with tool results
                    updated_history = self.history.get_history(message.channel.id)
                    
                    # Step 4: Generate final response using main LLM
                    response = await asyncio.to_thread(
                        self.llm.get_response,
                        updated_history
                    )
                    
                    # Add bot response to history
                    self.history.add_message(
                        message.channel.id,
                        self.client.user.name,
                        response,
                        is_bot=True
                    )
                    
                    # Send response (respecting Discord's 2000 char limit)
                    await message.reply(response[:2000])
                
                except Exception as e:
                    await message.reply("❌ Something went wrong.")
                    print(f"Error processing message: {e}")
                    import traceback
                    traceback.print_exc()
                
                finally:
                    await asyncio.sleep(Config.COOLDOWN_SECONDS)
                    self.request_queue.task_done()
    
    def run(self):
        """Start the bot."""
        self.client.run(BOT_API_KEY)