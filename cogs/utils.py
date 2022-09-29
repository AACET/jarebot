from pydoc import describe
from discord.ext import commands
import discord
from libs import config

class Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        latency = f"{str(round(self.bot.latency * 1000))} ms"
        await interaction.response.send_message(f"🏓 **Pong** ({latency})")


async def setup(bot):
    await bot.add_cog(Utils(bot), guilds=[discord.Object(id=1024844907090821120)])