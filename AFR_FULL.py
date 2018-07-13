#!/usr/bin/env python2
#
# sudo apt-get -y install python-alsaaudio
#
import Adafruit_CharLCD as LCD
import time,sys,os
from ScrollLCD import *


# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()
#lcd.begin(16,1)

# create some custom characters
lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.create_char(7, [31, 17, 21, 21, 21, 21, 17, 31])

lcd.clear()
lcd.set_color(1.0, 0.0, 1.0)
buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
            (LCD.LEFT,   'Left'  , (1,0,0)),
            (LCD.UP,     'Up'    , (0,0,1)),
            (LCD.DOWN,   'Down'  , (0,1,0)),
            (LCD.RIGHT,  'Right' , (1,0,1)) )

while lcd.is_pressed(buttons[0][0]) == False:
	lcd.clear()
	lcd.message('Remove both sou-\nnd cards.')
	time.sleep(1)
	lcd.clear()
	lcd.message('Reinsert (speaker\n card first)')
	time.sleep(1)
	lcd.clear()
	lcd.message('Hold select\n to continue')
	time.sleep(1)
lcd.clear()

lcd.set_color(1.0, 1.0, 0.0)

lcd.message('Launching AFR\nSystem 2.5')
time.sleep(1)
lcd.clear()
lcd.message('Testing...')
os.system('~/freq 1000')
lcd.clear()
lcd.message('Success!\nStarting...')

#text = "Remove both sound cards. Reinsert both. (speaker card first). Press select once done."
#scroll(lcd, text)
#time.sleep(5)

import sys
import getopt
import logging
import alsaaudio as aa
from struct import unpack
import numpy as np
import time
import isine 
import json
import time
import readadc
import datetime
from time import gmtime, strftime
import time,sys

import Adafruit_CharLCD as LCD


# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

# create some custom characters
lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.create_char(7, [31, 17, 21, 21, 21, 21, 17, 31])


# temperature sensor middle pin connected channel 0 of mcp3008
sensor_pin = 0
readadc.initialize()
def usage():
       print('usage: recordtest.py [-d <device>] <file>')
       sys.exit(2)

          
#logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


logging.debug("init")
if __name__ == '__main__':

   dev = 'default'
   card = 1
   sample_rate = 44100
   chunk = 2048

   opts, args = getopt.getopt(sys.argv[1:], 'd:c:')
   for o, a in opts:
      if o == '-d':
         dev = a
      if o == '-c':
         card = int(a)

   # Open the device in nonblocking capture mode. The last argument could
   # just as well have been zero for blocking mode. Then we could have
   # left out the sleep call in the bottom of the loop
   audioL = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, device='hw:2,0')
   audioR = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, device='hw:1,0')
   #audio = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, device=dev, cardindex=card)
   #audio = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NONBLOCK, device='default')

   # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
   audioL.setchannels(1)
   audioL.setrate(sample_rate)
   audioL.setformat(aa.PCM_FORMAT_S16_LE)

   audioR.setchannels(1)
   audioR.setrate(sample_rate)
   audioR.setformat(aa.PCM_FORMAT_S16_LE)

   # The period size controls the internal number of frames per period.
   # The significance of this parameter is documented in the ALSA api.
   # For our purposes, it is suficcient to know that reads from the device
   # will return this many frames. Each frame being 2 bytes long.
   # This means that the reads below will return either 320 bytes of data
   # or 0 bytes of data. The latter is possible because we are in nonblocking
   # mode.
   audioL.setperiodsize(chunk)
   audioR.setperiodsize(chunk)

   logging.debug("aa.PCM end")

def GetFreq(freq, freqs, power):
       i = 0
       while freq > freqs[i]:
              i = i+1
#       print(freq, freqs[i], power[i], i)
       return freqs[i-1], power[i-1]


lL, dataL = audioL.read()
lR, dataR = audioR.read()
audioL.pause(1)
audioR.pause(1)
alldiff = [0]*1000000
ct = 0
xxxx=0
while xxxx!=1:
   xxxx=0
   isine.change(-1)
   sensor_data = readadc.readadc(sensor_pin,
                                 readadc.PINS.SPICLK,
                                 readadc.PINS.SPIMOSI,
                                 readadc.PINS.SPIMISO,
                                 readadc.PINS.SPICS)
   millivolts = sensor_data * (3300.0 / 1024.0)
   # 10 mv per degree
   temp_C = ((millivolts) / 10.0) - 50.0
   # convert celsius to fahrenheit
   temp_F = (temp_C * 9.0 / 5.0) + 32
   # remove decimal point from millivolts
   millivolts = "%d" % millivolts
   # show only one decimal place for temprature and voltage readings
   temp_C = "%.1f" % temp_C
   temp_F = "%.1f" % temp_F
   print ('\n\n\n\n')
   print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*['freq','left','right','diff','peakL','peakR','tempC','date time']))
   print('-' * 57)
   freqdiff = [0]*100000
#   change(1)
#   for f in [500, 1000, 1500, 2000, 2500, 3000, 3500]:
#   freqs = [1000,8000,15000,20000]:
#   os.system('char-text '+ freqs)
#   for f in [1000,8000,15000,20000]:
#   for f in [1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,15000,20000]:
   for f in [6000,8000,10000,15000,20000]:
#   for f in [22000,23000,24000]:
#   for f in [500,1000,1500,2000,2500,3000,3500,4000,4500,5000,6000,7000,8000,9000,10000,15000,20000]:
       isine.change(-1)
       lcd.clear()
       lcd.message('Press select\n'+str(f))
       while lcd.is_pressed(buttons[0][0]) == False:
		xxxxadsf=0	

       lcd.clear()
       lcd.set_color(1.0, 0.0, 0.0)
       values = [0]*8
       values[0] = f
       isine.change(f)
       start = time.time()
       # Read data from device
       audioL.pause(0)
       audioR.pause(0)
       while time.time()- start < 10.0:
              lL, dataL = audioL.read()
              lR, dataR = audioR.read()
       audioR.pause(1)
       audioL.pause(1)

       if lL>0:
              sampsL= np.fromstring(dataL, dtype='int16')
              nL = sampsL.size
              freqsL = np.fft.rfftfreq(nL, d=1./sample_rate)
              fourier1L = np.fft.rfft(sampsL)
              fourierL = np.delete(fourier1L, len(fourier1L)-1)
              powerL  = np.log10(np.abs(fourierL)+0.000001)**2
              idxL = powerL.argmax()
              peakPowerL = powerL[idxL]
              peakFreqL = freqsL[idxL]
              frL, powL = GetFreq(f, freqsL, powerL)
              #print("L: "+str(frL)+" "+ str(powL))
	      values[1] = str(powL)
	      values[4] = round(peakFreqL,-2)
#	      if peakFreqL == frL:
#		values[4] = 1
#	      else:
#		values[4] = 0
#              print(peakFreqL, peakPowerL, frL, powL)
       else:
              print("error:",lL)


       #BEGIN RIGHT SAMPLE
       if lR>0:
              sampsR= np.fromstring(dataR, dtype='int16')
              nR = sampsR.size
              freqsR = np.fft.rfftfreq(nR, d=1./sample_rate)
              fourier1R = np.fft.rfft(sampsR)
              fourierR = np.delete(fourier1R, len(fourier1R)-1)
              powerR  = np.log10(np.abs(fourierR)+0.000001)**2
              idxR = powerR.argmax()
              peakPowerR = powerL[idxR]
              peakFreqR = freqsL[idxR]
              frR, powR = GetFreq(f, freqsR, powerR)
#              print(peakFreqR, peakPowerR, frR, powR)
#              print("R: "+str(frR)+" "+ str(powR))
	      values[2] = str(powR)
	      values[5] = round(peakFreqR,-2)

#	      if peakFreqR == frR:
#		values[5] = 1
#	      else:
#		values[5] = 0
#   	      print f              
       else:
              print("error:",lR)
       values[3] = str(float(values[1])-float(values[2]))
       freqdiff[f]=abs(float(values[3]))
       values = [ int(round(float(x))) for x in values ]
       values[6] = temp_C
       values[7] = strftime("%d-%b-%Y %H:%M:%S", gmtime())
       print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
       lcd.clear()
       lcd.set_color(0.0, 1.0, 0.0)
       lcd.message('F:' + str(values[0]) + ' T:' + str(values[6]) + '\n' + 'I:' + str(values[1]) + ' O:' + str(values[2]) + ' D:' + str(values[1]-values[2]))
       sys.stdout.flush()
       time.sleep(5)
   alldiff[ct]=sum(freqdiff) / float(len(freqdiff))
   print alldiff[ct]
   print alldiff[ct]-alldiff[0]
   isine.change(-1)
   time.sleep(0)
   ct = ct+1


