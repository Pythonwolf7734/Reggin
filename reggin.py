import discord
from discord_slash import SlashCommand, SlashContext
from discord.ext import commands

client = commands.Bot(command_prefix = 'reg:')
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("best bot"))
    print('Bot is ready...')
    guild = discord.utils.get(client.guilds, id=866788715413372979)
    channel = guild.get_channel(877604557377654844)
    embed = discord.Embed(description = f"Bot online", color=discord.Colour(0xd4af37))
    await channel.send(embed=embed)

client.load_extension('economy')
client.run('ODY4Mzg2NTk3NjE0MjU2MTc5.YPu6Cg.qKmdUQ0is4TyBP2puWKdOGSu_2k')