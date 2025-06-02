from discord.ext import commands
from discord import app_commands, Member
from typing import Optional
from database import execute_query
from joryu import JoryuPy
from datetime import timedelta


@app_commands.guild_only()
class Moderation(commands.Cog):
    def __init__(self, bot: JoryuPy) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Ban a user")
    @app_commands.describe(
        user="User to Ban", reason="Reason why you wanted to ban a specified user"
    )
    async def ban(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer()
        guild = ctx.guild
        await guild.ban(user=user, reason=reason)
        await ctx.send(f"Banned {user} for reason: {reason}")

    @commands.hybrid_command(description="Unban a user")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(
        user="User to unban", reason="Reason why you wanted to unban a specified user"
    )
    async def unban(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        guild = ctx.guild
        await guild.unban(user=user, reason=reason)
        await ctx.send(f"Unbanned {user} for reason: {reason}")

    @commands.hybrid_command(description="Time out a user")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(
        user="User to time out",
        reason="Reason why you wanted to time out a specified user",
    )
    async def timeout(
        self, ctx: commands.Context, user: Member, time: str, reason: Optional[str]
    ):
        if "s" in time:
            await user.timeout(
                timedelta(seconds=float(time.split("s")[0])), reason=reason
            )
        elif "m" in time:
            await user.timeout(
                timedelta(minutes=float(time.split("m")[0])), reason=reason
            )
        elif "h" in time:
            await user.timeout(
                timedelta(hours=float(time.split("h")[0])), reason=reason
            )
        elif "d" in time:
            await user.timeout(timedelta(days=float(time.split("d")[0])), reason=reason)
        await ctx.send(f"Muted {user} until {time} for reason: {reason}")

    @commands.hybrid_command(description="kick a user")
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(
        user="User to kick", reason="Reason why you wanted to kick a specified user"
    )
    async def kick(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        guild = ctx.guild
        await guild.kick(user=user, reason=reason)
        await ctx.send(f"Kicked {user} for reason: {reason}")

    @commands.hybrid_command(description="Warn a user")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to warn", reason="Warn a specific user")
    async def warn(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        awarns = await execute_query(
            "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, user.id),
        )
        warns = int(awarns[-1][3]) + 1 if awarns else 1
        await execute_query(
            "INSERT INTO warnings (guild_id, user_id, warns, reason, moderator_id) VALUES (?, ?, ?, ?, ?)",
            (ctx.guild.id, user.id, warns, reason, ctx.author.id),
        )
        await ctx.send(f"Warned {user} with reason: {reason}")

    @commands.hybrid_command(description="Get the warns of a user")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(user="User to count warns of")
    async def getwarns(self, ctx: commands.Context, user: Member):
        awarns = await execute_query(
            "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, user.id),
        )
        warns = int(awarns[-1][3]) if awarns else 0
        await ctx.send(f"User has {warns} warns")

    @commands.hybrid_command(description="Set a prefix for the guild")
    @commands.has_permissions(manage_channels=True)
    @app_commands.describe(prefix="Prefix to set")
    async def setprefix(self, ctx: commands.Context, prefix: str):
        try:
            await execute_query(
                "INSERT INTO prefixes (guild_id, prefix) VALUES (?, ?)",
                (ctx.guild.id, prefix),
            )
            prefix = await execute_query(
                "SELECT prefix FROM prefixes WHERE guild_id = ?", (
                    ctx.guild.id,)
            )
            await ctx.send(
                f"Successfully set the prefix for the guild to `{prefix[0]}`"
            )
        except Exception as e:
            await ctx.send(f"{e}")

    @commands.hybrid_command(description="Get the prefix of the current guild.")
    @commands.has_permissions(manage_messages=True)
    async def getprefix(self, ctx: commands.Context):
        prefix = await execute_query(
            "SELECT prefix FROM prefixes WHERE guild_id = ?", (ctx.guild.id,)
        )
        if prefix is None:
            await ctx.send("The prefix hasn't been set, so far.")
            return
        await ctx.send(f"The prefix has been set to `{prefix[0]}`")


async def setup(bot: JoryuPy):
    await bot.add_cog(Moderation(bot))

