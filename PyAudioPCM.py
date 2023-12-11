import pyaudio
import time
import sys
import discord

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