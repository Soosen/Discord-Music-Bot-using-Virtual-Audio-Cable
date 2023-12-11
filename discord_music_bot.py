import discord
import pyaudio
import time
import sys
import logging
import json

try:
    with open('config.json') as f:
        config = json.load(f)
except:
    print("[ERROR] Did not find config.json file")
    print("[ERROR] Closing the app...")
    time.sleep(3)
    sys.exit()

BOT_TOKEN = config["token"]
OWNER_ID = config["owners_id"]
DEFAULT_CHANNEL_ID = config["default_channel"]
VOICE_CLIENT = None

class PyAudioPCM(discord.AudioSource):
    def __init__(self, channels=2, rate=48000, chunk=960) -> None:
        p = pyaudio.PyAudio()
        input_device = None
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if "Virtual Audio Cable" in device_info['name'] and device_info["maxInputChannels"] == 2 and device_info["defaultSampleRate"] == 48000:
                input_device = i
                break

        if(not input_device):
            print("[ERROR] Did not find the Virtual Audio Cable. Make sure it is installed.")
            print("[ERROR] Closing the app...")
            time.sleep(3)
            sys.exit()

        self.chunks = chunk
        self.input_stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, input_device_index=input_device, frames_per_buffer=chunk)

    def read(self) -> bytes:
        return self.input_stream.read(self.chunks)
    


async def join_voice_channel():
    channel = get_owners_voice_channel()
    if(not channel):
        print("[WARNING] Did not find the owner in any of the voice channels!")
        print("[STATUS] Connecting to the default voice channel")

        channel = client.get_channel(DEFAULT_CHANNEL_ID)
        if(not channel):
            print("[ERROR] Default channel has not been found!")
            print("[ERROR] Closing the app...")
            time.sleep(3)
            sys.exit()

    voice_client = await channel.connect()
    VOICE_CLIENT = voice_client
    print("[STATUS] Successfully connected to the voice channel")
    voice_client.play(PyAudioPCM(), after=lambda e: print(f'Player error: {e}') if e else None)
    print("[STATUS] Playing sound from the Virtual Audio Cable...")

def get_owners_voice_channel():
    for guild in client.guilds:
        member = guild.get_member(OWNER_ID)
        if(not member):
            print("[WARNING] Did not find the owner or he does not exist")
            return None
        if(member.voice and member.voice.channel):
            return member.voice.channel
    return None

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

disable_discord_logs()
intents = discord.Intents.all()
intents.voice_states = True
client = discord.Client(intents=intents)     

@client.event
async def on_ready():
    print("[STATUS] Successfully connected to the discord server")
    await join_voice_channel()
    
client.run(BOT_TOKEN)