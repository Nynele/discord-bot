import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

DATABASE_PATH = 'database/moderation.db'

class ConfigCog(commands.Cog):
    """
    A cog for bot configuration commands, grouped under /configuracion.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Create a command group
    config_group = app_commands.Group(name="configuracion", description="Comandos de configuración del bot.")

    @config_group.command(
        name="canal_logs",
        description="Establece el canal para registrar las acciones de moderación."
    )
    @app_commands.describe(
        canal="El canal de texto que se usará para los logs."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """
        Sets the logging channel for the server.
        """
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild.id
        channel_id = canal.id

        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO guild_configs (guild_id, log_channel_id) VALUES (?, ?)",
                    (guild_id, channel_id)
                )
                await db.commit()

            embed = discord.Embed(
                title="✅ Configuración Guardada",
                description=f"El canal de logs ha sido establecido en {canal.mention}.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Error saving configuration: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Ocurrió un error al intentar guardar la configuración. Por favor, inténtalo de nuevo.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @set_log_channel.error
    async def on_configure_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Error handler for the configure command."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "No tienes los permisos de administrador necesarios para usar este comando.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Ocurrió un error inesperado.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Sets up the cog."""
    await bot.add_cog(ConfigCog(bot))