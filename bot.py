import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord import app_commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded: {filename}")

async def main():
    await load_cogs()
    await bot.start("BOT_TOKEN_HERE")

@bot.event
async def on_ready():
    print("Ready.")

asyncio.run(main())
