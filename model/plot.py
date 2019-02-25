from matplotlib import pyplot as plt

import pickle
import datetime
import random
import math
import numpy as np

from model.help import removed_keys
from methods import get_vector

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

print "load data ..."

Xs = []
ys = []

last_zero = False

with open('data/Xy.pickle', 'rb') as handle:
    data = pickle.load(handle)

    reps = data[0]
    ys = data[1]

    for i in range(0, len(reps), 2):
        index = i
        if last_zero:
            index += 1
        last_zero = not last_zero

        rep = reps[index]
        y = ys[index]

        X = get_vector(rep)
        
        Xs.append(X)
        ys.append(y)

print "> done"

print "reduce dim ..."

scaler = StandardScaler()
Xs = scaler.fit_transform(Xs)
pca = PCA(n_components=2)
reduced = pca.fit_transform(Xs)

print "> done"

print "plot ..."

c = [["blue","red"][int(i)] for i in ys]
plt.scatter(reduced[:, 0], reduced[:, 1], c=c, alpha=.1)

plt.show()