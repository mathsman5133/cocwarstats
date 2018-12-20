import discord
from discord.ext import commands
import sqlite3
from coc import ClashOfClans
from creds import coctoken
from FilterAndSend import filter, league_hr_send, clanhr_ffs_send, names, player_hr_send, playerga_send, war_ga

conn = sqlite3.connect('ffsbot.db')
c = conn.cursor()
coc = ClashOfClans(coctoken)

class DownloadCommands:
    def __init__(self, bot):
        self.bot = bot
    async def dl_set(self, ctx, wartype, week):
        roles = ctx.message.author.roles
        testyes = ''
        testno = ''
        for role in roles:
            if role.name == 'FFS Bot Command':
                testyes += '!'
        if testyes == '!':
            war = coc.clans('#RGRCYRGR').currentwar.get()
            try:
                state = war['state']
                try:
                    oppname = war['opponent']['name']
                    opptag = war['opponent']['tag']
                    c.execute(
                        "SELECT * FROM toggle WHERE wartype = :type AND opponent = :opp AND week = :week AND toggle = 1",
                        {'type': wartype, 'opp': opptag, 'week': str(week)})
                    dump = c.fetchall()
                    if len(dump) != 0:
                        await ctx.send("Someone has already initiated logging of this war.")
                    else:
                        if state == 'preparation' or 'inWar' or 'warEnded':
                            print('yes')

                            with conn:
                                c.execute("SELECT * FROM toggle WHERE opponent=:opp AND toggle=0", {'opp': opptag})
                                if len(c.fetchall()) == 0:
                                    c.execute("SELECT MAX(warid) FROM ffsbot")
                                    a = c.fetchall()
                                    for b in a:
                                        warid = b[0] + 1
                                    c.execute("INSERT INTO toggle VALUES (:toggle, :wartype, :week, :opponent, :warid)",
                                              {'toggle': 1, 'wartype': wartype, 'week': str(week), 'opponent': opptag, 'warid':warid})

                                else:
                                    c.execute(
                                        "UPDATE toggle SET toggle= 1, wartype= :wartype, week= :week WHERE opponent= :opp",
                                        {'opp': opptag, 'wartype': wartype, 'week': str(week)})
                            if state == 'preparation':
                                await ctx.send(
                                    'Your clan is currently in preperation against ' + oppname + '. Good Luck! Attacks will download when battle day starts until the war has finished. In order for the final data pull and upload to the clan spreadsheet, please ensure you do not spin until the bot has reported that csv has been downloaded and uploaded to sheets, and the stats have been downloaded. If this has not happened within 10-15min, please ping maths to fix it. Thanks!')
                            if state == 'inWar':
                                await ctx.send(
                                    'Your clan is currently in battle day against ' + oppname + '. Good Luck! Attacks will start downloading from now until the war finishes. In order for the final data pull and upload to the clan spreadsheet, please ensure you do not spin until the bot has reported that csv has been downloaded and uploaded to sheets, and the stats have been downloaded. If this has not happened within 10-15min, please ping maths to fix it. Thanks!')
                            if state == 'warEnded':
                                await ctx.send(
                                    "War has ended! Attacks will download as fast as they can; I will let you know when this is completed")
                except KeyError:
                    if state == 'notInWar':
                        await ctx.send(
                            "It appears your clan is not currently in war! If you just spun, please wait 10-15min for the API to register the war. If the war has finished and you tried to spin and stopped, please ping maths to download the war from warmatch. In order to pull stats from the API, you must be in preperation, battle day, or the war has just ended.")
            except KeyError:
                try:
                    reason = war['reason']
                    await ctx.send(
                        "<@230214242618441728>, error because " + reason + ". Please be patient until maths can fix.")
                except KeyError:
                    await ctx.send("Unknown error. Please wait about 10min or ping maths for help.")
        else:
            await ctx.send(
                'You do not have the required role of: FFS Bot Command. Please message leadership if you require this role. Downloading of wars has not commenced; ping someone who can download if warlogging needs to be started.')

    @commands.command(name='dl')
    @commands.has_role("FFS Bot Command")
    async def dlcmd(self, ctx, wartype: str = None, week: str = None):
        print(str(wartype) + str(week))
        if wartype:
            wartype = wartype.lower()
        if week:
            week = week.lower()
        war = coc.clans('#RGRCYRGR').currentwar.get()
        if not wartype:
            await ctx.send(
                "Please have a war type as your first argument: eg. `dl CWL W1` to download a CWL Week1 war, or `dl NDL W10` to download a Week10 NDL war.")
        if not week:
            if wartype == 'aw':
                await dl_set(ctx, wartype, week)
            else:
                await ctx.send(
                    'You have not included a week argument, and the wartype is not `AW`! If it is an arranged war, and not a league war with weeks, please type `dl AW` to download current war as an arranged war. If you require more options for wartypes, please tell maths.')
        if week:
            if week == 'placement':
                await dl_set(ctx, wartype, week)
            else:
                if not week.startswith('w'):
                    await ctx.send(
                        "The week arguement has been phrased incorrectly. It should be `W1` for Week1, or `w9` for Week9, or `Placement` for a placement match.")
                if not week[1].isdigit():
                    await ctx.send(
                        "The week arguement has been phrased incorrectly. It should be `W1` for Week1, or `w9` for Week9.")
                else:
                    await dl_set(ctx, wartype, week)
    @commands.command(name='stopdl')
    @commands.has_role("FFS Bot Command")
    async def stopdlcmd(self, ctx):
        c.execute("SELECT * FROM toggle")
        war = coc.clans('#RGRCYRGR').currentwar.get()
        try:
            opptag = war['opponent']['tag']
            oppname = war['opponent']['name']
            c.execute("SELECT * FROM toggle WHERE opponent=:opp AND toggle=1", {'opp': opptag})
            dump = c.fetchall()
            if len(dump) != 0:
                c.execute("UPDATE toggle SET toggle=0 WHERE opponent = :opp AND toggle = 1", {'opp': opptag})
                conn.commit()
                await ctx.send('Downloading of the war against {} has been stopped.'.format(oppname))
            else:
                await ctx.send("Could not find a war currently downloading against: " + oppname + "!")
        except KeyError:
            try:
                reason = war['reason']
                await ctx.send(
                    '<@230214242618441728>, error because ' + reason + '. Please be patient until maths can fix it.')
            except KeyError:
                await ctx.send("Your clan is not currently in war!")



def setup(bot):
    bot.add_cog(DownloadCommands(bot))
