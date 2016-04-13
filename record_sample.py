# -*- coding: utf-8 -*-
# 録音したデータをフレーム毎に扱う

import pyaudio
import wave
import threading
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt

from Tkinter import *
root = Tk()

import tkSnack

import sys
sys.path.append('/Users/ishin/work/libsvm-3.20/python')
from svm import *
from svmutil import *


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
MODEL_FILE = 'svm.model'

print u"Enterキーを押すと，3秒間録音をします"
raw_input()

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)

print("* recording")

frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    # int型に変換して格納
    data = np.frombuffer(stream.read(CHUNK), dtype="int16")
    print max(np.array(data) ** 2)
    frames.extend(list(np.array(data)**2))

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

plt.plot(frames)
plt.show()

d = datetime.datetime.today()
# filename = "%s.wav" % d.strftime("%y-%m-%d_%H%M%S")
# wf = wave.open(filename, 'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(b''.join(frames))
# wf.close()
