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

    @discord.app_commands.command(name="reload", description='Recarrega algumas funcionalidades')
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def _reload(self, interaction: discord.Interaction, skip_resync: bool):
        msg = "*[Recarregando código]*"
        await interaction.response.send_message(msg)
        cogs = []
        fail_cogs = []
        for cog in os.listdir("cogs"):
            if not os.path.isfile("cogs\\"+cog): continue            
            try:       
            await self.bot.reload_extension(f"cogs.{cog[:-3]}")
                cogs.append(f'`✅ {cog}`')
            except:
                cogs.append(f'`❎ {cog}`')
                fail_cogs.append(f'`❎ {cog}`')
        
        msg += '\n' + '\n'.join(cogs)
        await interaction.edit_original_response(content=msg)
        
        msg += '\n*[Sincronizando comandos]*'
        await interaction.edit_original_response(content=msg)
        fmt = []
        if not skip_resync:
            fmt = await self.bot.tree.sync(guild=interaction.guild)
        
        msg += f'\n`✅ {len(fmt)} comandos sincronizados.`'
        await interaction.edit_original_response(content=msg)

        await interaction.edit_original_response(content='**✅ Reload completo**'+(f" com erros!\n"+"\n".join(fail_cogs) if fail_cogs else ' sem erros!'))


async def setup(bot):
    await bot.add_cog(Admin(bot), guilds=[discord.Object(id=1024844907090821120)])