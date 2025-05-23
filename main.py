from joryu import JoryuPy, get_prefix
from dotenv import load_dotenv
from discord import Intents
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

JoryuPy(intents=Intents.all(), command_prefix=get_prefix).run(TOKEN)
