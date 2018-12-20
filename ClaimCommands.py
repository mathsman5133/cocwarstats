import discord
from discord.ext import commands
import sqlite3
from coc import ClashOfClans
from FilterAndSend import filter, league_hr_send, clanhr_ffs_send, names, player_hr_send, playerga_send, war_ga
from creds import coctoken
import paginator
import os

conn = sqlite3.connect(os.path.join(os.getcwd(),'ffsbot.db'))
c = conn.cursor()
coc = ClashOfClans(coctoken)

class ClaimCommands:
    def __init__(self, bot):
        self.bot = bot
    def try_playertag(self, playertag):
        get = coc.players(playertag).get()
        try:
            a = get['name']
            return
        except:
            return ('Playertag: ' + get['reason'])

    def find_playertag(self, playertag):
        c.execute("SELECT ign, userid FROM claims WHERE tag = :tag", {'tag': playertag})
        dump = c.fetchall()
        print(dump)
        return (dump)

    @commands.command(name="claim", alias=['identify', 'c'], description="Claim your account (tag or IGN)")
    async def claim_player(self, ctx, playertag: str = None, user: discord.User = None):
        """Claims/links your clash of clans account to your discord ID. Mandatory for using any stat personal stat commands.
        Claim someone else's account for them by adding a ping at end.
        PARAMETERS: [playertag] [@MENTION - optional]
        EXAMPLE: `claim #123ADSJF` or `claim #123ADSFC @mathsman`
        RESULT: Adds claim to databse and returns result."""

        if not playertag:
            await ctx.send("Please include a player tag!\n")
        if self.try_playertag(playertag):
            await ctx.send(f"Playertag error: {self.try_playertag(playertag)}")
        dbinfo = self.find_playertag(playertag)
        print(dbinfo)
        if dbinfo:
            for indiv in dbinfo:
                dbuser = self.bot.get_user(indiv[1]) or (await self.bot.get_user_info(indiv[1]))
                await ctx.send(f"{indiv[0]} has already been claimed by {dbuser.name}#{dbuser.discriminator}!\n")
        else:
            foruser = user or ctx.author
            cocinfo = coc.players(playertag).get()
            ign = cocinfo['name']
            c.execute("INSERT INTO claims VALUES (:id, :ign, :tag, :prim)",
                      {'id': foruser.id, 'tag': playertag, 'ign': ign, 'prim': None})
            conn.commit()
            await ctx.send(f"You have claimed {ign} for {foruser.name}#{foruser.discriminator}")

    @commands.command(name='del', alias=['delete', 'delclaim', 'deleteclaim', 'remove', 'release'], description="Delete claimed account")
    async def delete_player(self, ctx, playertag: str = None):
        """Deletes a claimed account from the database. You must be LT to delete someone else's.

        PARAMETERS: [playertag/IGN]
        EXAMPLE: `del #A78JH32G` or `del mathsman`
        RESULT: Deletes player from DB and returns result.
        """
        if not playertag:
            await ctx.send("Please include a player tag!\n")
        dbinfo = self.find_playertag(playertag)
        if self.try_playertag(playertag):
            await ctx.send(f"Playertag error: {self.try_playertag(playertag)}")
        else:
            cocinfo = coc.players(playertag).get()
            ign = cocinfo['name']
        if not dbinfo:
            await ctx.send(f"Could not find {ign} in the database.")
        else:
            c.execute(f"DELETE FROM claims WHERE tag = :tag", {'tag': playertag})
            conn.commit()
            await ctx.send(f"Successfully deleted {ign}")

    @commands.command(name='primary', alias=['setprim', 'prim', 'setprimary', 'setmain'], description="Set primary account for stat commands")
    async def primary_acct(self, ctx, playertag: str = None):
        """Sets an account as a primary account. It must be already claimed. This will reduce spam when using `hr` and `ga` commands,
        showing only the hr or attacks for this account. To see other accounts, use `ga #PLAYERTAG` or `hr [IGN]`

        PARAMETERS: [playertag/IGN]

        EXAMPLE: `primary mathsman` OR `primary #JQ78G5D`
        RESULT: Adds account to database and returns result."""
        userinfo = ctx.author
        if playertag.startswith('#'):
            c.execute("SELECT tag FROM claims WHERE userid = :id AND tag = :tag", {'id': userinfo.id, 'tag': playertag})
            dump = c.fetchall()
            if len(dump) == 0:
                await ctx.send("Playertag was not found in the database. To see all tags, type `gc`")
                return
        else:
            c.execute("SELECT tag FROM claims WHERE userid = :id AND tag = :tag", {'id': userinfo.id, 'tag': playertag})
            dump = c.fetchall()
            if len(dump) == 0:
                await ctx.send("IGN was not found in the database. To see all IGNs, please type `gc`")
                return
        c.execute("SELECT prim FROM claims WHERE userid = :id", {'id': userinfo.id})
        fetch_prim = c.fetchall()
        for prim in fetch_prim:
            if prim[0]:
                print(prim)
                c.execute("SELECT ign FROM claims WHERE prim = :prim", {'prim':prim[0]})
                a = c.fetchall()
                for b in a:
                    ign = b[0]
                await ctx.send(
                    f"Your primary account is already set to: {ign} ({playertag}). To remove this, use `delprim`")
                return
        if dump:
            c.execute("UPDATE claims SET prim = :prim WHERE userid = :id AND tag = :tag",
                      {'prim': playertag, 'id': userinfo.id, 'tag': playertag})
            conn.commit()
            c.execute("SELECT ign FROM claims WHERE tag = :playertag", {'playertag': playertag})
            a = c.fetchall()
            for b in a:
                ign = b[0]
            await ctx.send(
                f"You have added {ign} ({playertag}) as your primary account. For `myga` or `myhr` commands, you will only receive info for {ign}")
            print('done')
    @commands.command(name="delprim", alias=['deleteprimary', 'delprimary', 'deletemain', 'delmain'], description="Delete primary account")
    async def delete_prim(self, ctx):
        """Deletes your primary account. You must have an account set as a primary account. Takes no parameters
        PARAMETERS: None
        EXAMPLE: `delprim`
        RESULT: Deletes primary attachment from DB and returns result"""
        c.execute("SELECT prim FROM claims WHERE userid = :id", {'id': ctx.author.id})
        dump = list(set(c.fetchall()))
        for a in dump:
            if not a[0]:
                await ctx.send(
                    "You dont have any accounts set as primary accounts! To do this, type `prim #PLAYERTTAG`")
            else:
                c.execute("UPDATE claims SET prim = :prim WHERE userid = :id", {'id': ctx.author.id, 'prim': None})
                conn.commit()
                await ctx.send("Successfully deleted primary account")

    @commands.command(name="myc", alias=['myclaims', 'myaccounts', 'accounts', 'mybases', 'mc'], description="Shows your claimed accounts")
    async def my_claims(self, ctx):
        """Show all accounts linked to your discord id. Also shows primary account (if applicable); Takes no parameters.
        PARAMETERS: None
        EXAMPLE: `myc`
        RESULT: Lists claimed account IGN and Tag."""
        msg = ''
        c.execute("SELECT prim FROM claims WHERE userid = :id", {'id':ctx.author.id})
        a = c.fetchall()
        for dump in a:
            if dump:
                c.execute("SELECT tag, ign FROM claims WHERE prim =:prim", {'prim': dump[0]})
                b = c.fetchall()
                for f in b:
                    msg += '{:>10}'.format(f[1])
                    msg += '{:>14}'.format(f[0])
                    msg += '{:>10}'.format('TRUE')
                    msg += '\n'
        c.execute("SELECT tag, ign FROM claims WHERE userid = :id AND prim is null",
                  {'id': ctx.author.id, 'prim':None})
        d = c.fetchall()
        for ab in d:
            msg += '{:>10}'.format(ab[1])
            msg += '{:>14}'.format(ab[0])
            msg += '\n'
        print(msg, d)
        await ctx.send(
            "```(Un)Claimed accounts in the database \n\n{:>10}{:>14}{:>10}\n---------------------------------------------------------------\n".format(
                'IGN', 'Tag', 'Primary') + msg + '```')

    @commands.command(name="gc", alias=['getclaims', 'getclaim', 'gcs', 'gclaim', 'gclaims', 'accounts', 'names', 'getnames',
                                   'clantags'], description="Shows all players in DB")
    async def get_claims(self, ctx):
        """Gets all accounts in the database and returns them with IGN, tag and linked discord (if applicable)
        PARAMETERS: None
        EXAMPLE: `gc`
        RESULT: Returns all FFS accounts in database."""
        c.execute("SELECT AttackerName, AttackerClanMemberMemberTag FROM ffsbot WHERE AttackerType = 'Normal'")
        unique = list(set(c.fetchall()))
        print(unique)
        msg = []

        user = ctx.author
        for db in unique:
            c.execute("SELECT userid FROM claims WHERE tag = :tag", {'tag': db[1]})
            dump = list(set(c.fetchall()))
            for a in dump:
                dbuser = self.bot.get_user(a[0]) or (await self.bot.get_user_info(a[0]))
            if len(dump) == 0:
                line = ''
                line += '{:>18}'.format(db[0])
                line += '{:>14}'.format(db[1])
                msg.append(line + '\n')
            else:
                line = ''
                line += '{:>18}'.format(db[0])
                line += '{:>14}'.format(db[1])
                line += '{:>20}'.format(dbuser.name + '#'+ dbuser.discriminator)
                msg.append(line + '\n')
        to_del = []
        header = ('```(Un)Claimed accounts in the database \n\n{:>18}{:>14}{:>20}'.format('IGN', 'Tag',
                                                                                          'Discord') + '```')
        to_del.append(await ctx.send(header))
        try:
            page = 1
            pages = paginator.MsgPag(ctx, message=ctx.message, entries=msg, per_page=30)
            await pages.paginate(start_page=page, to_del=to_del)
        except paginator.CannotPaginate as e:
            await self.bot.say(str(e))

def setup(bot):
    bot.add_cog(ClaimCommands(bot))