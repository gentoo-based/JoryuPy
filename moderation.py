from discord.ext import commands
from discord import app_commands, Member
from typing import Optional

@app_commands.guild_only()
class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot | commands.AutoShardedBot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(description="Ban a user")
    @commands.has_guild_permissions()
    @commands.bot_has_guild_permissions()
    @app_commands.describe(user="User to Ban", reason="Reason why you wanted to ban a specified user")
    async def ban(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        guild = ctx.guild
        await guild.ban(user=user, reason=reason)
        await ctx.send(f"Banned {user} for reason: {reason}")

    @commands.hybrid_command(description="Unban a user")
    @commands.has_guild_permissions()
    @commands.bot_has_guild_permissions()
    @app_commands.describe(user="User to unban", reason="Reason why you wanted to unban a specified user")
    async def unban(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        guild = ctx.guild
        await guild.unban(user=user, reason=reason)
        await ctx.send(f"Unbanned {user} for reason: {reason}")

    @commands.hybrid_command(description="kick a user")
    @commands.has_guild_permissions()
    @commands.bot_has_guild_permissions()
    @app_commands.describe(user="User to kick", reason="Reason why you wanted to kick a specified user")
    async def kick(self, ctx: commands.Context, user: Member, reason: Optional[str]):
        guild = ctx.guild
        await guild.kick(user=user, reason=reason)
        await ctx.send(f"Kicked {user} for reason: {reason}")

async def setup(bot: commands.Bot | commands.AutoShardedBot):
    await bot.add_cog(Moderation(bot))