import discord
from discord.ext import commands
import sqlite3
from FilterAndSend import filter, league_hr_send, clanhr_ffs_send, names, player_hr_send, playerga_send, war_ga
import os

conn = sqlite3.connect(os.path.join(os.getcwd(),'ffsbot.db'))
c = conn.cursor()


class ClanCommands:
    def __init__(self, bot):
        self.bot = bot

    async def clan_hrs_allwartypes(self, ctx, wartype, week):
        c.execute("SELECT oppname FROM clanhr WHERE wartype = :wartype AND week = :week", {'wartype':wartype, 'week':week})
        oppnamedump = c.fetchall()
        if len(oppnamedump) == 0:
            ctx.send(":x: No wars found with that League/War Type! To find all League/War Types, type `wars`")
        else:
            unique_clanname = list(set(oppnamedump))
            for oppname in unique_clanname:
                print('ok')
                c.execute("SELECT atttype FROM clanhr WHERE oppname = :opp", {'opp':oppname[0]})
                atttype = c.fetchall()
                unique_atttype = list(set(atttype))
                for att in unique_atttype:
                    if att[0] == 'Normal':
                        c.execute("SELECT * FROM clanhr WHERE oppname = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;", {'opp':oppname[0]})
                        dump = c.fetchall()
                        clanhr_ffs_send(dump, oppname, 'Normal')
                    if att[0] == 'Enemy':
                        c.execute(
                            "SELECT * FROM clanhr WHERE oppname = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                            {'opp': oppname[0]})
                        dump = c.fetchall()
                        clanhr_ffs_send(dump, oppname, 'Enemy')
    async def search_clan(self, ctx, warid):
        try:
            if int(warid):
                c.execute("SELECT warid FROM ffsbot WHERE warid = :warid", {'warid': warid})
                newwarid = list(set(c.fetchall()))
                print(newwarid)
                if len(newwarid) == 0:
                    await ctx.send("Invalid war id provided. Please type `waralias` to find the full list.")
        except ValueError:
            if warid.startswith('#'):
                c.execute("SELECT warid FROM ffsbot WHERE WarEnemyTag = :tag", {'tag': warid})
                newwarid = list(set(c.fetchall()))
                if len(newwarid) == 0:
                    await ctx.send("Invalid clan tag provided. Please type `waralias` to find the full list.")
            else:
                c.execute("SELECT warid FROM ffsbot WHERE WarEnemyName = :name", {'name': warid})
                newwarid = list(set(c.fetchall()))
                if len(newwarid) == 0:
                    await ctx.send("Invalid clan name provided. Please type `waralias` to find the full list.")

        if newwarid:
            for a in newwarid:
                return a[0]

    @commands.command(name="waralias", aliases=['wa', 'alias', 'warnames', 'wars', 'wartag'], description="Get all wars with respective ID/tag/league/weeks")
    async def namescmd(self, ctx):
        await names(ctx)
    @commands.command(name='clanhr', alias=['clanhitrate', 'searchclans'])
    async def warshrs(self, ctx,*, warid:str=None, enemy_us:str=None, fresh_clean:str=None, offth:str=None, defth:str=None):
        """Gives you a HR page for both offence and defensive stats of a clan. Clan name/tag parameter is mandatory.

                PARAMETERS: [opponent clan name/tag]
                EXAMPLE: `clanhr Reddit Viper` or `clanhr #QW354GRY`
                RESULT: A table of (offence and defence) HRs for the war against Reddit Viper"""
        if not warid:
            await ctx.send(":x: Please include war/clan id; ie. opponent name, tag or war id.")
        else:
            waridf = await self.search_clan(ctx, warid)
            if not enemy_us:
                enemy_us = 'all'
            if not fresh_clean:
                fresh_clean = 'all'
            if not offth:
                offth = 'all'
            if not defth:
                defth = 'all'
            enemy_us = enemy_us.lower()
            fresh_clean = fresh_clean.lower()
            offth = offth.lower()
            defth = defth.lower()
            await filter(ctx,'warid','all','all',enemy_us,fresh_clean,offth,defth, clanhr_ffs_send, warid=waridf)


    @commands.command(name="lhr", alias=['leaguehitrate', 'leaguehr', 'cwlhr'])
    async def league_hrs(self, ctx, wartype:str=None, week:str=None, enemy_us:str=None, fresh_clean:str=None, offth:str=None, defth:str=None):
        """Gives you a HR page for both offence and defensive stats of a league. The way parameters work: they are in order, and if you want one but all
        of another, set every one before it as `all`. Sorry, best way I could get it to work. League name is mandatory. All other parameters are optional.

        PARAMETERS: [leaguename] [offence/defence] [fresh/clean] [offensive TH] [defensive TH]
        EXAMPLE: `lhr cwl` or `lhr cwl offence clean all 9`
        RESULT: (1) gives all combined HRs for CWL, (2) gives all combined HRs for CWL, where attack type is offence, clean, all off TH, against TH9s."""
        if not wartype:
            await ctx.send("Please include a wartype! Eg. `lhr cwl w1` or `lhr ndl`. You can find the full list using `waralias`")
        else:
            if not week:
                week = 'all'
            if not enemy_us:
                enemy_us = 'all'
            if not fresh_clean:
                fresh_clean = 'all'
            if not offth:
                offth = 'all'
            if not defth:
                defth = 'all'
            wartype = wartype.lower()
            week = week.lower()
            enemy_us = enemy_us.lower()
            fresh_clean = fresh_clean.lower()
            offth = offth.lower()
            defth = defth.lower()
            await filter(ctx, 'oppname', wartype, week, enemy_us, fresh_clean, offth, defth, league_hr_send)
    # @bot.command(name="clanstats")
    # async def clanstats(ctx, oppname:str=None, wartype:str=None, week:str=None, enemy_us:str=None, fresh_clean:str=None, offth:str=None, defth:str=None):
    #     if not oppname:
    #         await ctx.send(":x: Please include a clan name!")
    #     else:
    #         if not week:
    #             week = 'all'
    #         if not enemy_us:
    #             enemy_us = 'all'
    #         if not fresh_clean:
    #             fresh_clean = 'all'
    #         if not offth:
    #             offth = 'all'
    #         if not defth:
    #             defth = 'all'
    #         wartype = wartype.lower()
    #         week = week.lower()
    #         enemy_us = enemy_us.lower()
    #         fresh_clean = fresh_clean.lower()
    #         offth = offth.lower()
    #         defth = defth.lower()
    #         await filter(ctx, 'oppname', wartype, week, enemy_us, fresh_clean, offth, defth, clanhr_ffs_send, oppnamefromdb=oppname)
    @commands.command(name='gwa', alias=['getwarattack', 'getwarattacks', 'warattaks', 'clanattacks', 'warhits', 'getwarhits', 'gethits'])
    async def ga_wars(self, ctx,*, warid: str = None, enemy_us: str = None, fresh_clean: str = None, offth: str = None,
                      defth: str = None):
        """Gives you all attacks, for both offence and defensive stats of a war. Opponent tag, name or warid is mandatory parameter.
                PARAMETERS: [opponent name/tag/warid]
                EXAMPLE: `gwa Reddit Viper` or `gwa 3`
                RESULT: (1) gives you all attacks for war against Reddit Viper, (2) gives all attacks against the clan with warid 3 (USA Adults)."""
        if not warid:
            await ctx.send(
                "Please include some form of id for the war: opponent tag, name or war id. To find these type `waralias`")
        else:
            waridf = await self.search_clan(ctx, warid)
            if waridf:
                if not enemy_us:
                    enemy_us = 'all'
                if not fresh_clean:
                    fresh_clean = 'all'
                if not offth:
                    offth = 'all'
                if not defth:
                    defth = 'all'
                enemy_us = enemy_us.lower()
                fresh_clean = fresh_clean.lower()
                offth = offth.lower()
                defth = defth.lower()
                await filter(ctx, 'warid', 'all', 'all', enemy_us, fresh_clean, offth, defth,
                             war_ga, warid=waridf)


def setup(bot):
    bot.add_cog(ClanCommands(bot))
