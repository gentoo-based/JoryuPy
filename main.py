#!/usr/bin/env python

from os import getenv

from discord import Intents
from dotenv import load_dotenv

from joryu import JoryuPy, get_prefix

load_dotenv()

TOKEN = getenv("DISCORD_TOKEN")

JoryuPy(intents=Intents.all(), command_prefix=get_prefix).run(TOKEN)
