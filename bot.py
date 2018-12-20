import sqlite3
import discord
import asyncio
from coc import ClashOfClans
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import logging
import sys
import paginator
import time
from creds import coctoken, ffsbottoken
import traceback
import datetime
from paginator import EmbedPag
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logger.addHandler(logging.StreamHandler(sys.stdout))
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
bot = commands.Bot(command_prefix='.', case_insensitive=True)
bot.remove_command('help')
TOKEN = ffsbottoken

initial_extensions = ['ClanCommands', 'PlayerCommands', 'ClaimCommands', 'DatabaseCommands', 'DownloadCommands']



if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(e)


class Misc:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        cmd = error.original.__class__.__name__
        error = getattr(error, 'original', error)
        errtraceback = traceback.format_exception(type(error), error, error.__traceback__)
        #get traceback from error
        tbtosend = ''
        #make it nice to read
        for b in errtraceback:
            tbtosend += b + '\n'
        #send with formatting
        await ctx.send(f'```py\n{tbtosend}\n```')
        e = discord.Embed(colour=0x00ff00)
        e.title = f"{cmd}: {error}"
        icon = [bot.get_user(230214242618441728).avatar_url]
        e.set_footer(
            text="If this is not obvious how to fix (ie. need to include a ping/bad tag etc), please ping @mathsman to fix his hunk a junk.",
            icon_url=icon)
        timestamp = datetime.datetime.utcnow()
        e.timestamp = timestamp
        await ctx.send(embed=e)
        print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

    def find_command(self, bot, command):
        """Finds a command (be it parent or sub command) based on string given"""
        cmd = None

        for part in command.split():
            try:
                if cmd is None:
                    cmd = bot.get_command(part)
                else:
                    cmd = cmd.get_command(part)
            except AttributeError:
                cmd = None
                break

        return cmd

    @commands.command()
    @commands.has_role("FFS Bot Command")
    async def load(self, ctx, *, module):
        """Load a cog/extension. Available cogs to reload: `ClaimCommands`, `PlayerCommands`, `ClanCommands`, `DownloadCommands`, `DatabaseCommands`.
                PARAMETERS: [extension name]
                EXAMPLE: `load DownloadCommands`
                RESULT: Loads commands: dl and stopdl. These will now work. Returns result"""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')


    @commands.command()
    @commands.has_role("FFS Bot Command")
    async def unload(self, ctx, *, module):
        """Unloads a cog/extension. Available cogs to unload: `ClaimCommands`, `PlayerCommands`, `ClanCommands`, `DownloadCommands`.
                PARAMETERS: [extension name]
                EXAMPLE: `unload DownloadCommands`
                RESULT: Unloads commands: dl and stopdl. These will now not work. Returns result"""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')
    
    @commands.command(name='ping')
    async def pingcmd(self, ctx):
        """Gives bot latency, ie. how fast the bot responds (avg 300ms)
                PARAMETERS: []
                EXAMPLE: `ping`
                RESULT: Bot latency/speed/delay in ms"""

        start = time.perf_counter()
        message = await ctx.send('Ping...')
        # Rewrite: await ctx.send('Ping...')
        end = time.perf_counter()
        duration = bot.latency * 1000
        await message.edit(content='Pong! {:.2f}ms'.format(duration))
        # Rewrite: await message.edit(content='Pong! {:.2f}ms'.format(duration))

    async def on_ready(self):
        print(bot.guilds)
        print(server.name for server in bot.guilds)
        game = discord.Game("with numbers")
        await bot.change_presence(status=discord.Status.idle, activity=game)

    @commands.command()
    async def help(self, ctx, *, message=None):
        'This command is used to provide a link to the help URL.\n    This can be called on a command to provide more information about that command\n    You can also provide a page number to pull up that page instead of the first page\n\n    EXAMPLE: !help help\n    RESULT: This information'
        cmd = None
        page = 1
        if message is not None:
            try:
                page = int(message)
            except:
                cmd = self.find_command(bot, message)
        if cmd is None:
            entries = []
            e = discord.Embed(colour=0x00ff00)
            e.set_author(name="Command List.")
            e.add_field(name="claim", value="Claim an account", inline=False)
            e.add_field(name="del", value="Delete claimed account", inline=False)
            e.add_field(name="primary", value="Set primary account", inline=False)
            e.add_field(name="delprim", value="Delete primary account", inline=False)
            e.add_field(name="myc", value="See claimed accounts", inline=False)
            e.add_field(name="gc", value="Get all claimable accounts\n", inline=False)

            e.add_field(name="hr", value="Get HR of a player [tag/ign]", inline=False)
            e.add_field(name="phr", value="Ping someone to get their HR", inline=False)
            e.add_field(name="mhr", value="Get HR of your claimed accounts", inline=False)
            e.add_field(name="ga", value="Get attacks of a player [tag/ign]", inline=False)
            e.add_field(name="gpa", value="Get attacks of a player [ping]", inline=False)
            e.add_field(name="myga", value="Get attacks of claimed accounts\n", inline=False)

            e.add_field(name="waralias", value="Get all war info (opp name/tag/warid)", inline=False)
            e.add_field(name="clanhr", value="Get HR of a clan [tag/ign]", inline=False)
            e.add_field(name="lhr", value="Get HR of a league [league name]", inline=False)
            e.add_field(name="gwa", value="Get attacks of a war [opp name/tag/warid]\n", inline=False)

            e.add_field(name="dl", value="Start downloading of a war [league name AND week]", inline=False)
            e.add_field(name="stopdl", value="Stop downloading of current war", inline=False)
            e.add_field(name="updatestats", value="Updated stats manually if you spin early", inline=False)
            e.add_field(name="load", value="Load a cog", inline=False)
            e.add_field(name="unload", value="Unload a cog", inline=False)
            e.add_field(name="ping", value="Get response time of bot", inline=False)
            timestamp = datetime.datetime.utcnow()
            e.timestamp = timestamp
            icon = bot.get_user(230214242618441728).avatar_url
            e.set_footer(text="Words in [ ] at end of description are mandatory parameters. \n\nType help [command] for more info on a command, examples, and how to use it. ", icon_url=icon)
            await ctx.send(embed=e)
        if cmd is None:
            e = []
            e.append("**claim**")
            e.append("Claim an account")
            e.append("**del**")
            e.append("Delete claimed account")
            e.append("**primary**")
            e.append("Set primary account")
            e.append("**delprim**")
            e.append("Delete primary account")
            e.append("myc")
            e.append("See claimed accounts")
            e.append("**gc**")
            e.append("Get all claimable accounts")
            #
            # e.add_field(name="hr", value="Get HR of a player [tag/ign]", inline=False)
            # e.add_field(name="phr", value="Ping someone to get their HR", inline=False)
            # e.add_field(name="mhr", value="Get HR of your claimed accounts", inline=False)
            # e.add_field(name="ga", value="Get attacks of a player [tag/ign]", inline=False)
            # e.add_field(name="gpa", value="Get attacks of a player [ping]", inline=False)
            # e.add_field(name="myga", value="Get attacks of claimed accounts\n", inline=False)
            #
            # e.add_field(name="waralias", value="Get all war info (opp name/tag/warid)", inline=False)
            # e.add_field(name="clanhr", value="Get HR of a clan [tag/ign]", inline=False)
            # e.add_field(name="lhr", value="Get HR of a league [league name]", inline=False)
            # e.add_field(name="gwa", value="Get attacks of a war [opp name/tag/warid]\n", inline=False)
            #
            # e.add_field(name="dl", value="Start downloading of a war [league name AND week]", inline=False)
            # e.add_field(name="stopdl", value="Stop downloading of current war", inline=False)
            # e.add_field(name="updatestats", value="Updated stats manually if you spin early", inline=False)
            # e.add_field(name="load", value="Load a cog", inline=False)
            # e.add_field(name="unload", value="Unload a cog", inline=False)
            # e.add_field(name="ping", value="Get response time of bot", inline=False)
            # timestamp = datetime.datetime.utcnow()
            # e.timestamp = timestamp
            # icon = bot.get_user(230214242618441728).avatar_url
            # e.set_footer(text="Words in [ ] at end of description are mandatory parameters. \n\nType help [command] for more info on a command, examples, and how to use it. ", icon_url=icon)
            # await ctx.send(embed=e)
            try:
                page = 1
                pages = paginator.EmbedPag(ctx, message=ctx.message, entries=e, per_page=5)
                await pages.paginate(start_page=1)
            except paginator.CannotPaginate as err:
                await ctx.send(str(err))

        else:
            description = cmd.help
            if description is not None:
                parameter = [x.replace('PARAMETERS: ', '') for x in description.split('\n') if 'PARAMETERS:' in x]
                example = [x.replace('EXAMPLE: ', '') for x in description.split('\n') if 'EXAMPLE:' in x]
                result = [x.replace('RESULT: ', '') for x in description.split('\n') if 'RESULT:' in x]
                description = [x for x in description.split('\n') if x and ('EXAMPLE:' not in x) and ('RESULT:' not in x) and ('PARAMETERS:' not in x)]
            else:
                parameter = None
                example = None
                result = None
            embed = discord.Embed(title=cmd.qualified_name, colour=0x00ff00)
            embed.set_footer(icon_url=self.bot.user.avatar_url)
            if description:  # Get the description for a command
                embed.add_field(name='Description', value='\n'.join(description), inline=False)
            if parameter:
                embed.add_field(name="Parameters", value='\n'.join(parameter), inline=False)
            if example:
                embed.add_field(
                    name='Example', value='\n'.join(example),
                    inline=False)  # Split into examples, results, and the description itself based on the string
            if result:
                embed.add_field(name='Result', value='\n'.join(result), inline=False)
            timestamp = datetime.datetime.utcnow()
            embed.timestamp = timestamp
            await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, *, msg):
        print(ctx.message.guild.channels)
        error_channels = ''
        successful = 1
        for channel in ctx.message.guild.text_channels:
            try:
                await self.bot.get_channel(channel.id).send(msg)
                successful += 1
            except discord.errors.Forbidden:
                error_channels += f'<#{channel.id}>\n'
        embed = discord.Embed()
        if error_channels == '':
            embed.color = (0x00ff00)
        else:
            embed.colour = (0xff0000)
        embed.set_author(name=f"Successful number of channels sent in: {successful}\n"
                              f"I'm missing permissions in the following channels:\n",
                              icon_url=self.bot.user.avatar_url)
        embed.description = error_channels
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))
setup(bot)


print('ready')
bot.run(TOKEN)
