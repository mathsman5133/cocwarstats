import sqlite3
import paginator
import aiosqlite
db_path = 'C:/py/ffsbot/ffsbot.db'
#conn = sqlite3.connect('ffsbot.db')
#c = conn.cursor()

class FilterAndSend:
    def __init__(self):
        return

async def clanhr_ffs_send(ctx, dump, oppname, enemy_ffs):
    embed = []
    print(dump)
    clans = []
    for ab in dump:
        clans.append(ab[1])
    print(enemy_ffs)
    clannames = list(set(clans))
    for clanname in clannames:
        embed.append(
            'FFS vs {} ({} Stats)\n{:>0}{:>12}{:>12}{:>12}{:>12}{:>12}{:>12} \n-------------------------------------------------------------------------------\n'.format(
                clanname, enemy_ffs, 'Attack', 'Fresh/Clean', '**2**', '***3***', 'Total', '**2HR**', '***3HR***'))
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT * FROM clanhr WHERE oppname = :opp AND atttype = :type AND totatt != 0 ORDER BY offth, defth;", {'opp':clanname, 'type':enemy_ffs})
            fetch = await c.fetchall()
            await c.close()
        def fill(number):
            for int in range(number):
                embed.append('')
        for info in fetch:
            print(info)
            if info[5] == 9:
                if info[6] == 9:
                    offth = '  9'
                else:
                    offth = ' {}'.format(info[5])
            else:
                offth = str(info[5])
            if info[6] == 9:
                if info[5] != 9:
                    offth = ' {}'.format(info[5])
            line = ''
            line += '{:>0}'.format(offth + "v" + str(info[6]))
            line += '{:>12}'.format(info[4])
            line += '{:>12}'.format(info[10])
            line += '{:>12}'.format(info[9])
            line += '{:>12}'.format(info[8])
            line += '{:>12}%'.format(info[12])
            line += '{:>12}%'.format(info[11]) + '\n'
            embed.append(line)
        length = len(fetch)
        dif = 20-length
        fill(dif)
    try:
        page = 1
        pages = paginator.MsgPag(ctx, message=ctx.message, entries=embed, per_page=21)
        await pages.paginate(start_page=page)
    except paginator.CannotPaginate as e:
        await ctx.send(str(e))


async def war_summary(ctx, warid):
    async with aiosqlite.connect(db_path) as db:
        c = await db.execute("SELECT oppname FROM warsum WHERE warid = :id", {'id':warid})
        oppname1 = await c.fetchall()
        await c.close()
    for oppname in oppname1:
        oppname = oppname

    send = ''
    send += f'ForgedFromSteel vs {oppname} \nWartype: {wartype}\nWeek:{week}\n```'
    send += f'{ourstars}' + ':^16'.format('Stars') + '{:>32}'.format(oppstars)



async def names(ctx):
    async with aiosqlite.connect(db_path) as db:
        c = await db.execute("SELECT WarEnemyTag, WarEnemyName, WarType, WarEnd, warid FROM ffsbot")
        unique = list(set(await c.fetchall()))
        c = await db.execute("SELECT warid FROM ffsbot")
        fetch = list(set(await c.fetchall()))
    embed = []
    embed.append("Clans and leagues in the DB with abbreviations\n{:>10}{:>20}{:>14}{:>14}{:>14}\n--------------------------------------------------------------------------------\n".format('Tag', 'Name', 'League', 'Week', 'WarId'))
    def fill(number):
        for int in range(number):
            embed.append('')
    for clan in unique:
        msg_clans = ''
        msg_clans += '{:>10}'.format(clan[0])
        msg_clans += '{:>20}'.format(clan[1])
        msg_clans += '{:>14}'.format(clan[2])
        msg_clans += '{:>14}'.format(clan[3])
        msg_clans += '{:>14}'.format(clan[4]) + '\n'
        embed.append(msg_clans)
    length = len(fetch)
    dif = 20-length
    fill(dif)
    try:
        page = 1
        pages = paginator.MsgPag(ctx, message=ctx.message, entries=embed, per_page=21)
        await pages.paginate(start_page=page)
    except paginator.CannotPaginate as e:
        await ctx.send(str(e))


async def league_hr_send(ctx, dump, league, enemy_ffs):
    if enemy_ffs == 'Normal':
        other = 'Defence '
    if enemy_ffs == 'Enemy':
        other = 'Offence '
    print('yes')
    async with aiosqlite.connect(db_path) as db:
        c = db.execute("SELECT dif FROM leaguehr")
        fetch = list(set(await c.fetchall()))
        await c.close()
    embed1 = []
    header = (
        '```{} League ({} Stats)\n\nTo see {}attacks, or another league, please press ⏹ reaction.\n\n{:>5}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}\n---------------------------------------------------------------------\n```'.format(
            league[0], enemy_ffs, other, 'Attack', 'Fresh/Clean', '**2**', '***3***', 'Total', '**2HR**', '***3HR***'))
    def fill(number):
        for int in range(number):
            embed1.append('')
    for info in dump:
        line = ''
        line += '{:>5}'.format(str(info[2]) + "v" + str(info[3]))
        line += '{:>10}'.format(info[1])
        line += '{:>10}'.format(info[7])
        line += '{:>10}'.format(info[6])
        line += '{:>10}'.format(info[5])
        line += '{:>10}%'.format(info[9])
        line += '{:>10}%'.format(info[8]) + '\n'
        embed1.append(line)
    to_del = []
    length = len(fetch)
    dif = 15-length
    fill(dif)
    to_del.append(await ctx.send(header))
    try:
        page = 1
        pages = paginator.MsgPag(ctx, message=ctx.message, entries=embed1, per_page=15)
        await pages.paginate(start_page=page, to_del=to_del)
    except paginator.CannotPaginate as e:
        await ctx.send(str(e))


async def player_hr_send(ctx, dump, playertag, enemy_ffs):
    print('got')
    if enemy_ffs == 'Normal':
        enemy_ffs = 'Offence '
        other = 'Defence '
    if enemy_ffs == 'Enemy':
        enemy_ffs = 'Defence '
        other = 'Offence '
    async with aiosqlite.connect(db_path) as db:
        c = await db.execute("SELECT playername FROM playerhr WHERE playertag = :tag", {'tag':playertag[0]})
        names = list(set(await c.fetchall()))
        c = await db.execute("SELECT playertag FROM playerhr WHERE playertag = :tag", {'tag':playertag[0]})
        fetch = await c.fetchall()
        await c.close()
    for name1 in names:
        name = name1[0]
    header = '```Player: {} {} Stats\n\n{:>0}{:>12}{:>10}{:>10}{:>10}{:>10}{:>10} \n-------------------------------------------------------------------------------```'.format(
        name + ' (' + playertag[0] + '),', enemy_ffs, 'Attacks', 'Fresh/Clean', '**2**', '***3***', 'Total', '**2HR**', '***3HR***')
    embed1 = []
    to_delete = []
    to_delete.append(await ctx.send(header))
    for info in dump:
        if info[3] == 9:
            if info[4] == 9:
                offth = '  9'
            else:
                offth = ' {}'.format(info[3])

        else:
            offth = str(info[3])
        if info[4] == 9:
            if info[3] != 9:
                offth = ' {}'.format(info[3])
        line = ''
        line += '{:>0}'.format(offth + "v" + str(info[4]))
        line += '{:>13}'.format(info[2])
        line += '{:>9}'.format(info[8])
        line += '{:>9}'.format(info[7])
        line += '{:>10}'.format(info[6])
        line += '{:>10}%'.format(info[10])
        line += '{:>9}%'.format(info[9]) + '\n'
        embed1.append(line)
    def fill(number):
        for int in range(number):
            embed1.append('')
    length = len(fetch)
    dif = 15 - length
    fill(dif)
    try:
        page = 1
        pages = paginator.MsgPag(ctx, message=ctx.message, entries=embed1, per_page=20)
        await pages.paginate(start_page=page, to_del=to_delete)
    except paginator.CannotPaginate as e:
        await ctx.send(str(e))

async def playerga_send(ctx, dump, playertag, enemy_ffs):
    if enemy_ffs == 'Normal':
        enemy_ffs = 'Offence '
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT AttackerName FROM ffsbot WHERE AttackerClanMemberMemberTag = :tag", {'tag': playertag[0]})
            names2 = await c.fetchall()
            await c.close()
    if enemy_ffs == 'Enemy':
        enemy_ffs = 'Defence '
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT DefenderName FROM ffsbot WHERE DefenderClanMemberMemberTag = :tag", {'tag': playertag[0]})
            names2 = await c.fetchall()
            await c.close()
    names = list(set(names2))
    number = len(names2)
    for name1 in names:
        name = name1[0]
    header = '```Player: {} {} Last {} Hits, for (competetive) wars downloaded with the bot\n\n{:>2}{:>8}{:>12}{:>10}{:>12}{:>8}{:>16}{:>20} \n---------------------------------------------------------------------------------------------```'.format(
        name + ' (' + playertag[0] + '),', number, enemy_ffs, 'Attack', 'Triple', 'Fresh/Clean', 'Stars',
        'Percentage', 'Best', 'Opponent',
        'League + Week')
    to_delete = []
    to_delete.append(await ctx.send(header))
    embed1 = []
    for info in dump:
        if info[9] == 9:
            if info[13] == 9:
                offth = '  9'
            else:
                offth = ' {}'.format(info[9])

        else:
            offth = str(info[9])
        if info[13] == 9:
            if info[9] != 9:
                offth = ' {}'.format(info[9])
        else:
            pass
        if info[16] == 3:
            emoji = '✅'
        else:
            if info[13] == 11:
                if info[16] == 2:
                    emoji = '📏'
                else:
                    emoji = '❌'
            else:
                emoji = '❌'
            if info[13] == 12:
                if info[16] == 2:
                    emoji = '📏'
                else:
                    emoji = '❌'

        if info[14] == 1:
            fresh_clean = 'Fresh'
        else:
            fresh_clean = 'Clean'
        line = ''
        line += '{:>0}'.format(offth + "v" + str(info[13]))
        line += '{:>4}'.format(emoji)
        line += '{:>13}'.format(fresh_clean)
        line += '{:>10}'.format(info[16])
        line += '{:>11}'.format(info[15]) + '%'
        line += '{:>10}'.format(info[20])
        line += '{:>17}'.format(info[1])
        line += '{:>20}'.format(info[2] + ' (' +  info[3] + ')') + '\n'
        embed1.append(line)
    def fill(number):
        for int in range(number):
            embed1.append('')
    length = number
    dif = 15 - length
    fill(dif)

    try:
        print(embed1)
        page = 1
        pages = paginator.MsgPag(ctx, message=ctx.message, entries=embed1, per_page=20)
        await pages.paginate(start_page=page, to_del=to_delete)
    except paginator.CannotPaginate as e:
        await ctx.send(str(e))


async def war_ga(ctx, dump, playertag,enemy_ffs):
    print('ok')
    if enemy_ffs == 'Normal':
        enemy_ffs = 'Offence '
        attackercol = 'Attacker Name'
        other = 'Defence '
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT WarEnemyName FROM ffsbot WHERE warid = :tag AND AttackerType = 'Normal'", {'tag': playertag[0]})
            names2 = await c.fetchall()
            await c.close()
    if enemy_ffs == 'Enemy':
        enemy_ffs = 'Defence '
        attackercol = 'Defender Name'
        other = 'Offence '
        async with aiosqlite.connect(db_path) as db:
            c = await db.execute("SELECT WarEnemyName FROM ffsbot WHERE warid = :tag AND AttackerType = 'Enemy'", {'tag': playertag[0]})
            names2 = await c.fetchall()
            await c.close()
    embed1 = []
    names = list(set(names2))
    number = len(names2)
    for name1 in names:
        name = name1[0]
        header = '```Enemy Clan: {}, {} Hits ({}Attacks)\n\nTo see {}attacks, please press ⏹ reaction. If you do not press it within 120 seconds, it will automatically post.\n\n{:>5}{:>8}{:>14}{:>9}{:>14}{:>10}{:>18}{:>22} \n----------------------------------------------------------------------------------------------------------```'.format(
            name, number, enemy_ffs, other, 'Attack', 'Triple', 'Fresh/Clean', 'Stars',
            'Percentage', 'Best', attackercol,
            'League + Week')
        to_delete = []
        to_delete.append(await ctx.send(header))
        for info in dump:
            if enemy_ffs == 'Defence ':
                attackername = info[12]
            if enemy_ffs == 'Offence ':
                attackername = info[8]
            if info[9] == 9:
                if info[13] == 9:
                    offth = '  9'
                else:
                    offth = ' {}'.format(info[9])

            else:
                offth = str(info[9])
            if info[13] == 9:
                if info[9] != 9:
                    offth = ' {}'.format(info[9])
            else:
                pass
            if info[16] == 3:
                emoji = '✅'
            else:
                if info[13] == 11:
                    if info[16] == 2:
                        emoji = '📏'
                    else:
                        emoji = '❌'
                else:
                    emoji = '❌'
                if info[13] == 12:
                    if info[16] == 2:
                        emoji = '📏'
                    else:
                        emoji = '❌'

            if info[14] == 1:
                fresh_clean = 'Fresh'
            else:
                fresh_clean = 'Clean'
            line = ''
            line += '{:>4}'.format(offth + "v" + str(info[13]))
            line += '{:>4}'.format(emoji)
            line += '{:>13}'.format(fresh_clean)
            line += '{:>10}'.format(info[16])
            line += '{:>11}'.format(info[15]) + '%'
            line += '{:>10}'.format(info[20])
            #line += '{:>17}'.format(info[1])
            line += '{:>20}'.format(attackername)
            line += '{:>20}'.format(info[2] + ' (' + info[3] + ')') + '\n'
            line += ''
            embed1.append(line)
        entries = embed1

        try:
            page = 1
            pages = paginator.MsgPag(ctx, message=ctx.message, entries=entries, per_page=20)
            await pages.paginate(start_page=page, to_del=to_delete)
        except paginator.CannotPaginate as e:
            await ctx.send(str(e))

async def filter(ctx, oppname_wartype, wartype, week, enemy_us, fresh_clean, offth, defth, normal_post_line, oppnamefromdb:str=None, playertagfromdb:str=None, playertagga:str=None, warid:str=None, playertaggd:str=None):
    if wartype == 'all':
        async with aiosqlite.connect(db_path) as db:
            if oppname_wartype == 'oppname':
                c = await db.execute("SELECT place FROM clanhr")
            if oppname_wartype == 'wartype':
                c = await db.execute("SELECT wartype FROM leaguehr")
            if oppname_wartype == 'playerhr':
                c = await db.execute("SELECT playertag FROM playerhr")
            if oppname_wartype == 'playerga':
                c = await db.execute("SELECT hitid FROM ffsbot")
            if oppname_wartype == 'warid':
                c = await db.execute("SELECT warid FROM ffsbot")
            unique_clanname = list(set(await c.fetchall()))
            await c.close()
    else:
        if week == 'all':
            async with aiosqlite.connect(db_path) as db:
                if oppname_wartype == 'oppname':
                    c = await db.execute("SELECT wartype FROM clanhr WHERE wartype = :type", {'type':wartype})
                if oppname_wartype == 'wartype':
                    c = await db.execute("SELECT wartype FROM leaguehr WHERE wartype = :type", {'type':wartype})
                if oppname_wartype == 'playerhr':
                    c = await db.execute("SELECT playertag FROM playerhr WHERE playertag = :type", {'type':wartype})
                if oppname_wartype == 'playerga':
                    c = await db.execute("SELECT hitcode FROM ffsbot WHERE playertag = :type", {'type':wartype})
                if oppname_wartype == 'warid':
                    c = await db.execute("SELECT warid FROM ffsbot WHERE WarType = :type", {'type':wartype})
                unique_clanname = list(set(c.fetchall()))
                await db.close()
        else:
            async with aiosqlite.connect(db_path) as db:

                if oppname_wartype == 'oppname':
                    c = await db.execute("SELECT wartype FROM clanhr WHERE wartype = :wartype AND week = :week", {'wartype':wartype, 'week':week})
                if oppname_wartype == 'wartype':
                    c = await db.execute("SELECT wartype FROM leaguehr WHERE wartype = :wartype", {'wartype':wartype, 'week':week})
                if oppname_wartype == 'playerhr':
                    c = await db.execute("SELECT playertag FROM playerhr WHERE wartype = :wartype", {'wartype': wartype, 'week': week})
                if oppname_wartype == 'warid':
                    c = await db.execute("SELECT warcode FROM ffsbot WHERE WarType = :type", {'type': wartype})
                unique_clanname = list(set(c.fetchall()))
                await db.close()
    async with aiosqlite.connect(db_path) as db:

        if oppnamefromdb:
            c = await db.execute("SELECT oppname FROM clanhr WHERE oppname = :name", {'name':oppnamefromdb})
            unique_clanname = list(set(c.fetchall()))
        if playertagfromdb:
            c = await db.execute("SELECT playertag FROM playerhr WHERE playertag = :tag", {'tag':playertagfromdb})
            unique_clanname = list(set(c.fetchall()))
        if playertagga:
            c = await db.execute("SELECT AttackerClanMemberMemberTag FROM ffsbot WHERE AttackerClanMemberMemberTag = :tag", {'tag':playertagga})
            unique_clanname = list(set(c.fetchall()))
        if playertaggd:
            c = await db.execute("SELECT DefenderClanMemberMemberTag from ffsbot WHERE DefenderClanMemberMemberTag = :tag", {'tag':playertaggd})
            unique_clanname = list(set(c.fetchall()))
        if warid:
            c = await db.execute("SELECT warid FROM ffsbot WHERE warid = :warid", {'warid':warid})
            unique_clanname = list(set(await c.fetchall()))
        await db.close()
    # print(playertagga)
    # print(unique_clanname)
    for oppname in unique_clanname:
        async with aiosqlite.connect(db_path) as db:
            if oppname_wartype == 'oppname':
                c = await db.execute("SELECT atttype FROM clanhr WHERE place = :opp", {'opp': oppname[0], 'oppname':oppname_wartype})
            if oppname_wartype == 'wartype':
                c = await db.execute("SELECT atttype FROM leaguehr WHERE wartype = :opp", {'opp': oppname[0], 'oppname':oppname_wartype})
            if oppname_wartype == 'playerhr':
                c = await db.execute("SELECT atttype FROM playerhr WHERE playertag = :opp",
                          {'opp': oppname[0], 'oppname': oppname_wartype})
            if oppname_wartype == 'playerga':
                c = await db.execute("SELECT AttackerType FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp", {'opp':oppname[0]})
            if oppname_wartype == 'playergd':
                c = await db.execute("SELECT AttackerType FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp", {'opp':oppname[0]})
            if oppname_wartype == 'warid':
                c = await db.execute("SELECT AttackerType FROM ffsbot WHERE warid = :id", {'id':oppname[0]})
            atttype = await c.fetchall()
            unique_atttype = list(set(atttype))

            for att in unique_atttype:
                if enemy_us == 'all':
                    if fresh_clean == 'all':
                        if offth == 'all':
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp':oppname[0]})
                                    # if oppname_wartype == 'oppname':
                                    #     c = await db.execute(
                                    #         "SELECT * FROM clanhr WHERE oppname = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                    #         {'opp': oppname[0]})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0]})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0]})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0]})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0]})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' ORDER BY hitid;",
                                            {'opp': oppname[0]})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                        else:
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                            else:
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def':defth, 'off':offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND defth = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND defth = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND defth = :def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'def':defth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND defth=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND defth=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND defth=:def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                    else:
                        if offth == 'all':
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean = :fc AND place = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean = :fc AND wartype = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean = :fc AND playertag = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean = :fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean = :fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean = :fc AND warid = :opp AND AttackerType = 'Normal' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Enemy' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                        else:
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND offth =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND offth =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Normal' AND offth =:off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                            else:
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def':defth, 'off':offth, 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'def':defth, 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                if enemy_us == 'normal':
                    if fresh_clean == 'all':
                        if offth == 'all':
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                            else:
                                if defth == 'all':
                                    if att[0] == 'Normal':
                                        if oppname_wartype == 'oppname':
                                                c = await db.execute(
                                                "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                                {'opp': oppname[0], 'off': offth, 'oppname':oppname_wartype})
                                        if oppname_wartype == 'wartype':
                                            c = await db.execute(
                                                "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                                {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                        if oppname_wartype == 'playerhr':
                                            c = await db.execute(
                                                "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                                {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                        if oppname_wartype == 'playerga':
                                            c = await db.execute(
                                                "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                                {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                        if oppname_wartype == 'playergd':
                                            c = await db.execute(
                                                "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                                {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                        if oppname_wartype == 'warid':
                                            c = await db.execute(
                                                "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                                {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                        dump = await c.fetchall()
                                        await normal_post_line(ctx, dump, oppname, 'Normal')
                                else:
                                    if att[0] == 'Normal':
                                        if oppname_wartype == 'oppname':
                                            c = await db.execute(
                                                "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                                {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname':oppname_wartype})

                                        if oppname_wartype == 'wartype':
                                            c = await db.execute(
                                                "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                                {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                        if oppname_wartype == 'playerhr':
                                            c = await db.execute(
                                                "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                                {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                        if oppname_wartype == 'playerga':
                                            c = await db.execute(
                                                "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                                {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                        if oppname_wartype == 'playergd':
                                            c = await db.execute(
                                                "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                                {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                        if oppname_wartype == 'warid':
                                            c = await db.execute(
                                                "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                                {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                        dump = await c.fetchall()
                                        await normal_post_line(ctx, dump, oppname, 'Normal')
                        else:
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                            else:
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                    else:
                        if offth == 'all':
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean = :fc AND place = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean = :fc AND wartype = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean = :fc AND playertag = :opp AND atttype = 'Normal' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean = :fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean = :fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean = :fc AND warid = :opp AND AttackerType = 'Normal' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                            else:
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                        else:
                            if defth == 'all':
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')
                            else:
                                if att[0] == 'Normal':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Normal' AND totatt != 0 AND offth =:off AND defth = :def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Normal' AND AttackerTownHallLevel =:off AND DefenderTownHallLevel = :def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'def': defth, 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Normal')

                if enemy_us == 'enemy':
                    if fresh_clean == 'all':
                        if offth == 'all':
                            if defth == 'all':
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                            else:
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                        else:
                            if defth == 'all':
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                            else:
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'def':defth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                    else:
                        if offth == 'all':
                            if defth == 'all':
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Enemy' AND totatt != 0 ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Enemy' ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'fc': fresh_clean, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                            else:
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                        else:
                            if defth == 'all':
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')
                            else:
                                if att[0] == 'Enemy':
                                    if oppname_wartype == 'oppname':
                                        c = await db.execute(
                                            "SELECT * FROM clanhr WHERE fresh_clean=:fc AND place = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off':offth, 'def':defth, 'fc':fresh_clean, 'oppname':oppname_wartype})
                                    if oppname_wartype == 'wartype':
                                        c = await db.execute(
                                            "SELECT * FROM leaguehr WHERE fresh_clean=:fc AND wartype = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerhr':
                                        c = await db.execute(
                                            "SELECT * FROM playerhr WHERE fresh_clean=:fc AND playertag = :opp AND atttype = 'Enemy' AND totatt != 0 AND offth = :off AND defth=:def ORDER BY offth, defth;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playerga':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND AttackerClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})
                                    if oppname_wartype == 'playergd':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND DefenderClanMemberMemberTag = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY hitid DESC;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    if oppname_wartype == 'warid':
                                        c = await db.execute(
                                            "SELECT * FROM ffsbot WHERE fresh_clean=:fc AND warid = :opp AND AttackerType = 'Enemy' AND AttackerTownHallLevel = :off AND DefenderTownHallLevel=:def ORDER BY AttackerTownHallLevel, DefenderTownHallLevel;",
                                            {'opp': oppname[0], 'off': offth, 'def': defth, 'fc': fresh_clean,
                                             'oppname': oppname_wartype})

                                    dump = await c.fetchall()
                                    await normal_post_line(ctx, dump, oppname, 'Enemy')

        await db.close()