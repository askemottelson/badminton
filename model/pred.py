### test lol
from scraper.methods import get_player_name
from methods import get_player_representation, get_pvp_representation, get_vector
from db.models import Tournament, Match
from sklearn.externals import joblib
from model.help import removed_keys
from model.train_nn import make_keras
import numpy as np

tournament = Tournament()
tournament.week = 1
tournament.year = 2019
tournament.country = "ENG"
start_date = 6
end_date = 10
name = "ONEX ALL ENGLAND OPEN BADMINTON CHAMPIONSHIPS 2019"
prizemoney = 1000000
city = "BIRMINGHAM"
url = "https://bwfworldtour.bwfbadminton.com/tournament/3376/yonex-all-england-open-badminton-championships-2019/"

clf = joblib.load('data/dnn.pkl') 

def dopred(p1_name, p2_name, round_no):
    match = Match()
    match.tournament = tournament
    match.round_no = round_no

    try:
        p1_name = p1_name.lower()
        p2_name = p2_name.lower()

        p1 = get_player_name(p1_name)
        p2 = get_player_name(p2_name)

        p1_model = get_player_representation(p1, match)
        p2_model = get_player_representation(p2, match)

        rep = get_pvp_representation(p1_model, p2_model, match)

        match = get_vector(rep)
        match = match.reshape(1, -1)

        p = clf.predict(match)[0][0]

        print p1_name, "\t", p2_name, "\t", p, "\t", clf.predict_proba(match)[0][p], "\t%"
    except Exception as e:

        raise e

dopred("Kento MOMOTA", "Khosit PHETPRADAB",0)
dopred("Kantaphon WANGCHAROEN", "WANG Tzu Wei",0)
dopred("KIDAMBI Srikanth", "Brice LEVERDEZ",0)
dopred("Jonatan CHRISTIE", "LEE Dong Keun",0)
dopred("CHOU Tien Chen", "HUANG Yuxiang",0)
dopred("Tommy SUGIARTO", "Rajiv OUSEPH",0)
dopred("Anthony Sinisuka GINTING", "NG Ka Long Angus",0)
dopred("SAI PRANEETH B.", "PRANNOY H. S.",0)
dopred("LU Guangzu", "Hans-Kristian Solberg VITTINGHUS",0)
dopred("Sameer VERMA", "Viktor AXELSEN",0)
dopred("Jan O JORGENSEN", "Kazumasa SAKAI",0)
dopred("Rasmus GEMKE", "CHEN Long",0)
dopred("LIN Dan", "Kanta TSUNEYAMA",0)
dopred("Kenta NISHIMOTO", "SON Wan Ho",0)
dopred("Suppanyu AVIHINGSANON", "LIEW Daren",0)
dopred("Anders ANTONSEN", "SHI Yuqi",0)



