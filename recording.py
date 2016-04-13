# -*- coding: utf-8 -*-
# 録音しながら特徴量を抽出しSVMによる識別を行う

import pyaudio
import wave
import threading
import time
import datetime
import math
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

        # 対象発話かそうでないかの判定
        pre_model = svm_load_model(PRE_MODEL_FILE)
        # 対象発話: 1, それ以外: -1
        pre_result = svm_predict([1], [[length_f, a]], pre_model)
        # SVMモデルの読み込み
        m = svm_load_model(MODEL_FILE)
        result = svm_predict([1], [[length_f, a]], m)

        f = open(RESULT_FILE, 'a')
        d = datetime.datetime.today()

        if pre_result[0][0] == 1:
            # 肯定 -1, 否定 1
            if result[0][0] == -1:
                f.write ("ACK\t%s\n" % d.strftime("%Y/%m/%d %H:%M:%S"))
            else:
                f.write ("NAK\t%s\n" % d.strftime("%Y/%m/%d %H:%M:%S"))
        else:
            f.write("ETC\t%s\n" % d.strftime("%Y/%m/%d %H:%M:%S"))

        f.close()
CHUNK = 200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
MODEL_FILE = 'svm.model'
PRE_MODEL_FILE = 'previous.model'

if __name__ == '__main__':

    p = pyaudio.PyAudio()
    tkSnack.initializeSnack(root)
    mysound = tkSnack.Sound()

    stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

    print("* recording")

    last_frames = [] # 最後600フレームを見る
    last_chunks = [] # 最後2000フレームを常に格納
    active_frames = [] # 発話を格納する
    power_boundary = None
    CONFIG_FILE = 'recording.conf'
    count = 0
    power_count = 0
    zerocross_count = 0
    START_NUM = 10
    END_NUM = 20
    ZEROCROSS_START = 4
    speaking = False # 発話中フラグ

    while True:
        # IOError の発生しうる箇所
        try:
            conf_file = open(CONFIG_FILE, 'r')
            power_boundary = int(conf_file.readline().rstrip())
            zerocross_boundary = int(conf_file.readline().rstrip())
            conf_file.close()
            # 1フレームを要素とするint型配列にする
            d = datetime.datetime.today()
            stream_data = stream.read(CHUNK)
            data = np.frombuffer(stream_data, dtype="int16")
        except:
            print "--------IO Error--------"
            continue

        # 追加処理
        last_frames.extend(data)
        last_chunks.extend(stream_data)
        if len(last_frames) > CHUNK * 3:
            del(last_frames[0:CHUNK])

        # バイナリデータだとint64型の2倍の長さを持つので CHUNK * 20 保存
        if len(last_chunks) > CHUNK * 10 * 2:
            del(last_chunks[0:CHUNK * 2])

        # 過去CHUNK * 3 フレームのパワーの平均
        np_frames = np.array(last_frames, dtype='int64')
        mean = round(math.log(np.sum(np_frames ** 2)), 2)
        zerocrosses = len(filter(lambda n:n<0, np_frames[:-1] * np_frames[1:]))
        # if count % 100 is 0:
        print mean, zerocrosses

        if speaking:
            print "** speaking"
            active_frames.extend(stream_data)
            if (mean < power_boundary):
                power_count += 1
            else:
                power_count = 0

            if (zerocrosses < zerocross_boundary):
                zerocross_count += 1
            else:
                zerocross_count = 0

            if (power_count > END_NUM and zerocross_count > END_NUM):
                print "ﾀﾞﾏｯﾀｱｱｱ", power_count
                speaking = False
                power_count = 0
                zerocross_count = 0
                d = datetime.datetime.today()
                filename = "wav/%s.wav" % d.strftime("%y-%m-%d_%H%M%S")
                wf = wave.open(filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(active_frames))
                wf.close()
                recognize(filename)
                active_frames = []

        else:
            print "-- not speaking"
            if(mean > power_boundary):
                power_count += 1
            else:
                power_count = 0

            if (zerocrosses > zerocross_boundary):
                zerocross_count += 1
            else:
                zerocross_count = 0

            if (power_count > START_NUM or zerocross_count > ZEROCROSS_START):
                print "ｼｬﾍﾞｯﾀｱｱｱｱｱｱｱｱｱｱ ", mean, power_count
                speaking = True
                power_count = 0
                zerocross_count = 0
                active_frames.extend(last_chunks)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
