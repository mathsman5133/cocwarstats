from __future__ import print_function
from coc import ClashOfClans
import sqlite3
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time
import os
from googleapiclient.http import MediaFileUpload
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import csv
from discord import Webhook, RequestsWebhookAdapter
import discord
import aiosqlite
from creds import coctoken, ffswebid, ffstoken, ffsbottoken
coctoken = coctoken()
ffswebid = ffswebid()
ffsbottoken = ffsbottoken()
ffstoken = ffstoken()
conn = sqlite3.connect(os.path.join(os.getcwd(),'ffsbot.db'))
db_path = os.path.join(os.getcwd(),'ffsbot.db')
c = conn.cursor()
ffswebhook = Webhook.partial(ffswebid, ffstoken, adapter=RequestsWebhookAdapter())
# SCOPES = ['https://www.googleapis.com/auth/drive.file',
#         'https://www.googleapis.com/auth/drive.apps.readonly']
# # store = file.Storage('/home/pi/Desktop/storage.json')
# store = file.Storage('C:/py/storage.json')
# creds = store.get()
# if not creds or creds.invalid:
#    flow = client.flow_from_clientsecrets('C:/py/drivecreds2.json', SCOPES)
#    # flow = client.flow_from_clientsecrets('/home/pi/Desktop/drivecreds2.json', SCOPES)
#
#    creds = tools.run_flow(flow, store)
# DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))
# coc = ClashOfClans(coctoken)
# scope = ['https://spreadsheets.google.com/feeds',
#         'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('C:/py/creds.json', scope)
# # creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/Desktop/credssheets.json', scope)
#
# clientgoogle = gspread.authorize(creds)
def dump_hits(wartype, week, ffs, warid):
    opptag = ffs['opponent']['tag']
    oppname = ffs['opponent']['name']
    usdump = ffs['clan']['members']

    for member in usdump:
        try:
            for attack in member['attacks']:
                order = attack['order']
                #async with aiosqlite.connect(db_path) as db:
                with conn:
                    c.execute("SELECT attorder FROM ffsbot WHERE attorder = :order AND warid = :warid", {'warid':warid, 'order':order})
                    findatx = c.fetchall()
                    print(findatx)
                    if len(findatx) == 0:
                        oppclanname = ffs['opponent']['name']
                        oppclantag = ffs['opponent']['tag']
                        attackertag = attack['attackerTag']
                        stars = attack['stars']
                        destruction = attack['destructionPercentage']
                        order = attack['order']
                        tag = member['tag']
                        ign = member['name']
                        th = member['townhallLevel']
                        mapos = member['mapPosition']
                        defendertag = attack['defenderTag']
                        for opp in ffs['opponent']['members']:
                            if opp['tag'] == defendertag:
                                oppth = opp['townhallLevel']
                                opppos = opp['mapPosition']
                                oppname = opp['name']
                                if opp['bestOpponentAttack']['attackerTag'] == tag:
                                    best = 'TRUE'
                                else:
                                    best = 'FALSE'

                        defendertag = attack['defenderTag']
                        c.execute("SELECT attorder FROM ffsbot WHERE DefenderClanMemberMemberTag = :tag AND WarEnemyTag = :clantag AND WarType = :type AND WarEnd = :week", {'order':order, 'tag':defendertag, 'clantag':oppclantag, 'type':wartype, 'week':week})
                        findhits = c.fetchall()
                        try:
                            mini = min(findhits)
                            attempt = 2
                        except ValueError:
                            attempt = 1
                        c.execute("SELECT MAX(hitid) FROM ffsbot")
                        a = c.fetchall()
                        for b in a:
                            hitid = b[0] + 1
                        print('ok')
                        c.execute("""INSERT INTO ffsbot VALUES
                                    (:enemytag, :enemyname, :type,
                                    :end, :order, :attacktype, :atttag,
                                    :attrank, :attname, :attth, :deftag,
                                    :defrank, :defname, :defth, :attempt, 
                                    :dest, :stars, :newstars, :netstars, 
                                    :netdest, :best, :hitid)""",
                                  {'enemytag':oppclantag,
                                   'enemyname':oppclanname,
                                   'type':wartype,
                                   'end':week,
                                   'order':order,
                                   'attacktype':'Normal',
                                   'atttag':tag,
                                   'attrank':mapos,
                                   'attname':ign,
                                   'attth':th,
                                   'deftag':defendertag,
                                   'defrank':opppos,
                                   'defname':oppname,
                                   'defth':oppth,
                                   'attempt':attempt,
                                   'dest':destruction,
                                   'stars':stars,
                                   'newstars':'',
                                   'netstars':'',
                                   'netdest':warid,
                                   'best':best,
                                   'hitid':hitid
                                   })
                        #db.close()
                        print('updated')
                        print('{}'.format(ign) + "brings to you a " + str(th) + "v" + str(oppth) + " attack for : " + str(stars) + ":star: and " + str(destruction) + " (Attack No." + str(order) + ").")
                        try:
                            ffswebhook.send(ign + "brings to you a " + str(th) + "v" + str(oppth) + " attack for : " + str(stars) + ":star: and " + str(destruction) + " (Attack No." + str(order) + ").")
                        except discord.errors.HTTPException:
                            print('no')
        except Exception as e:
            print(e)
            continue

    print('ok')
    themdump = ffs['opponent']['members']
    for member in themdump:
        try:
            #async with aiosqlite.connect(db_path) as db:
            with conn:
                for attack in member['attacks']:
                    print('them')
                    order = attack['order']
                    c.execute("SELECT attorder FROM ffsbot WHERE attorder = :order AND WarEnemyTag = :clantag AND WarType = :type AND WarEnd = :week", {'clantag':opptag,'type':wartype, 'week':week, 'order':order} )
                    findatx = c.fetchall()
                    if len(findatx) == 0:
                        oppclanname = ffs['opponent']['name']
                        oppclantag = ffs['opponent']['tag']
                        attacks = member['attacks']
                        attackertag = attack['attackerTag']
                        stars = attack['stars']
                        destruction = attack['destructionPercentage']
                        order = attack['order']
                        tag = member['tag']
                        ign = member['name']
                        th = member['townhallLevel']
                        mapos = member['mapPosition']
                        defendertag = attack['defenderTag']
                        for us in ffs['clan']['members']:
                            if us['tag'] == defendertag:
                                usth = us['townhallLevel']
                                uspos = us['mapPosition']
                                usname = us['name']
                                if us['bestOpponentAttack']['attackerTag'] == tag:
                                    best = 'TRUE'
                                else:
                                    best = 'FALSE'
                        defendertag = attack['defenderTag']
                        c.execute(
                            "SELECT attorder FROM ffsbot WHERE DefenderClanMemberMemberTag = :tag AND WarEnemyTag = :clantag AND WarType = :type AND WarEnd = :week",
                            {'tag': defendertag, 'clantag': oppclantag, 'type': wartype, 'week': week})
                        findhits = c.fetchall()
                        try:
                            mini = min(findhits)
                            attempt = 2
                        except ValueError:
                            attempt = 1
                        c.execute("SELECT MAX(hitid) FROM ffsbot")
                        a = c.fetchall()
                        for b in a:
                            hitid = b[0] + 1
                        c.execute("""INSERT INTO ffsbot VALUES
                                    (:enemytag, :enemyname, :type,
                                    :end, :order, :attacktype, :atttag,
                                    :attrank, :attname, :attth, :deftag,
                                    :defrank, :defname, :defth, :attempt, 
                                    :dest, :stars, :newstars, :netstars, 
                                    :netdest, :best, :hitid)""",
                                  {'enemytag':oppclantag,
                                   'enemyname':oppclanname,
                                   'type':wartype,
                                   'end':week,
                                   'order':order,
                                   'attacktype':'Enemy',
                                   'atttag':tag,
                                   'attrank':mapos,
                                   'attname':ign,
                                   'attth':th,
                                   'deftag':defendertag,
                                   'defrank':uspos,
                                   'defname':usname,
                                   'defth':usth,
                                   'attempt':attempt,
                                   'dest':destruction,
                                   'stars':stars,
                                   'newstars':'',
                                   'netstars':'',
                                   'netdest':warid,
                                   'best':best,
                                   'hitid':hitid
                                   })
                        #await db.close()
                        print(ign + "brings to you a " + str(th) + "v" + str(usth) + " attack for : " + str(stars) + ":star: and " + str(destruction) + " (Attack No." + str(order) + ").")
                        print('updated')
                        try:
                            ffswebhook.send('{}'.format(ign) + "brings to you a " + str(th)+ "v" + str(usth) + " attack for : " + str(stars) + ":star: and " +str(destruction) + " (Attack No." + str(order) + ")")
                        except discord.errors.HTTPException:
                            pass

        except:
            continue
    print('none')

def db_drop():
    FILENAME = 'ffsbot'
    SRC_MIMETYPE = 'application/vnd.google-apps.spreadsheet'
    DST_MIMETYPE = 'text/csv'
    files = DRIVE.files().list(
        q='name="%s" and mimeType="%s"' % (FILENAME, SRC_MIMETYPE),
        orderBy='modifiedTime desc,name').execute().get('files', [])
    print(files[0])
    if files:
        fn = 'C:/py/ffsstats.csv'
        print('Exporting "%s" as "%s"... ' % (files[0]['name'], fn), end='')
        data = DRIVE.files().export(fileId=files[0]['id'], mimeType=DST_MIMETYPE).execute()
        if data:
            with open(fn, 'wb') as f:
                f.write(data)
            print('DONE')
            ffswebhook.send("Stats for all wars including most recent war have been downloaded. This will shortly be added into the database.")
        else:
            print('ERROR (could not download file)')
    else:
        print('!!! ERROR: File not found')

def db_up():
    with open('ffswardump.csv', 'r', encoding="utf-8", newline='') as csvfile:
        read = csvfile.read()
        clientgoogle.import_csv('1wmbvoov45SGI7tCxweQ-7Wu815FFzqhATqDFh2z6U88', read.encode('utf-8'))
        #ffswebhook.send("All war data including most recent war has been uploaded to google drive. Stats will shortly download.")

async def to_csv():
    with open('ffswardump.csv', 'w', encoding="utf-8", newline='') as csvfile:
        #async with aiosqlite.connect(db_path) as db:
        with conn:
            c.execute("SELECT * FROM ffsbot")
        writer = csv.writer(csvfile)
        writer.writerow([ i[0] for i in c.description ])
        writer.writerows(c.fetchall())
        #ffswebhook.send("All war data including most recent war has been converted to a csv. This will shortly be uploaded to google drive.")

async def cmd_loadhits():
    try:
        ffs = coc.clans('#RGRCYRGR').currentwar.get()
        state = ffs['state']
        opponent = ffs['opponent']['tag']
        print(opponent)
        oppname = ffs['opponent']['name']
        #async with aiosqlite.connect(db_path) as db:
        with conn:
            c.execute("SELECT toggle FROM toggle WHERE opponent = :opp AND toggle=1", {'opp':opponent})
            toggle = c.fetchall()
            c.execute("SELECT wartype FROM toggle WHERE opponent = :opp AND toggle = 1", {'opp':opponent})
            wartype = c.fetchall()
            c.execute("SELECT week FROM toggle WHERE opponent = :opp AND toggle = 1", {'opp':opponent})
            week = c.fetchall()
            c.execute("SELECT warid FROM toggle WHERE opponent = :opp AND toggle = 1", {'opp':opponent})
            warid = c.fetchall()
            #await db.close()
        for res in toggle:
            if int(res[0]) == 1:
                if state == 'inWar':
                    for war in wartype:
                        for weekno in week:
                            for id in warid:
                                dump_hits(war[0], weekno[0], ffs, id[0])
                if state == 'warEnded':
                    for war in wartype:
                        for weekno in week:
                            for id in warid:
                                dump_hits(war[0], weekno[0], ffs, id[0])
                                await set_fresh_clean(id[0])
                                await add_clanhrs(opponent, oppname, war[0], weekno[0])
                                await add_playerhrs()
                                await add_leagues()
                                ffswebhook.send(f"All hits have been downloaded, fresh and clean attacks confirmed, {oppname} has been added to `clanhr` command. All players and league stats and respective commands have been updated. \n\nYou are free to spin another war. Thanks!")
                    to_csv()
                    db_up()
                    #async with aiosqlite.connect(db_path) as db:
                    with conn:
                        c.execute("UPDATE toggle SET toggle=0 WHERE opponent=:opp AND toggle = 1", {'opp':opponent})
                        #await db.close()
            else:
                pass
        print(toggle)
    except sqlite3.OperationalError:
        pass

async def add_clanhr_db(opptag, oppname,wartype, week, fresh_clean, offth, defth, atttype, totatt, three, two, triphr, doubhr):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""INSERT into clanhr VALUES (:opptag, :oppname, :week, :wartype, :fresh_clean, :offth, :defth, :atttype, :totatt, :three, :two, :triphr, :doubhr, 1)""",
                  {'opptag':opptag,
                   'oppname':oppname,
                   'week':week,
                   'wartype':wartype,
                   'fresh_clean':fresh_clean,
                   'offth':offth,
                   'defth':defth,
                   'totatt':totatt,
                   'three':three,
                   'two':two,
                   'triphr':triphr,
                   'doubhr':doubhr,
                   'atttype':atttype
                   })
        await db.close()

async def add_leaguehr_db(wartype, fresh_clean, offth, defth, atttype, totatt, three, two, triphr, doubhr):
    async with aiosqlite.connect(db_path) as db:
        c = await db.execute("SELECT MAX(dif) FROM leaguehr")
        a = await c.fetchall()
        for b in a:
            max = b[0]
        await db.execute("""INSERT into leaguehr VALUES (:wartype, :fresh_clean, :offth, :defth, :atttype, :totatt, :three, :two, :triphr, :doubhr, :place, :dif)""",
                  {'wartype':wartype,
                   'fresh_clean':fresh_clean,
                   'offth':offth,
                   'defth':defth,
                   'totatt':totatt,
                   'three':three,
                   'two':two,
                   'triphr':triphr,
                   'doubhr':doubhr,
                   'atttype':atttype,
                   'place':1,
                   'dif':max + 1
                   })
        await db.close()

async def add_player_db(tag, name, fresh_clean, offth, defth, atttype, totatt, three, two, triphr, doubhr):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""INSERT into playerhr VALUES (:opptag, :oppname, :fresh_clean, :offth, :defth, :atttype, :totatt, :three, :two, :triphr, :doubhr)""",
                  {'opptag':tag,
                   'oppname':name,
                   'fresh_clean':fresh_clean,
                   'offth':offth,
                   'defth':defth,
                   'totatt':totatt,
                   'three':three,
                   'two':two,
                   'triphr':triphr,
                   'doubhr':doubhr,
                   'atttype':atttype
                   })
        await db.close()

async def add_clanhrs(enemytag, enemyname, wartype, week):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM clanhr WHERE opptag = :opptag AND wartype = :type AND week = :week", {'opptag':enemytag, 'type':wartype, 'week':week})
        await db.commit()
        c = await db.execute("SELECT AttackerTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week",
                  {'opptag':enemytag, 'type':wartype, 'week':week})
        off_th = await c.fetchall()
        unique_offth = list(set(off_th))
        for offth in unique_offth:
            c = await db.execute(
                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week",
                {'opptag': enemytag, 'type': wartype, 'week': week})
            def_th = await c.fetchall()
            unique_defth = list(set(def_th))
            for defth in unique_defth:
                c = await db.execute(
                    "SELECT AttackerType FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week",
                    {'opptag': enemytag, 'type': wartype, 'week': week})
                atttypeall = await c.fetchall()
                unique_atttype = list(set(atttypeall))
                for atttype in unique_atttype:
                    c = await db.execute(
                        "SELECT Attempt FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week",
                        {'opptag': enemytag, 'type': wartype, 'week': week})
                    attall = await c.fetchall()
                    unique_attall = list(set(attall))
                    for att in unique_attall:
                        if att[0] == 1:
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype",
                                {'opptag': enemytag, 'type': wartype, 'week': week, 'offth':offth[0], 'defth':defth[0], 'atttype':atttype[0]})
                            dump = await c.fetchall()
                            totalhits = len(dump)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 3",
                                {'opptag': enemytag, 'type': wartype, 'week': week, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            tottriples = await c.fetchall()
                            triples = len(tottriples)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 2",
                                {'opptag': enemytag, 'type': wartype, 'week': week, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            totdoub = await c.fetchall()
                            doub = len(totdoub)
                            try:
                                triphr = round((triples / totalhits * 100), 0)
                            except ZeroDivisionError:
                                triphr = 0
                            try:
                                doubhr = round((doub / totalhits * 100)+ triphr, 0)
                            except ZeroDivisionError:
                                doubhr = 0
                            await add_clanhr_db(enemytag, enemyname, wartype,week, 'fresh', offth[0], defth[0], atttype[0], totalhits, triples, doub,  triphr, doubhr)
                        else:
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype",
                                {'opptag': enemytag, 'type': wartype, 'week':week, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            dump = await c.fetchall()
                            totalhits = len(dump)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 3",
                                {'opptag': enemytag, 'type': wartype, 'week': week, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            tottriples = await c.fetchall()
                            triples = len(tottriples)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarEnemyTag = :opptag AND WarType = :type AND WarEnd = :week AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 2",
                                {'opptag': enemytag, 'type': wartype, 'week': week, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            totdoub = await c.fetchall()
                            doub = len(totdoub)
                            try:
                                triphr = round((triples / totalhits * 100), 0)
                            except ZeroDivisionError:
                                triphr = 0
                            try:
                                doubhr = round((doub / totalhits * 100)+ triphr, 0)
                            except ZeroDivisionError:
                                doubhr = 0
                            await add_clanhr_db(enemytag, enemyname, wartype, week, 'clean', offth[0], defth[0], atttype[0],
                                          totalhits, triples, doub, triphr, doubhr)
        await db.close()
async def add_leaguehr(wartype):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""INSERT into leaguehr VALUES (:wartype, :fresh_clean, :offth, :defth, :atttype, :totatt, :three, :two, :triphr, :doubhr, :place, :dif)""",
                  {'wartype':None,
                   'fresh_clean':None,
                   'offth':None,
                   'defth':None,
                   'totatt':None,
                   'three':None,
                   'two':None,
                   'triphr':None,
                   'doubhr':None,
                   'atttype':None,
                   'place':1,
                   'dif':1
                   })
        await db.commit()
        c = await db.execute("SELECT AttackerTownHallLevel FROM ffsbot WHERE WarType = :type",
                  {'type':wartype})
        off_th = await c.fetchall()
        unique_offth = list(set(off_th))
        for offth in unique_offth:
            c = await db.execute(
                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type",
                {'type': wartype})
            def_th = await c.fetchall()
            unique_defth = list(set(def_th))
            for defth in unique_defth:
                c = await db.execute(
                    "SELECT AttackerType FROM ffsbot WHERE WarType = :type",
                    {'type': wartype})
                atttypeall = await c.fetchall()
                unique_atttype = list(set(atttypeall))
                for atttype in unique_atttype:
                    c = await db.execute(
                        "SELECT Attempt FROM ffsbot WHERE WarType = :type",
                        {'type': wartype})
                    attall = await c.fetchall()
                    unique_attall = list(set(attall))
                    for att in unique_attall:
                        print(att)
                        if att[0] == 1:
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype",
                                {'type': wartype, 'offth':offth[0], 'defth':defth[0], 'atttype':atttype[0]})
                            dump = await c.fetchall()
                            totalhits = len(dump)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 3",
                                {'type': wartype, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            tottriples = await c.fetchall()
                            triples = len(tottriples)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 2",
                                {'type': wartype, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            totdoub = await c.fetchall()
                            doub = len(totdoub)
                            try:
                                triphr = round((triples / totalhits * 100), 0)
                            except ZeroDivisionError:
                                triphr = 0
                            try:
                                doubhr = round((doub / totalhits * 100)+ triphr, 0)
                            except ZeroDivisionError:
                                doubhr = 0
                            await add_leaguehr_db(wartype, 'fresh', offth[0], defth[0], atttype[0], totalhits, triples, doub,  triphr, doubhr)
                        else:
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype",
                                {'type': wartype, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            dump = await c.fetchall()
                            totalhits = len(dump)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 3",
                                {'type': wartype, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            tottriples = await c.fetchall()
                            triples = len(tottriples)
                            c = await db.execute(
                                "SELECT DefenderTownHallLevel FROM ffsbot WHERE WarType = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 2",
                                {'type': wartype, 'offth': offth[0], 'defth': defth[0],
                                 'atttype': atttype[0]})
                            totdoub = await c.fetchall()
                            doub = len(totdoub)
                            try:
                                triphr = round((triples / totalhits * 100), 0)
                            except ZeroDivisionError:
                                triphr = 0
                            try:
                                doubhr = round((doub / totalhits * 100)+ triphr, 0)
                            except ZeroDivisionError:
                                doubhr = 0
                            await add_leaguehr_db(wartype, 'clean', offth[0], defth[0], atttype[0], totalhits, triples,
                                          doub, triphr, doubhr)
        await db.close()


async def add_playerhr(tag, off_def):
    async with aiosqlite.connect(db_path) as db:
        if off_def == 'off':
            c = await db.execute("SELECT AttackerTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type",
                      {'type':tag})
            off_th = await c.fetchall()
            unique_offth = list(set(off_th))
        if off_def == 'def':
            c = await db.execute("SELECT AttackerTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type",
                      {'type': tag})
            off_th = await c.fetchall()
            unique_offth = list(set(off_th))

        for offth in unique_offth:
            if off_def == 'off':
                c = await db.execute(
                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type",
                    {'type': tag})
                def_th = await c.fetchall()
                unique_defth = list(set(def_th))
            if off_def == 'def':
                c = await db.execute(
                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type",
                    {'type': tag})
                def_th = await c.fetchall()
                unique_defth = list(set(def_th))

            for defth in unique_defth:
                if off_def == 'off':
                    c = await db.execute(
                        "SELECT AttackerType FROM ffsbot WHERE AttackerClanMemberMemberTag = :type",
                        {'type': tag})
                    atttypeall = await c.fetchall()
                    unique_atttype = list(set(atttypeall))
                if off_def == 'def':
                    c = await db.execute(
                        "SELECT AttackerType FROM ffsbot WHERE DefenderClanMemberMemberTag = :type",
                        {'type': tag})
                    atttypeall = await c.fetchall()
                    unique_atttype = list(set(atttypeall))
                for atttype in unique_atttype:
                    if off_def == 'off':

                        c = await db.execute(
                            "SELECT Attempt FROM ffsbot WHERE AttackerClanMemberMemberTag = :type",
                            {'type': tag})
                        attall = await c.fetchall()
                        unique_attall = list(set(attall))
                    if off_def == 'def':
                        c = await db.execute(
                            "SELECT Attempt FROM ffsbot WHERE DefenderClanMemberMemberTag = :type",
                            {'type': tag})
                        attall = await c.fetchall()
                        unique_attall = list(set(attall))
                    for att in unique_attall:
                        if att[0] == 1:
                            if off_def == 'off':
                                c = await db.execute("SELECT AttackerName from ffsbot where AttackerClanMemberMemberTag = :tag", {'tag':tag})
                                names = (set(await c.fetchall()))
                                for name in names:
                                    name = name[0]
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype",
                                    {'type': tag, 'offth':offth[0], 'defth':defth[0], 'atttype':atttype[0]})
                                dump = await c.fetchall()
                                totalhits = len(dump)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 3",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                tottriples = await c.fetchall()
                                triples = len(tottriples)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 2",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                totdoub = await c.fetchall()
                                doub = len(totdoub)
                            if off_def == 'def':
                                c = await db.execute("SELECT DefenderName from ffsbot where DefenderClanMemberMemberTag = :tag",
                                          {'tag': tag})
                                names = (set(await c.fetchall()))
                                for name in names:
                                    name = name[0]
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0], 'atttype': atttype[0]})
                                dump = await c.fetchall()
                                totalhits = len(dump)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 3",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                tottriples = await c.fetchall()
                                triples = len(tottriples)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt = 1 AND AttackerType = :atttype AND Stars = 2",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                totdoub = await c.fetchall()
                                doub = len(totdoub)

                            try:
                                triphr = round((triples / totalhits * 100), 0)
                            except ZeroDivisionError:
                                triphr = 0
                            try:
                                doubhr = round((doub / totalhits * 100)+ triphr, 0)
                            except ZeroDivisionError:
                                doubhr = 0
                            print(atttype[0])
                            await add_player_db(tag, name, 'fresh', offth[0], defth[0], atttype[0], totalhits, triples, doub,  triphr, doubhr)
                        else:
                            if off_def == 'off':
                                c = await db.execute(
                                    "SELECT AttackerName from ffsbot where AttackerClanMemberMemberTag = :tag",
                                    {'tag': tag})
                                names = list(set(await c.fetchall()))
                                for name in names:
                                    name = name[0]
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                dump = await c.fetchall()
                                totalhits = len(dump)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 3",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                tottriples = await c.fetchall()
                                triples = len(tottriples)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE AttackerClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 2",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                totdoub = await c.fetchall()
                                doub = len(totdoub)

                            if off_def == 'def':
                                c = await db.execute(
                                    "SELECT AttackerName from ffsbot where DefenderClanMemberMemberTag = :tag",
                                    {'tag': tag})
                                names = list(set(await c.fetchall()))
                                for name in names:
                                    name = name[0]
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                dump = await c.fetchall()
                                totalhits = len(dump)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 3",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                tottriples = await c.fetchall()
                                triples = len(tottriples)
                                c = await db.execute(
                                    "SELECT DefenderTownHallLevel FROM ffsbot WHERE DefenderClanMemberMemberTag = :type AND AttackerTownHallLevel = :offth AND DefenderTownHallLevel = :defth AND Attempt != 1 AND AttackerType = :atttype AND Stars = 2",
                                    {'type': tag, 'offth': offth[0], 'defth': defth[0],
                                     'atttype': atttype[0]})
                                totdoub = await c.fetchall()
                                doub = len(totdoub)
                            try:
                                triphr = round((triples / totalhits * 100), 0)
                            except ZeroDivisionError:
                                triphr = 0
                            try:
                                doubhr = round((doub / totalhits * 100)+ triphr, 0)
                            except ZeroDivisionError:
                                doubhr = 0
                            print(atttype[0])
                            await add_player_db(tag, name,'clean', offth[0], defth[0], atttype[0], totalhits, triples,
                                          doub, triphr, doubhr)
        await db.close()


async def add_playerhrs():
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DROP TABLE playerhr")
        await db.execute("CREATE TABLE playerhr (playertag text, playername text, fresh_clean text, offth integer, defth integer, atttype text, totatt integer, three integer, two integer, triphr integer, doubhr integer)")
        await db.commit()
        c = await db.execute("SELECT AttackerClanMemberMemberTag from ffsbot")
        unique_tag = list(set(await c.fetchall()))
        for tag in unique_tag:
            await dd_playerhr(tag[0], 'off')
            await add_playerhr(tag[0], 'def')
        await db.close()


async def add_leagues():
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DROP TABLE leaguehr")
        await db.execute(
            "CREATE TABLE leaguehr (wartype text, fresh_clean integer, offth integer, defth integer, atttype text, totatt integer, three integer, two integer, triphr integer, doubhr integer, place integer, dif integer)")
        await db.commit()
        c = await db.execute("SELECT WarType from ffsbot")
        unique_tag = list(set(await c.fetchall()))
        print(unique_tag)
        for tag in unique_tag:
            await add_leaguehr(tag[0])
            await add_leaguehr(tag[0])
        await db.close()


async def set_fresh_clean(warid):
    async with aiosqlite.connect(db_path) as db:
        c = await db.execute("SELECT DefenderClanMemberMemberTag from ffsbot WHERE warid = :warid", {'warid':warid})
        all_defenders = list(set(await c.fetchall()))
        for defender in all_defenders:
            c = await db.execute("SELECT attorder FROM ffsbot WHERE warid = :warid AND DefenderClanMemberMemberTag = :deftag", {'warid': warid, 'deftag':defender[0]})
            all_hits = await c.fetchall()
            fresh = min(all_hits)
            for a in all_hits:
                await db.execute("UPDATE ffsbot SET Attempt = 2 WHERE attorder = :attorder AND warid = :warid", {'attorder':a[0], 'warid':warid})
            await db.commit()
            for b in fresh:
                await db.execute("UPDATE ffsbot SET Attempt = 1 WHERE attorder = :attorder AND warid = :warid", {'attorder':b, 'warid':warid})
        await db.close()


async def find_warid(warid):
    async with aiosqlite.connect(db_path) as db:
        c = await db.execute("SELECT WarType, WarEnd, WarEnemyTag, WarEnemyName FROM ffsbot WHERE warid = :warid", {'warid': warid})
        a = await c.fetchall()
        for b in a:
            return b

async def clan_hr(warid):
    info = await find_warid(warid)
    await add_clanhrs(info[2], info[3], info[0], info[1])

