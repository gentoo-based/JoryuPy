#!/usr/bin/env python

from os import getenv
from asyncio import run
from discord import Intents
from dotenv import load_dotenv
from discord.utils import setup_logging
from joryu import JoryuPy, get_prefix

load_dotenv()

TOKEN = getenv("DISCORD_TOKEN")


async def main():
    async with JoryuPy(intents=Intents.all(), command_prefix=get_prefix) as bot:
        setup_logging()
        await bot.start(TOKEN)


run(main=main())
