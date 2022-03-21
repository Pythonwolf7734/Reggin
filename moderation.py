import discord
from discord.channel import TextChannel
from discord_slash import cog_ext, SlashContext
from discord.ext import commands

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="lockdown", description="Lock all channels!")
    async def _lockdown(self, ctx: SlashContext):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            embed = discord.Embed(title="**__No permission__**", colour=discord.Colour(0xd0021b), description=":x: You need the permission `Administrator` to use this command")
            await ctx.send(embed=embed)
        elif not ctx.guild.me.permissions_in(ctx.channel).administrator:
            embed = discord.Embed(title="**__No permission__**", colour=discord.Colour(0xd0021b), description=":x: I need the permission `Administrator` to lockdown the server")
            await ctx.send(embed=embed)
        else:
            for channel in ctx.guild.channels:
                if type(channel) == discord.TextChannel:
                    await channel.edit(overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
                elif type(channel) == discord.VoiceChannel:
                    await channel.edit(overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})
            embed = discord.Embed(title=":rotating_light: LOCKDOWN", colour=discord.Colour(0xd0021b), description="All channels are now locked!")
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="lock", description="Lock a specific channel!", options=[{"name": "channel", "description": "The channel you want to lock", "type": 7, "required": True}])
    async def _lock(self, ctx: SlashContext, channel):
        if not ctx.author.permissions_in(channel).manage_roles:
            embed = discord.Embed(title="**__No permission__**", colour=discord.Colour(0xd0021b), description=":x: You need the permission `Manage channel` to use this command")
            await ctx.send(embed=embed)
        elif not ctx.guild.me.permissions_in(channel).manage_roles:
            embed = discord.Embed(title="**__No permission__**", colour=discord.Colour(0xd0021b), description=":x: I need the permission `Manage channel` to lock this channel")
            await ctx.send(embed=embed)
        else:
            if type(channel) == discord.VoiceChannel:
                await channel.edit(overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})
            else:
                await channel.edit(overwrites={ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
            embed = discord.Embed(title=":rotating_light: Locked Channel", colour=discord.Colour(0xd0021b), description=f"Locked {channel.mention}")
            await ctx.send(embed=embed)
            

def setup(bot):
    bot.add_cog(Slash(bot))