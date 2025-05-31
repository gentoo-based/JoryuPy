import mintegration
import asyncio
import random
from time import time
from discord import activity, Status, Message, Guild
from discord.ext import commands
from database import execute_query


async def get_prefix(bot, message: Message):
    if message.guild:
        prefix = await execute_query(
            "SELECT prefix FROM prefixes WHERE guild_id = ?", (message.guild.id,)
        )
        if prefix is None:
            return "td!"
        return prefix[0]
    else:
        return "td!"


class JoryuPy(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(help_command=None, *args, **kwargs)
        self.uptime = time()
        self.GITHUB_API_URL = (
            "https://api.github.com/repos/gentoo-based/memes/contents/memes"
        )

    async def setup_hook(self):
        """A once-only event handler"""

        # Create the tables in the database that is needed.
        await execute_query(
            "CREATE TABLE IF NOT EXISTS prefixes ( guild_id INTEGER PRIMARY KEY, prefix VARCHAR(10) NOT NULL DEFAULT 'td!' )",
            None,
        )
        await execute_query(
            "CREATE TABLE IF NOT EXISTS warnings (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER, user_id INTEGER, warns INTEGER, reason TEXT, moderator_id INTEGER)",
            None,
        )

        # Load the extensions/cogs.
        await self.load_extension("plugins.misc")
        await self.load_extension("plugins.moderation")
        await self.load_extension("plugins.owner")

        # Sync the command tree to keep all of the interaction commands up to date.

    async def on_ready(self):
        # Sync the command tree to keep all of the interaction commands up to date.
        await self.tree.sync()

        # Return that the bot has loaded
        print(
            f"{self.user.name}#{
                self.user.discriminator
            } has successfully entered the Discord API Gateway with {
                self.shard_count
            } Shards."
        )

    async def on_shard_ready(self, shard_id):
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
                "You can do better, Ichiban Kasuga. Everyone has things or people they treasure in life. You get that, don't you? Yeah, well I do too.",
            ]
            randomizedActivity = activity.CustomActivity(
                name=random.choice(kiryu_quotes)
            )
            await self.change_presence(
                activity=randomizedActivity, status=Status.online, shard_id=shard_id
            )
            await asyncio.sleep(random.randint(25, 50))

    async def on_guild_join(self, guild: Guild):
        """On guild join event handler"""

        # Insert the default prefix onto prefixes table in the database
        await execute_query(
            "INSERT INTO prefixes (guild_id, prefix) VALUES (?, ?)", (guild.id, "td!")
        )
