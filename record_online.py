# -*- coding: utf-8 -*-
# 録音しながら特徴量を抽出しSVMによる識別を行う

import pyaudio
import wave
import threading
import time
import datetime
import numpy as np

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
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

d = datetime.datetime.today()
filename = "%s.wav" % d.strftime("%y-%m-%d_%H%M%S")
wf = wave.open(filename, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

tkSnack.initializeSnack(root)

mysound = tkSnack.Sound()
# mysound.data(b''.join(frames))
mysound.read(filename)

pitch = mysound.pitch(method="ESPS")
f0_list = []
for i, f0 in enumerate(pitch):
    time = round(i * 0.01, 2)
    if (f0[0] != 0):
        f0_list.append([time, f0[0]])

print f0_list

if len(f0_list) == 0:
    print "f0が録れませんでした"
else:
    x = np.array(f0_list)[:, 0]
    y = np.array(f0_list)[:, 1]
    # length = (np.amax(np.array(f0_list)[:, 0]) - np.amin(np.array(f0_list)[:, 0])) / 0.01
    # print length
    # a = ((length * np.dot(x, y)) - (sum(x) * sum(y))) / ((length * sum(x ** 2)) - (sum(x) ** 2))
    a = ((len(f0_list) * np.dot(x, y)) - (sum(x) * sum(y))) / ((len(f0_list) * sum(x ** 2)) - (sum(x) ** 2))

    length_f = len(f0_list) * 10

    print "特徴量: (%s, %s)" % (length_f, a)

    # SVMモデルの読み込み
    m = svm_load_model(MODEL_FILE)
    result = svm_predict([1], [[length_f, a]], m)

    # 肯定 -1, 否定 1

    if result[0][0] == -1:
        print "判定: 肯定応答"
    else:
        print "判定: 否定応答"
