''' Use this example from an interactive python session, for example:

>>> from isine import change
>>> change(880)
'''

from __future__ import print_function

import sys
import time
from threading import Thread
from multiprocessing import Queue

if sys.version_info[0] < 3:
    from Queue import Empty
else:
    from queue import Empty

from math import pi, sin
import struct
import alsaaudio

sampling_rate = 48000
duration = 0.250

format = alsaaudio.PCM_FORMAT_S16_LE
framesize = 1 # bytes per frame for the values above
channels = 1
target_size = int(sampling_rate * channels * duration)

def nearest_frequency(frequency):
    return float(int(frequency * duration)/(duration))

def generate(frequency):
    # generate a buffer with a sine wave of `frequency`
    # that is approximately `duration` seconds long

    size = int(duration * sampling_rate)
    
    sine = [ int(32767 * sin(pi * frequency * i / sampling_rate)) \
             for i in range(size)]
             
    return struct.pack('%dh' % size, *sine)
                                                                  
class SinePlayer(Thread):
    
    def __init__(self, frequency = 5000.0):
        Thread.__init__(self)
        self.setDaemon(True)
        self.device = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, device="hw:1,0")
        self.device.setchannels(channels)
        self.device.setformat(format)
        self.device.setrate(sampling_rate)
        self.queue = Queue()
        self.change(frequency)
                
    def change(self, frequency):
        '''This is called outside of the player thread'''
        # we generate the buffer in the calling thread for less
        # latency when switching frequencies

        if frequency > sampling_rate / 2:
            raise ValueError('maximum frequency is %d' % (sampling_rate / 2))

        if (frequency == -1):
            self.playing = 0
        else:
            f = nearest_frequency(frequency)
            # print('nearest frequency: %f' % f)
            buf = generate(f)
            self.queue.put(buf)
            self.playing = 1
                        
    def run(self):
        buffer = None
        while True:
          if self.playing:
            try:
                buffer = self.queue.get(False)
                time.sleep(duration)
                self.device.write(buffer)
#                print(time.time())
            except Empty:
                if buffer:
                    self.device.write(buffer)
                time.sleep(duration/2-0.01)
#                print(time.time())
                

isine = SinePlayer()
isine.start()

def change(f):
    isine.change(f)
    
