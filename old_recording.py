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

def recognize(filename):
    RESULT_FILE = 'result.txt'
    tkSnack.initializeSnack(root)

    mysound = tkSnack.Sound()
    mysound.read(filename)
    pitch = mysound.pitch(method="ESPS")
    f0_list = []
    for i, f0 in enumerate(pitch):
        time = round(i * 0.01, 2)
        if (f0[0] != 0):
            f0_list.append([time, f0[0]])
    if len(f0_list) > 0:
        x = np.array(f0_list)[:, 0]
        y = np.array(f0_list)[:, 1]
        a = ((len(f0_list) * np.dot(x, y)) - (sum(x) * sum(y))) / ((len(f0_list) * sum(x ** 2)) - (sum(x) ** 2))

        length_f = len(f0_list) * 10

        print "特徴量: (%s, %s)" % (length_f, a)

        # SVMモデルの読み込み
        m = svm_load_model(MODEL_FILE)
        result = svm_predict([1], [[length_f, a]], m)

        f = open(RESULT_FILE, 'a')
        d = datetime.datetime.today()
        # 肯定 -1, 否定 1
        if result[0][0] == -1:
            f.write ("肯定応答\t%s\n" % d.strftime("%H:%M:%S"))
        else:
            f.write ("否定応答\t%s\n" % d.strftime("%H:%M:%S"))
        f.close()

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
MODEL_FILE = 'svm.model'

p = pyaudio.PyAudio()
tkSnack.initializeSnack(root)
mysound = tkSnack.Sound()

stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)

print("* recording")

START_FRAMES = 5
END_FRAMES = 10
THRESHOLD = 10
first_frames = []
start_frames = [] # 発話始め検出用
end_frames = [] # 発話終わり検出用
active_frames = [] # 発話を格納する
boundary = None
count = 0
speaking = False # 発話中フラグ

while True:
    data = stream.read(CHUNK)
    mysound = tkSnack.Sound()
    mysound.data(b''.join(data))
    power = np.mean(mysound.power())
    if count < 10:
        first_frames.append(power)
    elif count is 10:
        boundary = round(np.mean(first_frames), 2) + THRESHOLD
        print "boundary: %s" % boundary
    count += 1
    if speaking:
        active_frames.append(data)
        if((power < boundary)):
            end_frames.append(data)
        if len(end_frames) > END_FRAMES:
            d = datetime.datetime.today()
            print "黙った!: %s" % d.strftime("%H:%M%S")
            speaking = False
            d = datetime.datetime.today()
            filename = "wav/%s.wav" % d.strftime("%y-%m-%d_%H%M%S")
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(active_frames))
            wf.close()
            end_frames = []
            active_frames = []
            recognize(filename)

    else:
        # 閾値を超えているか
        if((power > boundary) and (boundary is not None)):
            start_frames.append(data)

        if len(start_frames) > START_FRAMES:
            d = datetime.datetime.today()
            print "喋った!: %s" % d.strftime("%H:%M%S")
            speaking = True
            for frame_data in start_frames:
                active_frames.append(frame_data)
            start_frames = []
    print power

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

