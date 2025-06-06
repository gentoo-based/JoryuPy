from subprocess import TimeoutExpired, run
from typing import Literal, Optional

from discord import Attachment, File, Interaction, app_commands
from discord.ext import commands

from joryu import JoryuPy


class Owner(commands.Cog):
    def __init__(self, bot: JoryuPy) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Talk through the bot (owner only)")
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.describe(
        message="Message to say",
        messageid="Message ID to reply to",
        attachment="Attachment to send",
    )
    async def echo(
        self,
        ctx: commands.Context,
        message: Optional[str],
        messageid: Optional[str],
        attachment: Optional[Attachment],
    ):
        if ctx.interaction is None:
            await ctx.message.delete()
            await ctx.channel.typing()
        else:
            await ctx.channel.typing()
            await ctx.defer(ephemeral=True)
        if attachment:
            if message:
                if messageid:
                    await ctx.channel.get_partial_message(messageid).reply(
                        content=message, File=File(attachment)
                    )
                    return
                await ctx.channel.send(file=File(attachment), content=message)
            else:
                if messageid:
                    await ctx.channel.get_partial_message(messageid).reply(
                        File=File(attachment)
                    )
                    return
                await ctx.channel.send(file=File(attachment))
            return
        elif message:
            if messageid:
                await ctx.channel.get_partial_message(messageid).reply(content=message)
                return
            await ctx.channel.send(content=message)
        await ctx.send("Sent!", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(cog="The specified cog to load")
    async def load(self, ctx: commands.Context, cog: Literal["moderation", "misc"]):
        """Loads a specified cog."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer(ephemeral=True)
        await self.bot.load_extension("plugins." + cog)
        if ctx.interaction is None:
            await ctx.author.send(f"Loaded cog: {cog} successfully.")
        else:
            await ctx.send(content=f"Loaded cog: {cog} successfully.", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(cog="The specified cog to unload")
    async def unload(self, ctx: commands.Context, cog: Literal["moderation", "misc"]):
        """Unloads a specified cog."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer(ephemeral=True)
        await self.bot.unload_extension("plugins." + cog)
        if ctx.interaction is None:
            await ctx.author.send(f"Unloaded cog: {cog} successfully.")
        else:
            await ctx.send(content=f"Unloaded cog: {cog} successfully.", ephemeral=True)

    @app_commands.command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(command="Command to run on the phone")
    async def sh(self, ctx: Interaction, command: str):
        """Run a command on the phone"""
        await ctx.response.defer()

        result = run(command, shell=True, capture_output=True, text=True, timeout=54000)

        # Prepare output message
        output = result.stdout if result.stdout else "No output."
        error = result.stderr if result.stderr else ""

        # Discord message limit is 2000 characters, truncate if needed
        if len(output) > 1900:
            output = output[:1900] + "\n...[output truncated]"
        if len(error) > 1900:
            error = error[:1900] + "\n...[error truncated]"

        response = f"**Output:**\n```{output}```"
        if error:
            response += f"\n**Error:**\n```{error}```"
        await ctx.followup.send(response)

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(cog="The specified cog to reload")
    async def reload(
        self, ctx: commands.Context, cog: Literal["moderation", "misc", "owner"]
    ):
        """Reloads a specified cog."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer(ephemeral=True)
        await self.bot.reload_extension("plugins." + cog)
        if ctx.interaction is None:
            await ctx.author.send(f"Reloaded cog: {cog} successfully.")
        else:
            await ctx.send(content=f"Reloaded cog: {cog} successfully.", ephemeral=True)

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def sync(self, ctx: commands.Context):
        """Sync the command tree"""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer(ephemeral=True)
        await self.bot.tree.sync()
        if ctx.interaction is None:
            await ctx.author.send(f"Synced the command tree successfully.")
        else:
            await ctx.send(
                content=f"Synced the command tree successfully.", ephemeral=True
            )

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def reinit(self, ctx: commands.Context):
        """Reset/reinitialize the bot."""
        if ctx.interaction is None:
            await ctx.channel.typing()
        else:
            await ctx.defer(ephemeral=True)
        await self.bot.load_extension("plugins.misc")
        await self.bot.load_extension("plugins.moderation")
        await self.bot.load_extension("plugins.owner")
        await self.bot.tree.sync()
        if ctx.interaction is None:
            await ctx.author.send(content="Successfully reinitialized the bot. Phew...")
        else:
            await ctx.send(
                content="Successfully reinitialized the bot. Phew...", ephemeral=True
            )


async def setup(bot: JoryuPy):
    await bot.add_cog(Owner(bot))
