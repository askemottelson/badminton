from db.models import *
from db.db_handler import db
import requests
from lxml import html
from bs4 import BeautifulSoup
import requests



def get_player_url(player_url):
    try:
        return db.query(Player).filter(Player.url == player_url).one()
    except:
        if "https" in player_url:
            player_url = player_url.replace("https","http")
        else:
            player_url = player_url.replace("http","https")
        return db.query(Player).filter(Player.url == player_url).one()


def get_player_name(player_name):
    return db.query(Player).filter(Player.name == player_name).all()[0]

def delete_tournament(name):
    r = db.query(Tournament).filter(Tournament.name == name).one()
    matches = db.query(Match).filter(Tournament.url == r.url).all()

    for match in matches:
        ms1 = match.stat1
        ms2 = match.stat2

        sets = match.sets

        for s in sets:
            db.delete(s)

        db.delete(ms1)
        db.delete(ms2)
        
        db.delete(match)

    db.commit()

def make_player(player_url):
    try:
        return db.query(Player).filter(Player.url == player_url).one()
    except:
        # really make it
        pass

    if not ("http://" in player_url or "https://" in player_url):
        return None

    # uniform url protocol
    player_url = player_url.replace("http://", "https://")

    print "new player", player_url

    # find more information
    r = requests.get(player_url)
    soup = BeautifulSoup(r.content, "html.parser")


    cat = soup.find("div", {"class":"player-wins"}).findChildren()[2].contents[0].lower().split()

    if not "ms" in cat:
        print "> not men's singles"
        return None

    player = Player()

    try:
        ages = soup.find("div", {"class":"player-age"}).findChildren()[-1].contents[0].strip().split("/")

        player.birthyear = ages[2]
        player.birthmonth = ages[1]
        player.birthday = ages[0]
    except:
        # no birth information
        pass

    hand = soup.find("div", {"class":"player-handed"}).findChildren()[-1].contents[0].strip().lower()

    if hand != "n/a":
        player.handedness = "right" if "right" in hand else "left"

    info = soup.find("div", {"class":"player-profile-country-wrap"})

    # create player
    player.name = info.findChildren()[1].contents[0].strip().lower()
    player.country = info.findChildren()[0].attrs['title'].lower()
    player.gender = "male"
    player.playertype = "singles"
    player.url = player_url


    print player.name, player.country, player.gender, player.birth(), player.handedness

    db.add(player)
    db.commit()

    return player
