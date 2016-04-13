# -*- coding: utf-8 -*-
# 録音しながらゼロクロスの数を数えるサンプルプログラム

import pyaudio
import wave
import threading
import time
import datetime
import math
import numpy as np

CHUNK = 200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
MODEL_FILE = 'svm.model'

if __name__ == '__main__':

    p = pyaudio.PyAudio()

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
    judge_count = 0
    START_NUM = 10
    END_NUM = 20
    speaking = False # 発話中フラグ

    while True:
        conf_file = open(CONFIG_FILE, 'r')
        power_boundary = int(conf_file.readline().rstrip())
        zerocross_boundary = int(conf_file.readline().rstrip())
        conf_file.close()
        # 1フレームを要素とするint型配列にする
        d = datetime.datetime.today()
        stream_data = stream.read(CHUNK)
        data = np.frombuffer(stream_data, dtype="int16")

        # 追加処理
        last_frames.extend(data)
        last_chunks.extend(stream_data)
        if len(last_frames) > CHUNK * 3:
            del(last_frames[0:CHUNK])

        # バイナリデータだとint64型の2倍の長さを持つので CHUNK * 20 保存
        if len(last_chunks) > CHUNK * 10 * 2:
            del(last_chunks[0:CHUNK * 2])

        # 過去CHUNK * 3 フレームのゼロクロス数
        np_frames = np.array(last_frames, dtype='int64')
        mean = round(math.log(np.sum(np_frames ** 2)), 2)
        zerocross = len(filter(lambda n:n<0, np_frames[:-1] * np_frames[1:]))
        if count % 200 is 0:
            print zerocross, mean


    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
