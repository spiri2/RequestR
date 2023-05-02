import discord
from discord import app_commands
from discord.ext import commands
from utils.ParseJson import ParseJson
import asyncio

class SuccessButton(discord.ui.View):
    @discord.ui.button(label="Command Executed Successfully.", style=discord.ButtonStyle.green)
    async def success_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
class FailureButton(discord.ui.View):
    @discord.ui.button(label="Command Failed.", style=discord.ButtonStyle.red)
    async def failure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

ParseJson = ParseJson()
channels = ParseJson.read_file("channels.json")

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.restricted_channel = channels["request-features"]
        self.restricted_channel = CHANNEL ID HERE
        self.whitelisted_cmd = "request"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.restricted_channel:
            await self.bot.process_commands()
            return
        if message.author.guild_permissions.administrator or message.author.guild_permissions.ban_members:
            await self.bot.process_commands()
            return
        if not message.interaction or message.interaction.name != self.whitelisted_cmd:
            try:
                await message.delete()
            except:
                pass

        await self.bot.process_commands()
    
    def is_interaction(self, message):
        return not message.interaction

    @app_commands.command(name="clear", description="Delete Messages (Admin-Only)")
    async def clear(self, interaction: discord.Interaction, number: int):
        if not interaction.user.guild_permissions.administrator:
            raise Exception

        await interaction.response.defer()
        
        cleared = await interaction.channel.purge(limit=number+1, check=self.is_interaction, bulk=True)
        cleared = len(cleared)
        followup = await interaction.followup.send(f"# Requested: {number}\n# Cleared: {cleared}",
                view=SuccessButton(), ephemeral=True)

        await asyncio.sleep(3)
        await followup.delete()
        
    @clear.error
    async def clear_error(self, interaction, error):
        if interaction.response.is_done():
            await interaction.followup.send(view=FailureButton(), ephemeral=True)
        else:
            await interaction.response.send_message(view=FailureButton(), ephemeral=True)

    @app_commands.command(name="setrequests", description="Set the channel for user requests")
    async def setrequests(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            raise Exception
        self.restricted_channel = interaction.channel.id
        channels["requests"] = self.restricted_channel
        ParseJson.save_file("channels.json", channels)
        await interaction.response.send_message(f"/{self.whitelisted_cmd} is whitelisted in {interaction.channel.mention}",
                ephemeral=True)

    @setrequests.error
    async def setrequests_error(self, interaction, error):
        await interaction.response.send_message("Updating channel failed.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Staff(bot), guilds=[discord.Object(id=GUILD ID HERE)])
