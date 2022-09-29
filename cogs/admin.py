import os
from pydoc import describe
from discord.ext import commands
import discord
from libs import config

class Admin(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        
        await self.bot.change_presence(activity=discord.Game("café nas pessoas"))

    @commands.command("reload", description='Recarrega algumas funcionalidades', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx):
        for cog in os.listdir("cogs"):
            if not os.path.isfile("cogs\\"+cog): continue            
            await self.bot.reload_extension(f"cogs.{cog[:-3]}")
        await ctx.send("Código recarregado 👍")


async def setup(bot):
    await bot.add_cog(Admin(bot))