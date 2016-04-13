# -*- coding: utf-8 -*-

import datetime
import numpy as np

import sys
sys.path.append('/Users/ishin/work/libsvm-3.20/python')
from svm import *
from svmutil import *

MODEL_FILE = 'svm.model'

# SVMモデルの読み込み
m = svm_load_model(MODEL_FILE)

result = svm_predict([1], [[200, -81.17]], m)
print result[0], result[1], result[2]
