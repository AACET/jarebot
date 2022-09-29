from pydoc import describe
from discord.ext import commands
import discord
from libs import config

class Utils(commands.Cog):

    @commands.command("ping", description='Uepa')
    async def ping(self, ctx):
        await ctx.send("🏓 Pong!")


async def setup(bot):
    await bot.add_cog(Utils(bot), guilds=[discord.Object(id=1024844907090821120)])