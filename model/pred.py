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
tournament.country = "THA"
start_date = 8
end_date = 13
name = "Thailand Masters"
prizemoney = 150000
city = "BANGKOK"
url = "https://bwfworldtour.bwfbadminton.com/tournament/3337/yonex-sunrise-hong-kong-open-2018/results/draw/ms"

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
        pass
        #raise e

# dopred("LIN Dan","LEE Cheuk Yiu",2)
# dopred("CHEAM June Wei","Pannawit THONGNUAM",2)
# dopred("Sitthikom THAMMASIN","Firman Abdul KHOLIK",2)
dopred("LU Guangzu","Koki WATANABE",2)
# dopred("Subhankar DEY","Brice LEVERDEZ",2)
# dopred("LEE Zii Jia","WONG Wing Ki Vincent",2)
# dopred("Lucas CORVEE","WANG Tzu Wei",2)
# dopred("Kean Yew LOH","ZHAO Junpeng",2)


