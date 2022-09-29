from datetime import datetime
from discord.ext import commands
import discord
from libs import config
import logging

logger = logging.getLogger(__name__)


class Logger(commands.Cog):
    @staticmethod
    async def log(channel, title, description, fields: list[list[str]] = None, author: discord.Member | discord.User = None):
        embed=discord.Embed(title=title, description=description)
        if author:
            embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=True)
        
        await channel.send(embed=embed)

    @staticmethod
    async def get_entry(action: discord.AuditLogAction, guild: discord.Guild) -> discord.AuditLogEntry:
        async for entry in guild.audit_logs(limit=1, action=action):
            return entry
    
    @staticmethod
    async def get_actor(action: discord.AuditLogAction, guild: discord.Guild) -> discord.User | discord.Member:
        entry = await Logger.get_entry(action, guild)
        return entry.user

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(config.logger.get("channel_id"))
        await self.log(channel, "📥 Entrada", f"{member.mention} entrou no servidor", author=member)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(config.logger.get("channel_id"))
        await self.log(channel, "📤 Saída", f"{member.mention} saiu do servidor", author=member)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logger.info(f"[{message.author.display_name}]: {message.content}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        
        channel = message.guild.get_channel(config.logger.getint("channel_id"))
        actor = await self.get_actor(discord.AuditLogAction.message_delete, message.guild)
        await self.log(
            channel,
            "❌ Mensagem deletada",
            f"Uma mensagem foi deletada",
            [
                ["Conteúdo", message.content],
                ["Autor", message.author.mention],
                ["Quem deletou", actor.mention]
            ],
            author=message.author
        )

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        channel = role.guild.get_channel(config.logger.getint("channel_id"))
        actor = await self.get_actor(discord.AuditLogAction.role_delete, role.guild)
        await self.log(
            channel,
            "✨ Cargo criado",
            f"Um cargo foi criado",
            [
                ["Nome", role.name],
                ["Cor", role.colour],
                ["Permissões", '\n'.join([f'`{perm}`' for perm, allowed in role.permissions if allowed])],
                ["Criador", actor.mention]
            ],
    
        )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        channel = role.guild.get_channel(config.logger.getint("channel_id"))
        actor = await self.get_actor(discord.AuditLogAction.role_delete, role.guild)
        await self.log(
            channel,
            "❌ Cargo deletado",
            f"Um cargo foi deletado",
            [
                ["Nome", role.name],
                ["Cor", role.colour],
                ["Quem deletou", actor.mention]
            ],
    
        )
    
    @commands.Cog.listener()
    async def on_member_update(self, old: discord.Member, new: discord.Member):
        print(new.timed_out_until, old.timed_out_until)
        channel = new.guild.get_channel(config.logger.getint("channel_id"))
        if new.timed_out_until != old.timed_out_until:
            entry = await self.get_entry(discord.AuditLogAction.member_update, new.guild)
            if new.timed_out_until:
                delta = datetime.now() - datetime.fromtimestamp(new.timed_out_until)
                
                await self.log(
                    channel,
                    "😶 Membro silenciado",
                    f"Um membro foi silenciado",
                    [
                        ["Membro", new.mention],
                        ["Quem silenciou", entry.user],
                        ["Tempo", delta.seconds]
                    ],
            
                )


async def setup(bot):
    await bot.add_cog(Logger(bot))