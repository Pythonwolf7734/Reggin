import discord
from discord.ext import commands
import sqlite3

client = commands.Bot(command_prefix = 'reg:')

#Utility functions
def read_replace(read, type="db"):
    #read = str(read)
    if type != "db":
        read=str(read)
    if type == "db":
        if read is None:
            return None
        for r in read:
            read = r
    elif type == "userid":
        read = read.replace(">", "")
        read = read.replace("<@", "")
        read = read.replace("!", "")
    elif type == "channelid":
        read = read.replace("<#", "")
        read = read.replace(">", "")
    elif type == "roleid":
        read = read.replace("<", "")
        read = read.replace("@", "")
        read = read.replace("&", "")
        read = read.replace(">", "")
    return read
#End utility functions



#DATABASE CREATE
connection = sqlite3.connect("/media/pi/JONAH_3/Python/Discord_Bot/Regin/Reggin_data.db") #Opening Database
cursor = connection.cursor()

#cursor.execute("""CREATE TABLE users (
#        userid INT, ing_name TEXT, clan INT, money INT, lastDaily TEXT, attack INT, health INT, defend INT
#    )""")   #Creating table with data for users

#cursor.execute("DROP TABLE clans")

#cursor.execute("""CREATE TABLE clans (
#        clanid INT, public INT, owner INT, level INT, name TEXT, castle INT
#    )""")   #Creating table with data for clans
#cursor.execute("DELETE FROM clans")
#cursor.execute("INSERT INTO  clans VALUES (?, ?, ?, ?, ?, ?)", (0, 1, 2, 3, 4, 5))
connection.commit()
#cursor.execute("SELECT * FROM clans")
#for x in cursor:
#    print(x)
#END DATABASE


#Classes

class Clan:

    def __init__(self, id):
        #Creating clan object
        #Selecting data from database
        data = {}
        cursor.execute("SELECT * FROM clans WHERE clanid=?", (id,))
        raw_data = cursor.fetchall()
        for el in raw_data:
            i = 0
            for x in el:
                data[i] = x
                i += 1
        self.id = data[0]
        if data[1] == 0:
            self.public = False
        elif data[1] == 1:
            self.public = True
        self.owner = data[2]
        self.level = data[3]
        self.name = data[4]
        self.castle = data[5]


class User:

    def __init__(self, id):
        cursor.execute("SELECT * FROM users WHERE userid=?", (id,))
        data = cursor.fetchone()
        if data is None:
            raise ValueError
        else:
            user_data = {}
            i = 0
            for x in data:
                user_data[i] = x
                i += 1
            self.id = user_data[0]
            self.name = user_data[1]
            if user_data[2] == 0:
                self.clan = None
            else:
                self.clan = Clan(user_data[2])
            self.money = user_data[3]
            self.attack = user_data[5]
            self.health = user_data[6]
            self.defend = user_data[7]

    def delete(self):
        cursor.execute("DELETE FROM users WHERE userid=?", (self.id,))
        if self.clan != None:
            cursor.execute("DELETE FROM clans WHERE owner=?", (self.id,))
            cursor.execute("UPDATE users SET clan=? WHERE clan=?", (0, self.clan.id))
        connection.commit()


#END Classes


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("best bot"))
    print('Bot is ready...')
    guild = discord.utils.get(client.guilds, id=866788715413372979)
    channel = guild.get_channel(877604557377654844)
    embed = discord.Embed(description = f"Bot online", color=discord.Colour(0xd4af37))
    await channel.send(embed=embed)

@client.command()
async def register(ctx):
    try:
        user = User(ctx.author.id)
    except:
        cursor.execute("INSERT INTO  users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, ctx.author.name, 0, 0, 0, 0, 0, 0))
        connection.commit()
        await ctx.send(f"Added {ctx.author.name} into database")
    else:
        await ctx.send("You are already in the databse")

@client.command()
async def delete(ctx):
    try:
        user = User(ctx.author.id)
    except:
        await ctx.send("You are not in the database")
    else:
        user.delete()
        await ctx.send(f"Deleted {user.name}")


client.run('Token')