import discord
import asyncio
from llm_client import LLMClient
from settings import BOT_API_KEY

INTENTS = discord.Intents.default()
INTENTS.message_content = True

client = discord.Client(intents=INTENTS)
llm = LLMClient()

QUEUE_MAX_SIZE = 1
COOLDOWN_SECONDS = 0

request_queue = asyncio.Queue(maxsize=QUEUE_MAX_SIZE)
processing_lock = asyncio.Lock()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    asyncio.create_task(queue_worker())


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith("!"):
        return

    prompt = f"User {message.author.name}: {message.content[len('!'):].strip()}"

    if request_queue.full():
        await message.reply("please dont spam ;-;")
        return

    await request_queue.put((message, prompt))


async def queue_worker():
    while True:
        message, prompt = await request_queue.get()

        async with processing_lock:
            try:
                #print(prompt)
                response = await asyncio.to_thread(
                    llm.get_response, prompt
                )

                await message.reply(response[:2000])  # Discord limit

            except Exception as e:
                await message.reply("❌ Something went wrong.")
                print(e)

            finally:
                await asyncio.sleep(COOLDOWN_SECONDS)
                request_queue.task_done()

if __name__ == "__main__":
    client.run(BOT_API_KEY)
