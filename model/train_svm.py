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
from sklearn.svm import LinearSVC, SVC
import math
import numpy as np
from sklearn.feature_selection import VarianceThreshold
from sklearn.multiclass import OneVsRestClassifier
from methods import get_vector
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import f_classif

TEST = True



def make_clf():

    clf = GridSearchCV(
        estimator=Pipeline(
            [
                ("normalize", StandardScaler()),
                ("reduce_dim", VarianceThreshold()),
                ("pca", PCA()),
                ("clf", SVC())
            ]
        ),
        param_grid={
            # "clf__C": [.01, .1, 1],
            # "clf__probability": [True],
            # "clf__kernel": ["linear"],
            # "reduce_dim__threshold": [0, .1],
            # "pca__n_components": [2, 3],

            "clf__C": [.1],
            "clf__probability": [True],
            "clf__kernel": ["linear"],
            "reduce_dim__threshold": [0],
            "pca__n_components": [2]
        },
        scoring="f1_micro"
    )
    return clf

make_clf()

now = datetime.datetime.now()
thisyear = float(now.year)

Xs = []

print "load data ..."

train_Xs = []
train_ys = []

test_Xs = []
test_ys = []

with open('data/Xy.pickle', 'rb') as handle:
    data = pickle.load(handle)

    reps = data[0]
    ys = data[1]

    # print reps[0].keys()

    for index,rep in enumerate(reps):

        y = int(ys[index])
        X = get_vector(rep)

        if random.randint(1, 100) > 80:
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


if TEST:

    print "train model ..."

    clf = make_clf()
    clf.fit(train_Xs, train_ys)

    print "> done"
    print "best parameters:"
    print clf.best_params_


    print "estimating accuracy ..."

    pred_ys = clf.predict(test_Xs)
    score = f1_score(test_ys, pred_ys, average="binary")

    print "> done"
    print "f1=", score

    die()


print "train full model ..."

clf = make_clf()
allXs = np.concatenate((train_Xs, test_Xs), axis=0)
allYs = np.concatenate((train_ys, test_ys), axis=0)

clf.fit(allXs, allYs)

print "> done"

print "save model ..."

joblib.dump(clf, 'data/svm.pkl')

print "> done"
