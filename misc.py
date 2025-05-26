import discord
import time
from time import gmtime,strftime
from discord.ext import commands
from discord import app_commands
from typing import Optional
import random
import aiohttp
from joryu import JoryuPy
import io

class Misc(commands.Cog):
    def __init__(self, bot: JoryuPy) -> None:
        self.bot = bot

    @commands.hybrid_command()
    async def help(self, ctx: commands.Context):    
        """List all of the valid commands for users."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        emb = discord.Embed(title="Misc Commands", description="""`ping` - Ping the bot, returning its current context's shard id along with the latency and uptime of the bot.\n`meme <meme>` - Display a meme through the bot, there are 24 total memes to display.\n`whois <user>` - Research about the specified user (if a user isn't specified it'll be specified to be you.)\n`avatar <user>` - Return the avatar of a specified user\n`flip` - Flips a coin\n`say` - Relays a message through the bot.\n`quotes` - Make the bot say random quotes""", color=0xFF0000)
        await ctx.send(embed=emb)

    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context):
        """Ping the bot, returning its current context's shard id along with the latency and uptime of the bot."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        latency_ms = round(self.bot.latency * 1000, 2)
        await ctx.send(f"Pong! `{latency_ms}ms`")

    @commands.hybrid_command()
    async def uptime(self, ctx: commands.Context):
        """Get the uptime of the bot."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        uptime = strftime("%Hh:%Mm:%Ss", gmtime(round(time.time() - self.bot.uptime)))    
        await ctx.send(f"Uptime: `{uptime}`")
    
    @commands.hybrid_command()
    @app_commands.describe(meme="Meme to relay")
    async def meme(self, ctx: commands.Context, meme: str):
        """Display a meme through the bot, there are 24 total memes to display."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer(ephemeral=True)
        async with aiohttp.ClientSession() as session:
            # Fetch the list of files in the GitHub folder
            async with session.get(self.bot.GITHUB_API_URL) as resp:
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
            # Optionally defer and confirm interaction response if slash command
            discord_file = discord.File(io.BytesIO(file_data), filename=chosen_file['name'])
            if ctx.interaction is not None:
                await ctx.send("Initialized your file.", ephemeral=True)
            else:
                await ctx.send("Initialized your file.", delete_after=5)
            await ctx.channel.send(file=discord_file)

    
    @commands.hybrid_command(description="Research about the specified user (if a user isn't specified it'll be specified to be you.)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(user="The member or user to display information of")
    async def whois(self, ctx: commands.Context, user: Optional[discord.Member]):
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"(`{user.global_name}`)")
        embed.add_field(name="Account Created",value=f"{user.created_at}", inline=True)
        if ctx.guild is not None:
            embed.add_field(name="Joined Server At", value=f"{user.joined_at}", inline=True)
        embed.add_field(name="Is on mobile?", value=f"{user.is_on_mobile()}", inline=True)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"ID: `{user.id}`")
        embed.color = 0xFF0000
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Return the avatar of a specified user")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(user="The member or user to return the avatar of")
    async def avatar(self, ctx: commands.Context, user: Optional[discord.Member]):
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"(`{user.global_name}`)")
        embed.set_image(url=user.avatar.url)
        embed.color = 0xFF0000
        await ctx.send(embed=embed)

    @commands.hybrid_command(name=f"{str(8)}ball")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def eightball(self, ctx: commands.Context, question: str):
        """Ask the 8ball"""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        eight_ball_yes = [
            "It is certain.",
            "Without a doubt. Or maybe with a doubt? Nah, doubt’s overrated.",
            "Yes – definitely. Ask me again after a snack.",
            "You may rely on it, unless you’re a penguin.",
            "As I see it, yes. But I’m just a bot, what do I know?",
            "Most likely. Unless the moon is made of cheese.",
            "Outlook good. Like a sunny day at the beach!",
            "Yes.",
            "Signs point to yes. Or maybe they’re just confused.",
            "Absolutely!",
            "For sure!",
            "Looks promising. Like a puppy wagging its tail!",
            "Yes, in due time. Patience, young grasshopper.",
            "Maybe. Or maybe not. The suspense!",
            "The stars say yes. Or they’re just twinkling.",
            "Chances are high. Like a kangaroo on a trampoline.",
            "Yes, but not how you expect. Plot twist!",
            "Only if you believe. Magic is real!",
            "You already know the answer. Don’t play coy.",
            "Why not? Because why not!",
            "Sure thing, champ!",
            "Yup, like a boss!",
            "You betcha!",
            "Heck yes!"
        ]

        # No-type responses
        eight_ball_no = [
            "Reply hazy, try again. My circuits are a bit fried.",
            "Ask again later. I’m busy watching cat videos.",
            "Better not tell you now. Secrets, secrets!",
            "Cannot predict now. The magic 8-ball is on vacation.",
            "Concentrate and ask again. Or just throw a coin.",
            "Don't count on it. Unless you have a unicorn.",
            "My reply is no. But hugs are free!",
            "My sources say no. They’re a bunch of jokers.",
            "Outlook not so good. Like a Monday morning.",
            "Very doubtful. Like a squirrel crossing the road.",
            "No chance. Unless you bribe me with cookies.",
            "Definitely not. Nope, nada, zip.",
            "I wouldn't bet on it. But betting on pizza is always good.",
            "Unlikely. Like a fish riding a bicycle.",
            "No, but keep trying. Persistence is key!",
            "The stars say no. They’re moody today.",
            "Chances are low. Like a turtle in a race.",
            "No, but something better awaits. Like cake.",
            "Ask your mom. She knows best.",
            "Ask your dad. He’s got the dad jokes.",
            "Absolutely not. Nope, no way, José.",
            "If you say so. I’m just a bot.",
            "Don't ask me. I’m just here for the memes.",
            "Possibly. Or possibly not.",
            "No way! Unless you’re a wizard.",
            "No, and that's final. No take backs!",
            "Ask again after coffee. Caffeine powers me.",
            "The universe says yes. Or maybe it’s just me.",
            "Nope, try again later."
        ]

        outcomes = [random.choices(eight_ball_yes)[0], random.choices(eight_ball_no)[0]]
        probabilities = [0.5, 0.5]  # Sum must be 1.0

        # Use random.choices to select one outcome based on probabilities
        result = random.choices(outcomes, weights=probabilities, k=1)[0]
        if ctx.interaction is None:
            await ctx.message.reply(f"{result}")
        else:
            await ctx.send(f"{result}")

    @commands.hybrid_command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def flip(self, ctx: commands.Context):
        """Flips a coin."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        funny_fall_reactions = ['Oops, it fell :/', 'AHHH IT FELL', 'It fell down below the couch :(', 'It fucking fell!']
        outcomes = ['Heads!', 'Tails!', random.choices(funny_fall_reactions)[0]]
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
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        await ctx.send(message)

    @commands.hybrid_command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def quotes(self, ctx: commands.Context):
        """Make the bot say random quotes"""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
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

        stuff = random.choices(population=yakuza_quotes, k=1)[0]
        if ctx.interaction is None:
            await ctx.message.reply(f"{stuff}")
        else:
            await ctx.send(f"{stuff}")
    

async def setup(bot: JoryuPy):
    await bot.add_cog(Misc(bot))
