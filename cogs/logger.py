from datetime import datetime, tzinfo
from operator import add
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
    async def on_guild_role_update(self, old: discord.Role, new: discord.Role):
        channel = old.guild.get_channel(config.logger.getint("channel_id"))
        actor = await self.get_actor(discord.AuditLogAction.role_update, old.guild)
        fields: list[list[str]] = []

        if old.name != new.name:
            fields.append(["Nome anterior", old.name])
            fields.append(["Nome atual", new.name])

        changed_perms = []
        old_perms = {perm: state for perm, state in old.permissions}
        for perm, state in new.permissions:
            if old_perms[perm] != state:
                changed_perms.append(f"`{'❎' if not state else '✅'} {perm}`")
        
        if changed_perms:
            fields.extend([
                ["Permissões editadas", '\n'.join(changed_perms)]
            ])

        await self.log(
            channel,
            "✍️ Cargo editado",
            f"Um cargo foi alterado",
            [
                *fields,
                ["Quem editou", actor.mention]
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
                delta = new.timed_out_until.timestamp()  - datetime.now().timestamp()   
                await self.log(
                    channel,
                    "😶 Membro silenciado",
                    f"Um membro foi silenciado",
                    [
                        ["Membro", new.mention],
                        ["Quem silenciou", entry.user.mention],
                        ["Tempo", f"{round(delta)} segundos"]
                    ],            
                )
            else:
                await self.log(
                    channel,
                    "🗣️ Silenciamento removido",
                    f"Um membro teve seu som restaurado",
                    [
                        ["Membro", new.mention],
                    ],            
                )

        elif new.roles != old.roles:
            entry = await self.get_entry(discord.AuditLogAction.member_update, new.guild)
            added_roles: list[discord.Role] = []
            removed_roles: list[discord.Role] = []
            for role in [*old.roles, *new.roles]:
                if role not in old.roles:
                    added_roles.append(role)
                elif role not in new.roles:
                    removed_roles.append(role)
            
            fields: list[list[str]] = []

            if added_roles:
                fields.append(["Cargos Adicionados", "\n".join([i.mention for i in added_roles])])
            if removed_roles:
                fields.append(["Cargos Removidos", "\n".join([i.mention for i in removed_roles])])
            
            await self.log(
                channel,
                "✍️ Mudança de cargos",
                f"Um membro teve seus cargos editados",
                [
                    *fields,
                    ["Membro", new.mention],
                    ["Quem editou", entry.user.mention]
                ],
                new
            )


        


async def setup(bot):
    await bot.add_cog(Logger(bot))