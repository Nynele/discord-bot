import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiosqlite

# --- Configuration ---
DATABASE_PATH = 'database/moderation.db'

# --- Bot Initialization ---
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True  # Required for tracking members

bot = commands.Bot(command_prefix="/", intents=intents)

# --- Database Setup ---
async def initialize_database():
    """Initializes the database and creates tables from schema.sql if they don't exist."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        with open('database/schema.sql', 'r') as f:
            await db.executescript(f.read())
        await db.commit()
        print("Database initialized successfully.")

# --- Cog (Command Module) Loading ---
async def load_cogs():
    """Loads all command cogs from the 'cogs' directory."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

# --- Bot Events ---
@bot.event
async def on_ready():
    """Event that runs when the bot is connected and ready."""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    # Synchronize the slash commands with Discord
    await bot.tree.sync()
    print("Slash commands have been synchronized.")

# --- Main Execution ---
async def main():
    """Main function to set up and run the bot."""
    # Change to bot directory if running from root
    if not os.path.exists('database'):
        os.chdir('bot')
    load_dotenv()
    BOT_TOKEN = os.getenv("DISCORD_TOKEN")
    
    if BOT_TOKEN is None:
        raise ValueError("Error: DISCORD_TOKEN not found. Please create a .env file with your bot's token.")
    
    await initialize_database()
    await load_cogs()
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shutting down.")
    except ValueError as e:
        print(e)