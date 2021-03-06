import discord
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import sqlite3
import datetime

#DATABASE CREATE
connection = sqlite3.connect("/media/pi/JONAH_31/Python/Discord_Bot/Regin/Reggin_data.db") #Opening Database
cursor = connection.cursor()

#cursor.execute("DROP TABLE users")

#cursor.execute("""CREATE TABLE users (
#        userid INT, ing_name TEXT, clan INT, money INT, lastDaily TEXT, attack INT, health INT, defend INT, dailyStrike INT
#    )""")   #Creating table with data for users

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
            if user_data[2] == 0 or user_data[2] == "0":
                self.clan = None
            else:
                self.clan = Clan(user_data[2])
            self.money = user_data[3]
            self.attack = user_data[5]
            self.health = user_data[6]
            self.defend = user_data[7]
            self.last_daily = user_data[4]
            self.streak = user_data[8]

    def delete(self):
        cursor.execute("DELETE FROM users WHERE userid=?", (self.id,))
        if self.clan != None:
            cursor.execute("DELETE FROM clans WHERE owner=?", (self.id,))
            cursor.execute("UPDATE users SET clan=? WHERE clan=?", (0, self.clan.id))
        connection.commit()

    def set_clan(self, clan_id):
        cursor.execute("UPDATE users SET clan=? WHERE userid=?", (clan_id, self.id))
        connection.commit()
        self.clan = Clan(clan_id)

    def add_money(self, amount):
        cursor.execute("UPDATE users SET money=? WHERE userid=?", (self.money+amount, self.id))
        connection.commit()
        self.money = self.money+amount

    def update_daily(self):
        cursor.execute("UPDATE users SET lastDaily=? WHERE userid=?", (str(datetime.datetime.now()), self.id))
        connection.commit()
        self.last_daily = str(datetime.datetime.now())

    def update_streak(self, streak):
        cursor.execute("UPDATE users SET dailyStrike=? WHERE userid=?", (streak, self.id))
        connection.commit()
        self.streak = streak
        


#END Classes


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="register", description="Register yourself for the economy system")
    async def register(self, ctx: SlashContext):
        try:
            user = User(ctx.author.id)
        except:
            time = datetime.datetime(year=2019, month=10, day=23, hour=6, minute=40, second=15)
            cursor.execute("INSERT INTO  users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (ctx.author.id, ctx.author.name, 0, 0, time, 0, 0, 0, 0))
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

    @cog_ext.cog_slash(name="money", description="See how rich you are")
    async def _money(self, ctx: SlashContext):
        try:
            user = User(ctx.author.id)
        except:
            await ctx.send("You are not registered! Use /register to register you!", hidden=True)
            return
        else:
            embed = discord.Embed(colour=discord.Colour(0xd4af37), description=f"You have {user.money} coins!")
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="daily", description="Get your daily coins")
    async def _daily(self, ctx: SlashContext):
        try:
            user = User(ctx.author.id)
        except:
            await ctx.send("You are not registered! Use /register to register you!", hidden=True)
            return
        else:
            day_last = user.last_daily.split(" ")[0]
            time_last = user.last_daily.split(" ")[1]
            last_time = datetime.datetime(year=int(day_last.split("-")[0]), month=int(day_last.split("-")[1]), day=int(day_last.split("-")[2]), hour=int(time_last.split(":")[0]), minute=int(time_last.split(":")[1]))
            time_diff = datetime.datetime.now() - last_time
            if time_diff.days < 1:
                to_wait = 24-(time_diff.seconds/3600)
                to_wait = round(to_wait, 0)
                to_wait = str(to_wait).split(".")[0]
                if to_wait == 0:
                    to_wait = 1440-(time_diff.seconds/60)
                    to_wait = round(to_wait, 0)
                    to_wait = str(to_wait).split(".")[0]
                    embed = discord.Embed(colour=discord.Colour(0x359ae), description=f"You can claim your daily money again in {to_wait}min")
                else:
                    embed = discord.Embed(colour=discord.Colour(0x359ae), description=f"You can claim your daily money again in {to_wait}h")
                    await ctx.send(embed=embed, hidden=True)
                    return
            else:
                if time_diff.days > 2:
                    money = 69
                    if user.streak == 0:
                        streak = "Claim your money again tomorrow to get a streak!"
                    else:
                        streak = f"Uff! Your streak broke. You had a streak of {user.streak}"
                        user.update_streak(0)
                else:
                    streak = user.streak + 1
                    user.update_streak(streak)
                    money = 69 + (streak*10)
                    streak = f"Your current streak is now {streak}"
                user.add_money(money)
                user.update_daily()
                embed = discord.Embed(colour=discord.Colour(0xd4af37), description=f"You claimed your {money} daily coins!")
                embed.set_footer(text=streak)
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Slash(bot))