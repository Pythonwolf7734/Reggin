import discord
from discord.ext import commands
import sqlite3

client = commands.Bot(command_prefix = 'reg:')


#DATABASE CREATE
connection = sqlite3.connect("/media/pi/JONAH_3/Python/Discord_Bot/Regin/Reggin_data.db") #Opening Database
cursor = connection.cursor()

#cursor.execute("""CREATE TABLE users (
#        userid INT, ing_name TEXT, clan INT, money INT, lastDaily TEXT
#    )""")   #Creating table with data for users

#cursor.execute("DROP TABLE clans")

#cursor.execute("""CREATE TABLE clans (
#        clanid INT, public INT, owner INT, level INT, name TEXT, castle INT
#    )""")   #Creating table with data for clans

connection.commit()
#END DATABASE


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("best bot"))
    print('Bot is ready...')
    guild = discord.utils.get(client.guilds, id=866788715413372979)
    channel = guild.get_channel(877604557377654844)
    embed = discord.Embed(description = f"Bot online", color=discord.Colour(0x91703b))
    await channel.send(embed=embed)



client.run('ODY4Mzg2NTk3NjE0MjU2MTc5.YPu6Cg.sCBJX85U905RnlmCwykR52Qmg8Q')