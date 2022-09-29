import os
import discord
from discord.ext.commands import Bot
import logging
from libs import config
import asyncio

logger = logging.getLogger(__name__)


def load_cogs(bot):
    for cog in os.listdir("cogs"):
        if not os.path.isfile("cogs\\"+cog):
            continue
        logger.info(f"Carregando cog {cog}")
        asyncio.run(bot.load_extension(f"cogs.{cog[:-3]}"))

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = Bot("!", intents=intents)
    load_cogs(client)
    client.run(config.auth.get("token"))
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()