import discord
from discord.ext import commands
import sqlite3
from FilterAndSend import filter, league_hr_send, clanhr_ffs_send, names, player_hr_send, playerga_send, war_ga
import paginator
conn = sqlite3.connect('ffsbot.db')
c = conn.cursor()


class PlayerCommands:
    def __init__(self, bot):
        self.bot = bot
    async def search_claims(self, ctx, cmd, user: discord.User = None):
        c.execute("SELECT prim FROM claims WHERE userid = :id AND prim is not null", {'id': user.id})
        dump = c.fetchall()
        len1 = len(dump)
        if not dump:
            c.execute("SELECT tag FROM claims WHERE userid = :id", {'id': user.id})
            dump = c.fetchall()
        leng = len(dump)
        if leng == 0:
            if cmd == 'm':
                await ctx.send(f"No accounts claimed! Relevant command: `claim #PLAYERTAG`")
            if cmd == 'p':
                await ctx.send(
                    f"{user.name} doesn't have any accounts claimed! Relevant command: `claim #PLAYERTAG <@{user.id}>`")
        else:
            if len1 == 0:
                if cmd == 'm':
                    await ctx.send(
                        f"You do not have a primary account selected; you will have {str(leng*2)} messages of attacks to sort through")
                if cmd == 'p':
                    await ctx.send(
                        f"{user.name} does not have a primary account selected; you will have {str(leng*2)} messages of attacks to sort through")

            for db in dump:
                print(db)
                c.execute("SELECT ign FROM claims WHERE tag = :tag", {'tag': db[0]})
                ign1 = c.fetchall()
                for ign in ign1:
                    if len1 > 1:
                        if cmd == 'm':
                            await ctx.send(
                                f"You have {db[1]} selected as the primary account. You will only get attacks of this account.")
                        if cmd == 'p':
                            await ctx.send(
                                f"{user.name} has {db[1]} selected as the primary account. You will only get attacks of this account. If you want others, use `ga IGN` or `ga #PLAYERTAG`")
            return dump

    @commands.command(name="hr", alias=['hitrate', 'searchhr', 'findhr', 'hrs'])
    async def player_hrs(self, ctx,*, playertag: str = None, enemy_us: str = None, fresh_clean: str = None, offth: str = None,
                         defth: str = None):
        """Gives you a HR page for both offence and defensive stats of a player.

        PARAMETERS: playertag [mandatory: ign or tag]
        EXAMPLE: `hr #PLD65GJ` or `hr mathsman`
        RESULT: Returns a HR table."""
        week = 'all'
        wartype = 'all'
        if not playertag.startswith('#'):
            c.execute("SELECT AttackerClanMemberMemberTag FROM ffsbot WHERE AttackerName = :name", {'name': playertag})
            a = list(set(c.fetchall()))
            for b in a:
                playertag = b[0]
        if not playertag:
            await ctx.send(
                "Please include a player tag! Use `mhr` for personal attacks, or `phr @MENTION` for someone else's")
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
            await filter(ctx, 'playerhr', wartype, week, enemy_us, fresh_clean, offth, defth, player_hr_send,
                         playertagfromdb=playertag)

    @commands.command(name="phr", alias=['pinghr', 'hrping', 'pinghitrate'])
    async def ping_hr(self, ctx, user: discord.User = None, enemy_us: str = None, fresh_clean: str = None, offth: str = None,
                      defth: str = None):
        """Gives you a HR page for both offence and defensive stats of assosiated accounts to the member you ping. The way parameters:
        work they are in order, and if you want one but all
        of another, set every one before it as `all`.
        Sorry, best way I could get it to work. Ping is mandatory. All other parameters are optional.
        Best way to think about it is like a filter. No parameters (aside from @) gives everything, anything after that restricts it.

        PARAMETERS: [@MENTION] [offence/defence] [fresh/clean] [offensive TH] [defensive TH]

        EXAMPLE: `phr @mathsman` or `phr @mathsman normal fresh all 9`

        RESULT: Returns a HR table for all stats of mathsman's accounts (1) or only offensive, fresh hits against TH9s for mathsman's accounts (2) ."""
        a = await self.search_claims(ctx, 'p', user)
        if a:
            for tag in a:
                if not enemy_us:
                    enemy_us = 'all'
                if not fresh_clean:
                    fresh_clean = 'all'
                if not offth:
                    offth = 'all'
                if not defth:
                    defth = 'all'
                enemy_us = enemy_us.lower()
                if enemy_us == 'offence':
                    enemy_us = 'Normal'
                if enemy_us == 'defence':
                    enemy_us = 'Enemy'
                fresh_clean = fresh_clean.lower()
                offth = offth.lower()
                defth = defth.lower()
                await filter(ctx, 'playerhr', 'all', 'all', enemy_us, fresh_clean, offth, defth, player_hr_send,
                             playertagfromdb=tag[0])

    @commands.command(name="mhr", alias=['myhr', 'myhitrate', 'mystats'])
    async def my_hr(self, ctx, enemy_us: str = None, fresh_clean: str = None, offth: str = None,
                    defth: str = None):
        """Gives you a HR page for both offence and defensive stats of your assosiated accounts.The way parameters
                work: they are in order, and if you want one but all
                of another, set every one before it as `all`.

                Sorry, best way I could get it to work. All  parameters are optional.

                Best way to think about it is like a filter. No parameters gives every stat, anything after that restricts them.

                PARAMETERS:  [enemy/normal] [fresh/clean] [offensive TH] [defensive TH]

                EXAMPLE: `mhr` or `mhr normal fresh all 9`
                RESULT: Returns a HR table for all stats of your accounts (1) or only offensive, fresh hits against TH9s for your accounts (2) ."""
        a = await self.search_claims(ctx, 'm', user=ctx.author)
        if a:
            for tag in a:
                if not enemy_us:
                    enemy_us = 'all'
                if not fresh_clean:
                    fresh_clean = 'all'
                if not offth:
                    offth = 'all'
                if not defth:
                    defth = 'all'
                enemy_us = enemy_us.lower()
                if enemy_us == 'offence':
                    enemy_us = 'Normal'
                if enemy_us == 'defence':
                    enemy_us = 'Enemy'
                fresh_clean = fresh_clean.lower()
                offth = offth.lower()
                defth = defth.lower()
                await filter(ctx, 'playerhr', 'all', 'all', enemy_us, fresh_clean, offth, defth, player_hr_send,
                             playertagfromdb=tag[0])

    @commands.command(name='ga', alias=['getattacks', 'getattack', 'gethits', 'gethit', 'hits'])
    async def ga_players(self, ctx, *,playertag: str = None, enemy_us: str = None, fresh_clean: str = None, offth: str = None,
                         defth: str = None):
        """Gives you all attacks, both offence and defensive of a player.

                PARAMETERS: playertag [mandatory: ign or tag]

                EXAMPLE: `ga #PLD65GJ` or `ga mathsman`
                RESULT: Returns a list of all attacks in database."""

        week = 'all'
        wartype = 'all'
        if not playertag.startswith('#'):
            print('ya')
            c.execute("SELECT AttackerClanMemberMemberTag FROM ffsbot WHERE AttackerName = :name", {'name': playertag})
            a = list(set(c.fetchall()))
            for b in a:
                playertag = b[0]
        if not playertag:
            await ctx.send(
                "Please include a player tag! Use `ga` for personal attacks, or `ga @MENTION` for someone else's")
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
            if enemy_us == 'offence':
                enemy_us = 'Normal'
            if enemy_us == 'defence':
                enemy_us = 'Enemy'
            fresh_clean = fresh_clean.lower()
            offth = offth.lower()
            defth = defth.lower()
            await filter(ctx, 'playerga', wartype, week, enemy_us, fresh_clean, offth, defth, playerga_send,
                         playertagga=playertag)
            await filter(ctx, 'playergd', wartype, week, enemy_us, fresh_clean, offth, defth,
                         playerga_send, playertagga=playertag)

    @commands.command(name='myga', alias=['myattacks', 'myhits'])
    async def my_ga(self, ctx, enemy_us: str = None, fresh_clean: str = None, offth: str = None, defth: str = None):
        """Gives you all attacks, for both offence and defensive stats of your claimed accounts. The way parameters
                        work: they are in order, and if you want one but all
                        of another, set every one before it as `all`.

                        Sorry, best way I could get it to work. All  parameters are optional.

                        Best way to think about it is like a filter. No parameters gives every stat, anything after that restricts them.

                        PARAMETERS:  [offence/defence] [fresh/clean] [offensive TH] [defensive TH]

                        EXAMPLE: `myga` or `@mathsman normal fresh all 9`
                        RESULT: Returns a list of all attacks of mathsman's accounts (1) or only offensive, fresh hits against TH9s for mathsman's accounts (2) ."""
        a = await self.search_claims(ctx, 'm', ctx.author)
        for tag in a:
            if tag[0]:
                if not enemy_us:
                    enemy_us = 'all'
                if not fresh_clean:
                    fresh_clean = 'all'
                if not offth:
                    offth = 'all'
                if not defth:
                    defth = 'all'
                enemy_us = enemy_us.lower()
                if enemy_us == 'offence':
                    enemy_us = 'Normal'
                if enemy_us == 'defence':
                    enemy_us = 'Enemy'
                fresh_clean = fresh_clean.lower()
                offth = offth.lower()
                defth = defth.lower()
                await filter(ctx, 'playerga', 'all', 'all', enemy_us, fresh_clean, offth, defth, playerga_send,
                             playertagga=tag[0])
                await filter(ctx, 'playergd', 'all', 'all', enemy_us, fresh_clean, offth, defth,
                             playerga_send, playertagga=tag[0])

    @commands.command(name='gpa', alias=['pinghits', 'getattacksping'])
    async def ga_ping(self, ctx, user: discord.User = None, enemy_us: str = None, fresh_clean: str = None, offth: str = None,
                      defth: str = None):
        """Gives you all attacks, for both offence and defensive stats of assosiated accounts to the member you ping. The way parameters:
        work they are in order, and if you want one but all
        of another, set every one before it as `all`.
        Sorry, best way I could get it to work. Ping is mandatory. All other parameters are optional.
        Best way to think about it is like a filter. No parameters (aside from @) gives everything, anything after that restricts it.

        PARAMETERS: [@MENTION] [offence/defence] [fresh/clean] [offensive TH] [defensive TH]

        EXAMPLE: `gpa @mathsman` or `gpa @mathsman normal fresh all 9`

        RESULT: Returns all attacks for mathsman's accounts (1) or only offensive, fresh hits against TH9s for mathsman's accounts (2) ."""
        a = await self.search_claims(ctx, 'p', user)
        if a:
            for tag in a:
                if not enemy_us:
                    enemy_us = 'all'
                if not fresh_clean:
                    fresh_clean = 'all'
                if not offth:
                    offth = 'all'
                if not defth:
                    defth = 'all'
                enemy_us = enemy_us.lower()
                if enemy_us == 'offence':
                    enemy_us = 'Normal'
                if enemy_us == 'defence':
                    enemy_us = 'Enemy'
                fresh_clean = fresh_clean.lower()
                offth = offth.lower()
                defth = defth.lower()
                await filter(ctx, 'playerga', 'all', 'all', enemy_us, fresh_clean, offth, defth, playerga_send,
                             playertagga=tag[0])
                await filter(ctx, 'playergd', 'all', 'all', enemy_us, fresh_clean, offth, defth,
                             playerga_send, playertagga=tag[0])

def setup(bot):
    bot.add_cog(PlayerCommands(bot))
