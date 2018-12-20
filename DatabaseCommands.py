import discord
from discord.ext import commands
from DownloadWar import set_fresh_clean, add_leagues, add_playerhrs, add_clanhrs
import traceback
import sqlite3
import asyncio

conn = sqlite3.connect('ffsbot.db')
c = conn.cursor()
class DatabaseCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addleagues")
    @commands.has_role("FFS Bot Command")
    async def add_leagues_hr(self, ctx):
        """Adds/updates league stats to the DB. This should automatically happen at the end of the war, unless you didn't wait 10-15min and the API didn't catch
        the end of the war. This affects the `lhr` command.
        PARAMETERS: []
        EXAMPLE: `addleagues`
        RESULT: updates league HRs in DB."""
        try:
            add_leagues()
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @commands.command(name="addplayerhr")
    @commands.has_role("FFS Bot Command")

    async def add_player_hrs(self, ctx):
        """Adds/updates player stats to the DB. This should automatically happen at the end of the war, unless you didn't wait 10-15min and the API didn't catch
        the end of the war. This affects the `hr`, `mhr` and `phr` commands.
        PARAMETERS: []
        EXAMPLE: `addplayerhr`
        RESULT: updates player HRs in DB."""
        try:
            add_playerhrs()
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @commands.command(name="addclanhrs")
    @commands.has_role("FFS Bot Command")

    async def add_clan_hrs(self, ctx, warid:int=None):
        """Adds/updates clan stats to the DB. This should automatically happen at the end of the war, unless you didn't wait 10-15min and the API didn't catch
        the end of the war. This affects the `clanhr` command.
        PARAMETERS: [warid - not name/tag, but the integer id]
        EXAMPLE: `addclanhrs`
        RESULT: updates player HRs in DB."""
        if not warid:
            await ctx.send("Please include a war id - not enemy name or tag, but the integer found by using `waralias`")
            return
        try:
            info = self.find_warid(self, warid)
            add_clanhrs(info[2], info[3], info[0], info[1])
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @commands.command(name="addfreshclean")
    @commands.has_role("FFS Bot Command")

    async def add_fresh_clean(self, ctx, warid:int):
        """Sets attacks from war as either fresh or clean. This should automatically happen at the end of the war, unless you didn't wait 10-15min and the API didn't catch
        the end of the war. This affects the all stat commands.
        PARAMETERS: []
        EXAMPLE: `addfreshclean`
        RESULT: adds attacks as either fresh or clean"""
        if not warid:
            await ctx.send("Please include a war id - not enemy name or tag, but the integer found by using `waralias`")
            return
        try:
            set_fresh_clean(warid)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    def find_warid(self, warid):
        c.execute("SELECT WarType, WarEnd, WarEnemyTag, WarEnemyName FROM ffsbot WHERE warid = :warid", {'warid':warid})
        a = c.fetchall()
        for b in a:
            return b


    @commands.command(name="updatestats")
    @commands.has_role("FFS Bot Command")

    async def update_stats(self, ctx, warid:int=None):
        """Updates all stats for a war. Only use this if the war has finished and you spun and it didnt happen automatically (as it should).
                his affects the all stat commands.
                PARAMETERS: [warid - not name/tag, but the integer id]
                EXAMPLE: `updatestats`
                RESULT: adds league, player and clanhrs. Adds fresh/clean hits."""
        if not warid:
            await ctx.send("Please include a war id - not enemy name or tag, but the integer found by using `waralias`")
            return
        try:
            info = self.find_warid(warid)
            add_clanhrs(info[2], info[3], info[0], info[1])
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        try:
            add_playerhrs()
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        try:
            add_leagues()
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        try:
            set_fresh_clean(warid)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        await ctx.send("All done. Please don't spin too soon in future")

def setup(bot):
    bot.add_cog(DatabaseCommands(bot))
