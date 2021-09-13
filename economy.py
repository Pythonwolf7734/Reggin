import discord
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import sqlite3

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
#cursor.execute("INSERT INTO  clans VALUES (?, ?, ?, ?, ?, ?)", (0, 0, 0, 0, "All ids", 0))
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

    def delete(self):
        cursor.execute("DELETE FROM clans WHERE clanid=?", (self.id,))
        cursor.execute("UPDATE users SET clan=? WHERE clan=?", (0, self.id))
        connection.commit()

    def change_level(self, new_level):
        cursor.execute("UPDATE clans SET level=? WHERE clanid=?", (new_level, self.id))
        connection.commit()
        self.level = new_level


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
            print(user_data[2])
            if user_data[2] == 0 or user_data[2] == "0":
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

    def set_clan(self, clan_id):
        cursor.execute("UPDATE users SET clan=? WHERE userid=?", (clan_id, self.id))
        connection.commit()


#END Classes


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="register", description="Register yourself for the economy system")
    async def register(self, ctx: SlashContext):
        try:
            user = User(ctx.author.id)
        except:
            cursor.execute("INSERT INTO  users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, ctx.author.name, 0, 0, 0, 0, 0, 0))
            connection.commit()
            await ctx.send(f"Added {ctx.author.name} into database")
        else:
            await ctx.send("You are already in the databse", hidden=True)

    @cog_ext.cog_slash(name="delete", description="Delete your data from the economy system")
    async def delete(self, ctx: SlashContext):
        try:
            user = User(ctx.author.id)
        except:
            await ctx.send("You are not in the database", hidden=True)
        else:
            user.delete()
            await ctx.send(f"Deleted {user.name}")

    @cog_ext.cog_slash(name="createclan", description="Create your own clan!", options=[{"name": "name", "description": "Your clans name", "type": 3, "required": True}, {"name": "public", "description": "If your guild is public everyone can join the guild", "type": 5, "required": True}])
    async def createclan(self, ctx: SlashContext, name, public):
        try:
            user = User(ctx.author.id)
        except:
            await ctx.send("You are not registered! Use /register to register you!", hidden=True)
            return
        if user.clan != None:
            await ctx.send("You are already in a clan", hidden=True)
            return
        id_clan = Clan(0)
        if public:
            cursor.execute("INSERT INTO  clans VALUES (?, ?, ?, ?, ?, ?)", (id_clan.level+1, 1, ctx.author.id, 1, name, 0))
        else:
            cursor.execute("INSERT INTO  clans VALUES (?, ?, ?, ?, ?, ?)", (id_clan.level+1, 0, ctx.author.id, 1, name, 0))
        connection.commit()
        user.set_clan(id_clan.level+1)
        user = User(ctx.author.id)
        await ctx.send(f"Clan `{user.clan.name}` was created!")
        id_clan.change_level(id_clan.level+1)

    @cog_ext.cog_slash(name="deleteclan", description="Delete your clan!")
    async def deleteclan(self, ctx: SlashContext):
        try:
            user = User(ctx.author.id)
        except:
            await ctx.send("You are not registered! Use /register to register you!", hidden=True)
            return
        if user.clan == None:
            await ctx.send("You don't own a clan!", hidden=True)
            return
        elif user.clan.owner != ctx.author.id:
            await ctx.send("You don't own a clan!", hidden=True)
            return
        else:
            user.clan.delete()
            await ctx.send(f"Deleted your clan `{user.clan.name}`!")

def setup(bot):
    bot.add_cog(Slash(bot))