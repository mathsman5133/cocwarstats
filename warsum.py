import sqlite3
from discord import Webhook, RequestsWebhookAdapter
import discord
from creds import coctoken, ffswebid, ffstoken, ffsbottoken
import os
coctoken = coctoken()
ffswebid = ffswebid()
ffsbottoken = ffsbottoken()
ffstoken = ffstoken()
conn = sqlite3.connect(os.path.join(os.getcwd(),'ffsbot.db'))
c = conn.cursor()
ffswebhook = Webhook.partial(ffswebid, ffstoken, adapter=RequestsWebhookAdapter())


def send_upddb(warid):
    warwins = claninfo['warWins']
    warties = claninfo['warTies']
    warlosses = claninfo['warLosses']
    c.execute("SELECT * FROM warsum WHERE warid = :warid", {'warid':warid})
    everything = c.fetchall()
    for first in everything:
        db = first


    ourattk = f'{info}/{str(warsize*2)}'
    ourbd = f'{th9}/{th10}/{th11}/{th12}'
    ourattkleft = f'{oal9}/{oal10}/{oal11}/{oal12}/'
    ourleft = f'{l9}/{l10}/{l11}/{l12}'
    formatus = f'{db[13]}%\n{db[6]:>10}\n{db[7]:>10}\n{ourattkleft:>10}\n{ourleft:>10}'
    oppattk = f'{ouratx}/{str(warsize*2)}'
    oppbd = f'{th9}/{th10}/{th11}/{th12}'
    oppattkleft = f'{oal9}/{oal10}/{oal11}/{oal12}/'
    oppleft = f'{l9}/{l10}/{l11}/{l12}'
    formatopp = f'{ourdest}%\n{ourattk:>10}\n{ourbd:>10}\n{ourattkleft:>10}\n{ourleft:>10}'
    size = f"Size:{warsize}vs{warsize}"
    formatsize = f"{size:^10}"
    formatstars = f"`{ourstars}⭐ vs ⭐{oppstars}`\nTotal Attks\nBreakdown\nRemaining Atks\nBases Left"
    tcwl = discord.Embed(color=0x32cd32)
    tcwl.set_author(name=repname,
                    icon_url=repicon)
    tcwl.add_field(name="ForgedFromSteel", value=formatus)
    tcwl.add_field(name=formatsize, value=formatstars)
    tcwl.add_field(name=oppname, value=formatopp)
    # tcwl.set_footer(text="Victory War Record: " + str(warwins) + "-" + str(warlosses) + "-" + str(warties),
    #                 icon_url="https://vignette.wikia.nocookie.net/clashofclans/images/2/2f/Balloon_info.png/revision/latest/scale-to-width-down/120?cb=20170927230730")
    ffswebhook.send(embed=tcwl)