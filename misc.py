import discord
import time
import os
from time import gmtime,strftime
from discord.ext import commands
from discord import app_commands
import typing
from typing import Optional
import random
import aiohttp
import io

GITHUB_API_URL = "https://api.github.com/repos/gentoo-based/memes/contents/memes"

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot | commands.AutoShardedBot, uptime: int) -> None:
        self.bot = bot
        self.uptime = uptime

    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context):
        """Ping the bot, returning its current context's shard id along with the latency and uptime of the bot."""
        uptime = strftime("%Hh:%Mm:%Ss", gmtime(round(time.time() - self.uptime)))
        await ctx.send(f"Pong!\nShard ID: {ctx.guild.shard_id}\nLatency: {round(self.bot.get_shard(ctx.guild.shard_id).latency)}ms\nUptime: {uptime}")
    
    @commands.hybrid_command(description="Display a meme through the bot, there are 24 total memes to display.")
    @app_commands.describe(meme="The meme to relay through the bot")
    async def meme(self, ctx: commands.Context, meme: typing.Literal["real_kiryu_kazuma_yakuza", "aworldiwithnoanswers", "Bait", "bakamitai", "beverageiron", "beverageprowler", "brb", "breakerstyle", "breakingzalaw", "bwird", "chinaairlines", "chinese", "fredbeardance", "friday", "gun", "hacer_man", "haruka", "insanity", "wearetheyakuza4", "kill_ltg", "tys", "kiryuintro", "prowler", "stfu", "myhonestreaction"]):

        async with aiohttp.ClientSession() as session:
            # Fetch the list of files in the GitHub folder
            async with session.get(GITHUB_API_URL) as resp:
                if resp.status != 200:
                    await ctx.send("Could not fetch memes from GitHub repository.")
                    return
                files = await resp.json()

            # Filter image/video files only
            valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".mp4", ".mov", ".mp5")
            media_files = [file for file in files if file['name'].lower().endswith(valid_extensions)]

            if not media_files:
                await ctx.send("No meme files found in the GitHub repository folder.")
                return

            # If user specified a meme name, try to find it in the files
            chosen_file = None
            if meme:
                # Case-insensitive match: check if meme string is in file name (without extension)
                for file in media_files:
                    # Remove extension and lower case for matching
                    name_without_ext = file['name'].rsplit('.', 1)[0].lower()
                    if meme.lower() == name_without_ext:
                        chosen_file = file
                        break
                if not chosen_file:
                    await ctx.send(f"Meme '{meme}' not found in the repository.")
                    return
            else:
                # Pick a random meme if none specified
                chosen_file = random.choice(media_files)

            # Download the chosen file
            async with session.get(chosen_file['download_url']) as file_resp:
                if file_resp.status != 200:
                    await ctx.send("Failed to download the meme image/video.")
                    return
                file_data = await file_resp.read()

            # Send the file to Discord
            discord_file = discord.File(io.BytesIO(file_data), filename=chosen_file['name'])
            await ctx.send(file=discord_file)

            # Optionally defer and confirm interaction response if slash command
            if ctx.interaction is not None:
                await ctx.defer(ephemeral=True)
                await ctx.send("Sent your file.")
            else:
                await ctx.send("Sent your file.", delete_after=5)
    
    @commands.hybrid_command(description="Research about the specified user (if a user isn't specified it'll be specified to be you.)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(user="The member or user to display information of")
    async def whois(self, ctx: commands.Context, user: Optional[discord.Member]):
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"{user.mention} (`{user.global_name}`)")
        embed.add_field(name="Account Created",value=f"{user.created_at}", inline=True)
        if ctx.guild is not None:
            embed.add_field(name="Joined Server At", value=f"{user.joined_at}", inline=True)
        embed.add_field(name="Is on mobile?", value=f"{user.is_on_mobile()}", inline=True)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"ID: `{user.id}`")
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Return the avatar of a specified user")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(user="The member or user to return the avatar of")
    async def avatar(self, ctx: commands.Context, user: Optional[discord.Member]):
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"{user.mention} (`{user.global_name}`)")
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def flip(self, ctx: commands.Context):
        """Flips a coin."""

        funny_fall_reactions = ['Oops, it fell :/', 'AHHH IT FELL', 'It fell down below the couch :(', 'It fucking fell!']
        outcomes = ['Heads!', 'Tails!', random.choices(funny_fall_reactions)]
        probabilities = [0.49995, 0.49995, 0.0001]  # Sum must be 1.0

        # Use random.choices to select one outcome based on probabilities
        result = random.choices(outcomes, weights=probabilities, k=1)[0]
        if ctx.interaction is None:
            await ctx.message.reply(f"{result}")
        else:
            await ctx.send(f"{result}")

    @commands.hybrid_command(description="Relays a message through the bot.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(message="Message to relay through the bot.")
    async def say(self, ctx: commands.Context, message: str):
        await ctx.send(message)

    @commands.hybrid_command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def quotes(self, ctx: commands.Context):
        """Make the bot say random quotes"""

        yakuza_quotes = [
            # Kiryu Kazuma
            "I’m the Dragon of Dojima... but today I’m just the guy who forgot how to dragon.",
            "I tried to punch a vending machine once. It didn’t sell me any snacks, but I got a free concussion.",
            "If I had a yen for every time someone underestimated me, I’d have enough to buy a small island... or at least a really fancy bento.",
            "I don’t always fight yakuza, but when I do, I prefer to do it while wearing slippers.",
            "I once challenged a cat to a staring contest. The cat blinked first. I’m still not over it.",

            # Goro Majima
            "I’m the Mad Dog of Shimano, baby! - Goro Majima",
            "You think you can handle the madness? I’m just getting started! - Goro Majima",
            "I don’t go crazy, I am crazy! - Goro Majima",
            "Come on! Show me what you got, punk! - Goro Majima",
            "I’m like a tornado in a teacup-small, but deadly! - Goro Majima",
            "You better watch your back, or I’ll be there with a smile and a baseball bat! - Goro Majima",
            "I’m the wild card in this deck, and I’m about to reshuffle! - Goro Majima",
            "Life’s a party, and I’m the one who crashes it! - Goro Majima",

            # Ichiban Kasuga
            "I’m not just a hero, I’m the hero who eats all the snacks! - Ichiban Kasuga",
            "When life knocks you down, get up and punch it back twice as hard! - Ichiban Kasuga",
            "I don’t just believe in myself-I believe in my friends and my unlimited stamina! - Ichiban Kasuga",
            "If you’re going to be a legend, you might as well be a funny one! - Ichiban Kasuga",
            "I’m the Dragon of Yokohama, and I’m here to party and save the day! - Ichiban Kasuga",

            # Haruka Sawamura
            "Big brother, please don’t fight again... but if you do, bring me a souvenir! - Haruka Sawamura",
            "I’m not just cute, I’m cute with a black belt in sass! - Haruka Sawamura",
            "If you want to win, you have to believe-and maybe bring some snacks. - Haruka Sawamura",

            # Shun Akiyama
            "Money can’t buy happiness, but it can buy a really nice car to cry in. - Akiyama",
            "I’m the loan shark with a heart of gold... and a wallet full of IOUs. - Akiyama",
            "If you want to survive in this city, you gotta have style and a good haircut. - Akiyama",

            # Taiga Saejima
            "I’m a big guy with a big heart... and an even bigger hammer. - Saejima",
            "You mess with my friends, you’ll meet my fists. - Saejima",
            "I don’t need words to solve problems. Just watch the hammer do the talking. - Saejima",

            # Ryuji Goda
            "I’m the Dragon of Kansai, and I’m here to steal your spotlight and your lunch. - Ryuji Goda",
            "You want a fight? I’m the storm you didn’t see coming. - Ryuji Goda",
            "I don’t just roar-I make earthquakes. - Ryuji Goda",

            # Other iconic funny moments
            "I’m not lost, I’m just on a quest to find the world’s best cup of coffee. It’s a dangerous mission.",
            "If life gives you lemons, squeeze them into your enemy’s eyes and run like hell.",
            "I tried karaoke once. The microphone is still recovering from the trauma.",
            "Why punch when you can politely ask your opponent to reconsider their life choices?",
        ]

        stuff = random.choices(yakuza_quotes)
        if ctx.interaction is None:
            await ctx.message.reply(f"{stuff}")
        else:
            await ctx.send(f"{stuff}")
    

async def setup(bot: commands.Bot | commands.AutoShardedBot):
    await bot.add_cog(Misc(bot, time.time()))