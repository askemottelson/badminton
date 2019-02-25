import sys
from scraper.methods import get_player_name
from methods import get_player_representation, get_pvp_representation, NoMatches

from db.db_handler import db
from db.models import *

import numpy as np
import pickle

import datetime
import random


def now():
    return datetime.datetime.now()

counter = 0
MIN_PRICE = 25000
MIN_YEAR = 2012
matches = db.query(Match).all()

matches = [
    m for m in matches
    if m.tournament.prizemoney > MIN_PRICE and m.tournament.year >= MIN_YEAR
]

# because the first matches take
# much faster to compute
np.random.shuffle(matches)

Xs = []
ys = []

time_last = now()
time_lefts = []

last_zero = False
for match in matches:
    p1 = match.player1
    p2 = match.player2

    p1_model = get_player_representation(p1, match)
    p2_model = get_player_representation(p2, match)

    try:
        if last_zero:
            X = get_pvp_representation(p1_model, p2_model, match)
            y = 0 # p1 won
        else:
            X = get_pvp_representation(p2_model, p1_model, match)
            y = 1 # p2 won
    except NoMatches:
        # print "no data"
        continue

    # swap order
    last_zero = not last_zero

    Xs.append(X)
    ys.append(y)

    counter += 1

    delta_time = now() - time_last
    left = len(matches) - counter

    time_left = (left * delta_time).total_seconds()
    time_last = now()
    time_lefts.append(time_left)

    avg = int(np.mean(time_lefts))
    print ">", 100*(counter / float(len(matches))), "%", "ETA:", str(datetime.timedelta(seconds=avg))

    #time_lefts = time_lefts[-10:]
    time_lefts.pop()


with open('data/Xy.pickle', 'wb') as handle:
    a = [
        Xs,
        ys
    ]
    pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
