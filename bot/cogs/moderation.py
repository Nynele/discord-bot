import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import datetime

DATABASE_PATH = 'database/moderation.db'

async def get_log_channel_id(guild_id: int) -> int | None:
    """Fetches the log channel ID for a given guild from the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT log_channel_id FROM guild_configs WHERE guild_id = ?", (guild_id,))
        result = await cursor.fetchone()
        return result[0] if result else None

class ModerationCog(commands.Cog):
    """
    A cog for core moderation commands, grouped under /moderacion.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Create a command group for all moderation commands
    mod_group = app_commands.Group(name="moderacion", description="Comandos de moderación para el servidor.")

    @mod_group.command(
        name="advertir",
        description="Advierte a un usuario por una razón específica."
    )
    @app_commands.describe(
        usuario="El usuario al que quieres advertir.",
        razon="La razón de la advertencia."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn_user(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild.id
        moderator = interaction.user
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("INSERT INTO warnings (guild_id, user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)", (guild_id, usuario.id, moderator.id, razon, datetime.datetime.now(datetime.timezone.utc).isoformat()))
                await db.commit()
        except Exception as e:
            await interaction.followup.send(f"❌ Error al guardar la advertencia: {e}", ephemeral=True)
            return
        await interaction.followup.send(f"✅ Has advertido a {usuario.mention} por: **{razon}**.", ephemeral=True)
        log_channel_id = await get_log_channel_id(guild_id)
        if log_channel_id and (log_channel := self.bot.get_channel(log_channel_id)):
            embed = discord.Embed(title="Usuario Advertido", color=discord.Color.orange(), timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.add_field(name="Usuario", value=usuario.mention, inline=False).add_field(name="Moderador", value=moderator.mention, inline=False).add_field(name="Razón", value=razon, inline=False)
            embed.set_footer(text=f"ID de Usuario: {usuario.id}")
            await log_channel.send(embed=embed)
        try:
            await usuario.send(embed=discord.Embed(title=f"Has sido advertido en {interaction.guild.name}", color=discord.Color.orange(), description=f"**Razón:** {razon}"))
        except discord.Forbidden:
            pass

    @mod_group.command(
        name="historial",
        description="Muestra el historial de moderación de un usuario."
    )
    @app_commands.describe(usuario="El usuario cuyo historial quieres ver.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def history(self, interaction: discord.Interaction, usuario: discord.Member):
        try:
            await interaction.response.defer(ephemeral=True)
            embed = discord.Embed(title=f"Historial de Moderación de {usuario.name}", color=discord.Color.blue())
            embed.set_footer(text=f"ID: {usuario.id}")
            try:
                embed.set_thumbnail(url=usuario.display_avatar.url)
            except:
                pass
            history_found = False
            try:
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    async with db.execute("SELECT moderator_id, reason, timestamp FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC", (interaction.guild.id, usuario.id)) as cursor:
                        warnings = await cursor.fetchall()
                        if warnings:
                            history_found = True
                            value = ""
                            for m_id, r, ts in warnings[:5]:
                                try:
                                    dt = datetime.datetime.fromisoformat(ts)
                                    time_str = discord.utils.format_dt(dt, style='R')
                                except:
                                    time_str = "Fecha desconocida"
                                value += f"- **Razón:** {r} | **Por:** <@{m_id}> | {time_str}\n"
                            if len(value) > 1024:
                                value = value[:1021] + "..."
                            embed.add_field(name=f"Advertencias ({len(warnings)})", value=value, inline=False)
            except Exception as e:
                print(f"Database error: {e}")
                embed.add_field(name="Error", value="Error al acceder a la base de datos.", inline=False)
            if not history_found:
                embed.description = "Este usuario no tiene un historial de moderación."
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Command error: {e}")
            try:
                await interaction.followup.send("Ocurrió un error inesperado.", ephemeral=True)
            except:
                pass

    @mod_group.command(name="kick", description="Expulsa a un usuario del servidor.")
    @app_commands.describe(usuario="El usuario que quieres expulsar.", razon="La razón de la expulsión.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_user(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)
        if usuario.top_role >= interaction.user.top_role:
            return await interaction.followup.send("❌ No puedes expulsar a alguien con un rol igual o superior.", ephemeral=True)
        try:
            await usuario.send(embed=discord.Embed(title=f"Has sido expulsado de {interaction.guild.name}", color=discord.Color.red(), description=f"**Razón:** {razon}"))
        except discord.Forbidden: pass
        await usuario.kick(reason=razon)
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("INSERT INTO kicks (guild_id, user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)", (interaction.guild.id, usuario.id, interaction.user.id, razon, datetime.datetime.now(datetime.timezone.utc).isoformat()))
            await db.commit()
        await interaction.followup.send(f"✅ {usuario.mention} ha sido expulsado.", ephemeral=True)
        log_channel_id = await get_log_channel_id(interaction.guild.id)
        if log_channel_id and (log_channel := self.bot.get_channel(log_channel_id)):
            embed = discord.Embed(title="Usuario Expulsado", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.add_field(name="Usuario", value=f"{usuario.mention}", inline=False).add_field(name="Moderador", value=interaction.user.mention, inline=False).add_field(name="Razón", value=razon, inline=False)
            await log_channel.send(embed=embed)

    @mod_group.command(name="ban", description="Banea a un usuario del servidor.")
    @app_commands.describe(usuario="El usuario que quieres banear.", razon="La razón del baneo.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_user(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)
        if usuario.top_role >= interaction.user.top_role:
            return await interaction.followup.send("❌ No puedes banear a alguien con un rol igual o superior.", ephemeral=True)
        try:
            await usuario.send(embed=discord.Embed(title=f"Has sido baneado de {interaction.guild.name}", color=discord.Color.dark_red(), description=f"**Razón:** {razon}"))
        except discord.Forbidden: pass
        await usuario.ban(reason=razon)
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("INSERT INTO bans (guild_id, user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)", (interaction.guild.id, usuario.id, interaction.user.id, razon, datetime.datetime.now(datetime.timezone.utc).isoformat()))
            await db.commit()
        await interaction.followup.send(f"✅ {usuario.mention} ha sido baneado.", ephemeral=True)
        log_channel_id = await get_log_channel_id(interaction.guild.id)
        if log_channel_id and (log_channel := self.bot.get_channel(log_channel_id)):
            embed = discord.Embed(title="Usuario Baneado", color=discord.Color.dark_red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.add_field(name="Usuario", value=f"{usuario.mention}", inline=False).add_field(name="Moderador", value=interaction.user.mention, inline=False).add_field(name="Razón", value=razon, inline=False)
            await log_channel.send(embed=embed)

    @mod_group.command(name="silenciar", description="Silencia a un usuario por un tiempo determinado.")
    @app_commands.describe(usuario="El usuario a silenciar.", duracion="Duración del silencio (ej. 5m, 1h, 2d).", razon="Razón del silencio.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_user(self, interaction: discord.Interaction, usuario: discord.Member, duracion: str, razon: str):
        await interaction.response.defer(ephemeral=True)
        try:
            delta = self.parse_duration(duracion)
            end_time = discord.utils.utcnow() + delta
        except ValueError as e:
            return await interaction.followup.send(f"❌ Formato de duración inválido: {e}", ephemeral=True)
        await usuario.timeout(end_time, reason=razon)
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("INSERT INTO mutes (guild_id, user_id, moderator_id, reason, end_timestamp, timestamp) VALUES (?, ?, ?, ?, ?, ?)", (interaction.guild.id, usuario.id, interaction.user.id, razon, end_time.isoformat(), datetime.datetime.now(datetime.timezone.utc).isoformat()))
            await db.commit()
        await interaction.followup.send(f"✅ {usuario.mention} ha sido silenciado hasta {discord.utils.format_dt(end_time, style='R')}.", ephemeral=True)
        log_channel_id = await get_log_channel_id(interaction.guild.id)
        if log_channel_id and (log_channel := self.bot.get_channel(log_channel_id)):
            embed = discord.Embed(title="Usuario Silenciado", color=0xFF9900, timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.add_field(name="Usuario", value=usuario.mention, inline=False).add_field(name="Moderador", value=interaction.user.mention, inline=False).add_field(name="Razón", value=razon, inline=False).add_field(name="Expira", value=discord.utils.format_dt(end_time, style='F'), inline=False)
            await log_channel.send(embed=embed)

    def parse_duration(self, dur_str: str) -> datetime.timedelta:
        s = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        total_seconds = 0
        num = ""
        for char in dur_str:
            if char.isdigit():
                num += char
            elif char in s:
                total_seconds += int(num) * s[char]
                num = ""
        if num: raise ValueError("Número sin designador.")
        return datetime.timedelta(seconds=total_seconds)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))