from sklearn.externals import joblib
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from keras.constraints import maxnorm
from keras import regularizers
from keras.layers.advanced_activations import LeakyReLU

import pickle
import datetime
import random
import math
import numpy as np
import random

from model.help import removed_keys, make_keras_picklable
from methods import get_vector
import collections

make_keras_picklable()


u0 = -1
TEST = False

def make_clf():
    clf = GridSearchCV(
        estimator=Pipeline(
            [
                ("reduce_dim", VarianceThreshold()),
                # ("standardize", StandardScaler()),
                ("normalize", MinMaxScaler()),
                ("clf", KerasClassifier(build_fn=make_keras))
            ]
        ),
        param_grid={
            "reduce_dim__threshold": [0],
            "clf__batch_size": [5],
            "clf__epochs": [25]
        },
        scoring="f1_micro"
    )
    return clf


def make_keras():
    model = Sequential()

    model.add(Dense(units=u0*4, kernel_initializer='he_uniform', activation='relu'))#, kernel_regularizer=regularizers.l2(0.01)))#, kernel_constraint=maxnorm(5)))
    # model.add(Dropout(0.2))
    model.add(Dense(units=u0, kernel_initializer='he_uniform', activation='relu'))#, kernel_regularizer=regularizers.l2(0.01)))#, kernel_constraint=maxnorm(3)))
    

    # output binary
    # model.add(Dropout(0.4))
    model.add(Dense(units=1, kernel_initializer='glorot_uniform', activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


if __name__ == "__main__":
    # # just checking that this works
    # toy_Xs = np.array([
    #     [0,1,2,3],
    #     [0,2,3,1],
    #     [0,1,2,3]
    # ])
    # toy_ys = np.array([0,1,0])
    # u0 = len(toy_Xs[0])
    # clf = make_clf()
    # clf.fit(toy_Xs, toy_ys)

    # now actually begin
    now = datetime.datetime.now()
    thisyear = float(now.year)

    Xs = []

    print "load data ..."

    train_Xs = []
    train_ys = []

    test_Xs = []
    test_ys = []

    last_zero = False

    with open('data/Xy.pickle', 'rb') as handle:
        data = pickle.load(handle)

        reps = data[0]
        ys = data[1]

        # print reps[0].keys()

        for index,rep in enumerate(reps):

            y = int(ys[index])
            X = get_vector(rep)

            if random.randint(1, 100) > 85:
                test_Xs.append(X)
                test_ys.append(y)
            else:
                train_Xs.append(X)
                train_ys.append(y)

    print "> done"

    train_Xs = np.array(train_Xs)
    train_ys = np.array(train_ys)
    test_Xs = np.array(test_Xs)
    test_ys = np.array(test_ys)

    print "train data:", len(train_Xs)
    print "test data:", len(test_Xs)
    u0 = len(train_Xs[0])

    if TEST:
        print "train model ..."

        clf = make_clf()
        clf.fit(train_Xs, train_ys)

        print "> done"
        print "estimating accuracy ..."

        print "... f1 ..."
        print "training:"
        pred_ys = clf.predict(train_Xs)
        score = f1_score(train_ys, pred_ys, average="binary")

        print "f1_train=", score

        print "test:"
        pred_ys = clf.predict(test_Xs)
        score = f1_score(test_ys, pred_ys, average="binary")

        print "f1_test=", score

        print "baseline=", np.mean(test_ys)
        print "> done"

        print "Best parameters set found on development set:"
        print clf.best_params_

        # die()

    # only go here if not testing
    print "train full model ..."

    clf = make_clf()
    allXs = np.concatenate((train_Xs, test_Xs), axis=0)
    allYs = np.concatenate((train_ys, test_ys), axis=0)

    clf.fit(allXs, allYs)

    print "> done"

    print "save model ..."

    joblib.dump(clf, 'data/dnn.pkl')

    print "> done"
