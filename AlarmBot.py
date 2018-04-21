# These are the dependecies. The bot depends on these to function, hence the name. Please do not change these unless your adding to them, because they can break the bot.
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import os
from pathlib import Path
path = Path(__file__).parent
from discord import opus
import youtube_dl
import asyncio
import json
import io
import re
from time import strptime
from datetime import timedelta, datetime
from pytz import timezone

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']
with open("config.json") as f:
    config = json.loads(f.read())

try:
    to_unicode = unicode
except NameError:
    to_unicode = str


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass
        raise RuntimeError('Could not load an opus lib. Tried %s' %
                           (', '.join(OPUS_LIBS)))


load_opus_lib()


# Here you can modify the bot's prefix and description and wether it sends help in direct messages or not.
client = Bot(description="Alarm Bot by All Meta",
             command_prefix="?", pm_help=False)
voice = None
player = None
waiting = False
# options


# This is what happens everytime the bot launches. In this case, it prints information like server count, user count the bot is connected to, and the bot id in the console.
# Do not mess with it because the bot can break, if you wish to do so, please consult me or someone trusted.
@client.event
async def on_ready():

    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to ' +
          str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(
        discord.__version__, platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    # Do not change this. This will really help us support you, if you need support.
    print('You are running BasicBot v2.1')
    print('Created by Habchy#1665')

    # This is buggy, let us know if it doesn't work.
    return await client.change_presence(game=discord.Game(name='?help'))

# This is a basic example of a call and response command. You tell it do "this" and it does it.


@client.command()
async def ping(*args):

    await client.say(":ping_pong: Pong!")


@client.command()
async def alarm(ttime, url):
    global waiting
    if(not waiting):
        waiting = True
        await client.say("Alarm set to %s in the nearest future!" % (ttime))
        x = deltaInSeconds(ttime)
        print(x)
        await asyncio.sleep(int(x))
        await alarmStart(url)
    else:
        await client.say("Already connected to a channel!")


@client.command()
async def stop(*args):
    if(client.is_voice_connected(client.get_server("334118303658147850"))):
        await voice.disconnect()
        player.stop()
        await client.say("Alarm off.")
    else:
        await client.say("Alarm off")


@client.command()
async def song(song):
    if(song.startswith("https://www.youtube.com/watch?")):
        await client.say("Default song set!")
        config["options"]["song"] = song
        writeToConfig()
    else:
        await client.say("Invalid URL!")


@client.command()
async def time(t):
    if(isTimeFormat(t)):
        await client.say("Default time set!")
        config["options"]["time"] = t
        writeToConfig()

    else:
        await client.say("Time must be formatted in this way: `HH:MM`")


@client.command(pass_context=True)
async def channel(ctx):
    await client.say("Set default voice channel to %s" % (ctx.message.author.voice.voice_channel.name))
    config["options"]["channel"] = ctx.message.author.voice.voice_channel.id
    writeToConfig()


async def alarmStart(url):
	global voice
	if config["options"]["channel"] is not None:
		voice = await client.join_voice_channel(client.get_channel(config["options"]["channel"]))
	else:
		voice = await client.join_voice_channel(client.get_channel("373999277292257300"))

	global player
	player = await voice.create_ytdl_player(url)
	player.start()


def writeToConfig():
    with io.open("config.json", "w", encoding="utf8") as o:
        str_ = json.dumps(config, indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        o.write(to_unicode(str_))


def isTimeFormat(input):
    try:
        strptime(input, '%H:%M')
        return True
    except ValueError:
        return False


def deltaInSeconds(time):
    x = strptime(time, "%H:%M")
    xToSec = timedelta(hours=x.tm_hour, minutes=x.tm_min).total_seconds()
    now = datetime.now(timezone("Europe/Oslo"))
    nowSeconds = now.hour*3600+now.minute*60+now.second
    # hvis tid er utenfor døgn, pluss på remaining time av døgnet
    return xToSec-nowSeconds if xToSec > nowSeconds else xToSec+(24*3600-nowSeconds)


client.run(config["token"])
