import discord
import time
import sys
import logging
import json
from PyAudioPCM import PyAudioPCM 
from spotify_controler import Spotify_Controller
from urllib.parse import urlparse

try:
    with open('config.json') as f:
        config = json.load(f)
except:
    print("[ERROR] Did not find config.json file")
    print("[ERROR] Closing the app...")
    time.sleep(3)
    sys.exit()

DISCORD_BOT_TOKEN = config["discord_token"]
DISCORD_PREFIX = config["discord_prefix"]

SPOTIFY_CLIENT_ID = config["spotify_client_id"]
SPOTIFY_CLIENT_SECRET = config["spotify_client_secret"]
SPOTIFY_REDIRECT_URI = config["spotify_redirect_uri"]

WHITE_LIST = config["white_list"]

global VOICE_CLIENT
VOICE_CLIENT = None   

BLUE = 0x00008B
RED = 0xFF0000
YELLOW = 0xD5B60A

async def join_voice_channel(channel_id):
    global VOICE_CLIENT
    if(VOICE_CLIENT):
        await VOICE_CLIENT.disconnect()

    channel = client.get_channel(channel_id)
    if(not channel):
        return False


    VOICE_CLIENT = await channel.connect()
    start_transmitting(VOICE_CLIENT)
    return True

async def leave_channel():
    global VOICE_CLIENT
    if(VOICE_CLIENT and VOICE_CLIENT.is_connected()):
        await VOICE_CLIENT.disconnect()
        return True
    
    return False

def start_transmitting(voice_client):
    voice_client.play(PyAudioPCM(), after=lambda e: print(f'Player error: {e}') if e else None)


async def send_embed(ctx, title, color):
    embed = discord.Embed(
        title=title,
        color=color 
    )

    await ctx.channel.send(embed=embed)

def disable_discord_logs():
    logging.basicConfig(level=logging.INFO)

    # Get the loggers
    discord_client_logger = logging.getLogger('discord.client')
    discord_gateway_logger = logging.getLogger('discord.gateway')
    discord_voice_client_logger = logging.getLogger('discord.voice_client')

    # Set the logging level for the specific loggers to WARNING
    discord_client_logger.setLevel(logging.WARNING)
    discord_gateway_logger.setLevel(logging.WARNING)
    discord_voice_client_logger.setLevel(logging.WARNING)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

#setup
disable_discord_logs()
intents = discord.Intents.all()
intents.voice_states = True
client = discord.Client(intents=intents)  
spotify_controller = Spotify_Controller(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI) 

@client.event
async def on_ready():
    print("[STATUS] Successfully connected to the discord server")

@client.event
async def on_message(ctx):
    if(ctx.author.id == client.user.id):
        return

    if(not ctx.content.startswith(DISCORD_PREFIX)):
        return
    
    if(len(WHITE_LIST) > 0 and ctx.author.id not in WHITE_LIST):
        await send_embed(ctx,
                            f"YOU HAVE NO CONTROL OVER ME! :smiling_imp:",
                            BLUE)
        return
    
    if(ctx.content.startswith(DISCORD_PREFIX + "join")):
        if(ctx.author.voice):
            await join_voice_channel(ctx.author.voice.channel.id)
            await send_embed(ctx,
                            f"Sucesfully connected to: {ctx.author.voice.channel.name}",
                            BLUE)
        else:
            await send_embed(ctx,
                            f"Sorry. I was unable to conenct to your voice channel.",
                            RED)

    if(ctx.content.startswith(DISCORD_PREFIX + "leave")):
        if(await leave_channel()):
            await send_embed(ctx,
                                f"Sucesfully left the voice channel.",
                                BLUE)
        else:
            await send_embed(ctx,
                            f"I was not connected to any voice channel.",
                            RED)

    if(ctx.content.startswith(DISCORD_PREFIX + "play") and not ctx.content.startswith(DISCORD_PREFIX + "playlist")):
        if(len(ctx.content.split()) < 2):
            await send_embed(ctx,
                            f"{DISCORD_PREFIX}play [Song Name]",
                            YELLOW)
            return
        song_name = ""
        for word in ctx.content.split()[1:]:
            song_name += word + " "

        song = spotify_controller.search_for_song(song_name)
        if(song):
            if(spotify_controller.is_playing()):
                spotify_controller.add_to_queue(song)
                await send_embed(ctx,
                            f"Hey! I found the song! Let me put it to the queue. {spotify_controller.sp.track(song)['name']} by {spotify_controller.sp.track(song)['artists'][0]['name']}",
                            BLUE)
            else:
                spotify_controller.play(song)
                await send_embed(ctx,
                            f"Hey! I found the song! Playing:{spotify_controller.sp.track(song)['name']} by {spotify_controller.sp.track(song)['artists'][0]['name']}",
                            BLUE)

            if(not VOICE_CLIENT or not VOICE_CLIENT.is_connected()):
                await join_voice_channel(ctx.author.voice.channel.id)


        else:
            await send_embed(ctx,
                            f"Sorry, I could not find the \"{song_name}\" song...",
                            YELLOW)

    if(ctx.content.startswith(DISCORD_PREFIX + "skip")):
        current_track = spotify_controller.sp.current_playback()['item']['name']
        spotify_controller.next_track()
        time.sleep(1)
        next_track = spotify_controller.sp.current_playback()['item']['name']
        await send_embed(ctx,
                            f"Skipped {current_track}. Now palying {next_track}",
                            BLUE)

    if(ctx.content.startswith(DISCORD_PREFIX + "previous")):
        try:
            spotify_controller.previous_track()
            time.sleep(1)
            next_track = spotify_controller.sp.current_playback()['item']['name']
            await send_embed(ctx,
                                f"Returned to {next_track}",
                                BLUE)
        except:
            await send_embed(ctx,
                                f"There were no previous tracks...",
                                RED)

    if(ctx.content.startswith(DISCORD_PREFIX + "pause")):
        spotify_controller.pause()
        await send_embed(ctx,
                                f"Paused...",
                                BLUE)
    
    if(ctx.content.startswith(DISCORD_PREFIX + "resume")):
        spotify_controller.resume()
        await send_embed(ctx,
                                f"Resumed {spotify_controller.sp.current_playback()['item']['name']}",
                                BLUE)

    if(ctx.content.startswith(DISCORD_PREFIX + "clear")):
        spotify_controller.clear_queue()
        await send_embed(ctx,
                                f"TO DO",
                                YELLOW)

    if(ctx.content.startswith(DISCORD_PREFIX + "volume")):
        if(len(ctx.content.split()) != 2):
            if(ctx.content.startswith(DISCORD_PREFIX + "clear")):
                spotify_controller.clear_queue()
                await send_embed(ctx,
                                f"{DISCORD_PREFIX}volume [0-100]",
                                YELLOW)
            return
        
        volume_value = ctx.content.split()[1]
        if(volume_value.isnumeric()):
            spotify_controller.volume(max(min(int(volume_value), 100),0))
            await send_embed(ctx,
                                f"Volume changed to {volume_value}",
                                BLUE)
        else:
            await send_embed(ctx,
                                f"{DISCORD_PREFIX}volume [0-100]",
                                YELLOW)

    if(ctx.content.startswith(DISCORD_PREFIX + "playlist")):
        if(len(ctx.content.split()) != 2):
            await send_embed(ctx,
                                f"{DISCORD_PREFIX}playlist [url]",
                                YELLOW)
            return
        
        spotify_controller.start_playlist(ctx.content.split()[1])
        await send_embed(ctx,
                                f"I found the playlist. Let me play it.",
                                BLUE)
        
    if(ctx.content.startswith(DISCORD_PREFIX + "help")):
            embed = discord.Embed(
                    title="Commands",
                    description=f"""{DISCORD_PREFIX}play [song name] 
                                    {DISCORD_PREFIX}pause
                                    {DISCORD_PREFIX}resume
                                    {DISCORD_PREFIX}skip
                                    {DISCORD_PREFIX}previous
                                    {DISCORD_PREFIX}playlist [url]
                                    {DISCORD_PREFIX}clear
                                    {DISCORD_PREFIX}volume [0-100]
                                    {DISCORD_PREFIX}help""",
                color=BLUE)

            await ctx.channel.send(embed=embed)
        

    
client.run(DISCORD_BOT_TOKEN)