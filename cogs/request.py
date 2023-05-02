import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from utils.ParseJson import ParseJson

class SuccessButton(discord.ui.View):
    @discord.ui.button(label="Request Received.", style=discord.ButtonStyle.green)
    async def success_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
class FailureButton(discord.ui.View):
    @discord.ui.button(label="Request Failed.", style=discord.ButtonStyle.red)
    async def failure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
class SuccessButtonUnreq(discord.ui.View):
    @discord.ui.button(label="Request Deleted.", style=discord.ButtonStyle.green)
    async def failure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
class SuccessButtonEdit(discord.ui.View):
    @discord.ui.button(label="Request Edited.", style=discord.ButtonStyle.green)
    async def failure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

ParseJson = ParseJson()
channels = ParseJson.read_file("channels.json")

class Request(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.request_channel = channels["dump"] 

    async def embed_handler(self, message, request_description, index):
        request_description = f"{index}) {request_description}"
        if message:
            original_emb = message.embeds[0]
            original_desc = original_emb.description
            new_desc = original_desc+"\n"+request_description
            embed = discord.Embed(
                    title=original_emb.title,
                    description=new_desc,
                    color=original_emb.color)
            await message.edit(embed=embed)
            return True

        embed = discord.Embed(
                title="Feature Request",
                description=request_description,
                color=discord.Color.blue())
        return embed

    async def find_index(self, target=None):
        ind = 0
        channel = await self.bot.fetch_channel(self.request_channel)
        async for message in channel.history(oldest_first=True):
            if message.embeds and message.author == self.bot.user:
                embed = message.embeds[0]
                if "Feature Request List" in embed.title:
                    items = len(embed.description.split("\n"))
                    if target and target >= ind and target <= ind+items: 
                        return [embed, message]
                    ind += items
        return ind+1

    async def find_embed(self, description):
        channel = await self.bot.fetch_channel(self.request_channel)
        index = await self.find_index()
        async for message in channel.history():
            if message.embeds and message.author == self.bot.user:
                embed = message.embeds[0]
                if "Feature Request List" in embed.title:
                    if (len(embed.description)+len(description)) < 4096:
                        await self.embed_handler(message, description, index)
                    else:
                        request_embed = await self.embed_handler(None, description, index)
                        await channel.send(embed=request_embed)
                    return

        request_embed = await self.embed_handler(None, description, "1")
        await channel.send(embed=request_embed)

    async def update_request_order(self, number):
        channel = await self.bot.fetch_channel(self.request_channel)
        items = 0
        async for message in channel.history(oldest_first=True):
            if message.embeds and message.author == self.bot.user:
                embed = message.embeds[0]
                if "Feature Request List" in embed.title:
                    items += len(embed.description.split("\n"))
                    if items < number:
                        continue
                    desc_list = embed.description.split("\n")
                    for request in desc_list:
                        num_ind = request.find(") ")
                        if int(request[:num_ind]) > number:
                            request_ind = desc_list.index(request)
                            desc_list[request_ind] = f"{int(request[:num_ind])-1}{request[num_ind:]}"
                    new_desc = "\n".join(desc_list)
                    new_emb = discord.Embed(
                            title=embed.title,
                            description=new_desc,
                            color=embed.color)
                    await message.edit(embed=new_emb)

    async def delete_request(self, number):
        total = await self.find_index()-1

        embed, message = await self.find_index(number)
        description = embed.description.split("\n")
        for item in description:
            if item.startswith(f"{number}) "):
                description.remove(item)
                break
        description = "\n".join(description)
        new_emb = discord.Embed(
                title=embed.title,
                description=description,
                color=embed.color)
        await message.edit(embed=new_emb)

        await self.update_request_order(number)

    async def edit_request(self, number, new_desc):
        embed, message = await self.find_index(number)
        description = embed.description.split("\n")
        for item in description:
            if item.startswith(f"{number}) "):
                ind = description.index(item)
                end_name_ind = description[ind].find(":")+1
                if (len(embed.description)-len(item)+len(new_desc)+len(item[:end_name_ind])) > 4096:
                    raise Exception
                description[ind] = f"{description[ind][:end_name_ind]} {new_desc}"
                break

        new_desc = "\n".join(description)
        new_emb = discord.Embed(
                title=embed.title,
                description=new_desc,
                color=embed.color)
        await message.edit(embed=new_emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx):
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(fmt)} cmds.")

    @app_commands.command(name="request",description="Allows user requests")
    async def request(self, interaction: discord.Interaction, request_description: str):
        requester_name = f" {interaction.user.name}#{interaction.user.discriminator}"
        desc = f"{requester_name}: {request_description}"
        await self.find_embed(desc)
        await interaction.response.send_message(view=SuccessButton(), ephemeral=True)

    @request.error
    async def request_error(self, interaction, error):
        await interaction.response.send_message(view=FailureButton(), ephemeral=True)

    @app_commands.command(name="unrequest",description="Deletes user requests (Admin-Only)")
    async def unrequest(self, interaction: discord.Interaction, number: int):
        if not interaction.user.guild_permissions.administrator:
            raise Exception
        if number < 0 or number > await self.find_index():
            raise Exception
        await self.delete_request(number)
        await interaction.response.send_message(view=SuccessButtonUnreq(), ephemeral=True)

    @unrequest.error
    async def unrequest_error(self, interaction, error):
        await interaction.response.send_message(view=FailureButton(), ephemeral=True)

    @app_commands.command(name="edit", description="Edits user requests (Admin-Only)")
    async def edit(self, interaction: discord.Interaction, number: int, description: str):
        if not interaction.user.guild_permissions.administrator:
            raise Exception
        await self.edit_request(number, description)
        await interaction.response.send_message(view=SuccessButtonEdit(), ephemeral=True)

    @edit.error
    async def edit_error(self, interaction, error):
        await interaction.response.send_message(view=FailureButton(), ephemeral=True)

    @app_commands.command(name="setdump", description="Set the channel for request dumps.")
    async def setdump(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            raise Exception
        self.request_channel = interaction.channel.id
        channels["dump"] = self.request_channel
        ParseJson.save_file("channels.json", channels)
        await interaction.response.send_message(f"Request dumps will be sent to {interaction.channel.mention}",
                ephemeral=True)

    @setdump.error
    async def setdump_error(self, interaction, error):
        await interaction.response.send_message("Updating channel failed.", ephemeral=True)
        

async def setup(bot):
    await bot.add_cog(Request(bot), guilds=[discord.Object(id=GUILD_ID_HERE)])
