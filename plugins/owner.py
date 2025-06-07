import asyncio
import base64
import binascii
from asyncio import create_subprocess_shell, create_subprocess_exec, subprocess
from typing import Literal, Optional, Tuple

import aiofiles
from discord import Attachment, File, Interaction, app_commands
from discord.ext import commands
import tempfile
import os
from joryu import JoryuPy
from .tdodl import check_policy

async def async_compile_code(content: str, language: str, output_executable: str = "a.out") -> Tuple[bool, str]:
    """
    Asynchronously compile C or C++ code from a string using gcc or g++.

    Returns:
        (success: bool, message: str)
    """
    if language.lower() == 'c':
        compiler = 'gcc'
        lang_flag = 'c'
    elif language.lower() in ('cpp', 'c++'):
        compiler = 'g++'
        lang_flag = 'c++'
    else:
        return False, "Unsupported language. Use 'c' or 'cpp'."

    # Write source code to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{lang_flag}', delete=False) as src_file:
        src_file.write(content)
        src_filename = src_file.name

    try:
        # Create subprocess asynchronously
        proc = await create_subprocess_exec(
            compiler, '-x', lang_flag, src_filename, '-o', output_executable,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for process to complete and capture output
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            return True, f"Compilation succeeded, executable: {output_executable}"
        else:
            # Decode stderr for error messages
            return False, f"Compilation failed:\n{stderr.decode().strip()}"
    except Exception as e:
        return False, f"Compilation error: {str(e)}"
    finally:
        # Clean up the temporary source file
        os.remove(src_filename)


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
        if ctx.interaction is not None:
            await ctx.interaction.followup.send("Sent!", ephemeral=True)

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
            await ctx.interaction.followup.send(
                content=f"Loaded cog: {cog} successfully.", ephemeral=True
            )

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
            await ctx.interaction.followup.send(
                content=f"Unloaded cog: {cog} successfully.", ephemeral=True
            )

    @commands.hybrid_command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(command="Command to run on the phone")
    async def sh(self, ctx: commands.Context, command: str):
        """Run a command on the phone"""
        if not await check_policy(command, "./policy") and ctx.author.id not in self.bot.authorized_owner_ids and ctx.author.id in self.bot.unauthorized_owner_ids:
            await ctx.defer()
            if ctx.interaction is not None:
                await ctx.interaction.followup.send(f"You are not worthy to run: {command}")
            else:
                await ctx.send(f"You are not worthy of such command: {command}")
            return

        async def initialize_response():
            result = await create_subprocess_shell(
                cmd=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Prepare output message
            output, error = await result.communicate()

            # Discord message limit is 2000 characters, truncate if needed
            if len(output) > 1900:
                cmd_shell = await create_subprocess_shell(
                    cmd=f'echo "{output.decode()}" | wgetpaste',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                output, error = await cmd_shell.communicate()
                response = f"**Output:**\n```{output.decode()}```"
                return response
            if len(error) > 1900:
                cmd_shell = await create_subprocess_shell(
                    cmd=f'echo "{error.decode()}" | wgetpaste',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                output, error = await cmd_shell.communicate()
                response = f"**Error:**\n```{error.decode()}```"
                return response

            response = f"**Output:**\n```{output.decode()}```"
            if error:
                response = f"\n**Error:**\n```{error.decode()}```"
            return response

        if ctx.interaction is not None:
            await ctx.defer()
            if ctx.author.id not in self.bot.unauthorized_owner_ids and ctx.author.id not in self.bot.authorized_owner_ids:
                await ctx.interaction.followup.send(":(", ephemeral=True)
                return
            await ctx.interaction.followup.send(await initialize_response())
        else:
            if ctx.author.id not in self.bot.unauthorized_owner_ids and ctx.author.id not in self.bot.authorized_owner_ids:
                await ctx.send(":(", ephemeral=True)
                return
            await ctx.send(await initialize_response())

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
            await self.bot.reload_extension("plugins." + cog)
            await ctx.author.send(f"Reloaded cog: {cog} successfully.")
        else:
            await ctx.defer()
            await self.bot.reload_extension("plugins." + cog)
            await ctx.interaction.followup.send(
                content=f"Reloaded cog: {cog} successfully.", ephemeral=True
            )

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def sync(self, ctx: commands.Context):
        """Sync the command tree"""
        if ctx.interaction is None:
            await self.bot.tree.sync()
            await ctx.author.send(f"Synced the command tree successfully.")
        else:
            await ctx.defer()
            await self.bot.tree.sync()
            await ctx.interaction.followup.send(
                f"Synced the command tree successfully."
            )

    @commands.hybrid_command()
    @commands.is_owner()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def reinit(self, ctx: commands.Context):
        """Reset/reinitialize the bot."""
        await ctx.defer()
        await self.bot.reload_extension("plugins.misc")
        await self.bot.reload_extension("plugins.moderation")
        await self.bot.reload_extension("plugins.owner")
        await self.bot.tree.sync()
        if ctx.interaction is None:
            await ctx.author.send(content="Successfully reinitialized the bot. Phew...")
        else:
            await ctx.interaction.followup.send(
                content="Successfully reinitialized the bot. Phew...", ephemeral=True
            )


async def setup(bot: JoryuPy):
    await bot.add_cog(Owner(bot))
