import pickle
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.externals import joblib
from model.help import removed_keys
import datetime
import random
from sklearn.metrics import f1_score
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import math
import numpy as np
from sklearn.feature_selection import VarianceThreshold

reps = []
ys = []



with open('data/Xy.pickle', 'rb') as handle:
    data = pickle.load(handle)

    reps = data[0]
    ys = data[1]

    for index, rep in enumerate(reps):        
        rep = reps[index]
        y = ys[index]

        reps.append(rep)
        ys.append(y)


keys = reps[0].keys()
keys.sort()

print ";".join(keys + ["y"])

for rep,y in zip(reps, ys):
    X = [
        str(rep[key]) for key in keys
    ]

    print ";".join(X + [str(y)])



