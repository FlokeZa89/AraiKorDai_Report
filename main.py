import interactions
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = interactions.Client(TOKEN)


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await interactions.load_extension(f'cogs.{filename[:-3]}')

async def main():
     await load()
     await bot.start()

asyncio.run(main())
