import os
import discord_ios
import discord
import asyncio
import random
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or("td!"), intents=intents, shard_count=32)
bot.remove_command("help")

@bot.listen()
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user.name}#{bot.user.discriminator} has successfully entered the Discord API Gateway.")

@bot.listen()
async def on_shard_ready(shard_id):
    while True:
        kiryu_quotes = [
            "Some are born with talent, and some aren't. That's true. But that said... Those with talent never make it through talent alone. You have to overcome.",
            "Life is like a trampoline. The lower you fall, the higher you go.",
            "Even if you cast yourself to hell, the burn's a lot easier to bear so long as you choose it.",
            "You have ties to this world, they don't disappear when you turn your back.",
            "You lay one goddamn finger on Makoto Makimura... And I'll bury the Tojo Clan. I'll crush it down to the last man. This I swear to you!",
            "The man who gets beat down isn't the loser. The guy who can't tough it out to the end, he's the one who loses.",
            "I'll buy the magazine for you but you must make sure no one can find it.",
            "Your life is yours to live. You shouldn't have to justify it to anyone else.",
            "If you always avoid things that are difficult, you'll never be able to grow. Owning up to your weaknesses and facing them head-on is the best way to improve.",
            "Any title a man draws up for himself isn't worth wearing.",
            "I try not to stereotype people into certain roles. A person's real value is on the inside.",
            "Complaining won't get it done any quicker.",
            "If you're so desperate to write yourself a title, write it in your own blood not others'.",
            "The treasure you're after is right up there. I'm the dragon guarding it. Defeat me.",
            "Some people have to disappear for the sake of what they treasure.",
            "When you don't pay your debts, I'm what you get.",
            "You walk alone in the dark long enough, it starts to feel like the light'll never come. You stop wanting to even take the next step. But there's not a person in this world who knows what's waiting down the road. All we can do is choose. Stand still and cry... or make the choice to take the next step. You pick whichever one feels right to you. I can get you as far as the starting line.",
            "You talk a lot of [expletive] but can you back it up?",
            "I don't die so easily.",
            "You can do better, Ichiban Kasuga. Everyone has things or people they treasure in life. You get that, don't you? Yeah, well I do too."
        ]
        activity = discord.activity.CustomActivity(name=random.choice(kiryu_quotes))
        await bot.change_presence(activity=activity, status=discord.Status.online, shard_id=shard_id)
        await asyncio.sleep(50)

async def load_cogs():
    await bot.load_extension("misc")
    await bot.load_extension("moderation")
    await bot.load_extension("owner")

asyncio.run(load_cogs())

bot.run(DISCORD_TOKEN)