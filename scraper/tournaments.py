import requests
from lxml import html
from bs4 import BeautifulSoup
import requests

from db.db_handler import db
from db.models import Player, PlayerRanking, Tournament, Match, MatchStats, Set
from sqlalchemy.orm.session import make_transient

from methods import get_player_name, delete_tournament

import sys
import re
import traceback

requests.packages.urllib3.disable_warnings()

years = range(2010,2019)


def make_url(year):
    year = str(year)
    return "http://bwfbadminton.com/calendar/"+year+"/completed/"


def getint(num):
    try:
        return int(num)
    except:
        return 0


def make_scrape_tournament(tournament, suffix="podium"):
    r = requests.get(tournament.url + suffix, verify=False)
    soup = BeautifulSoup(r.content, "html.parser")

    ul = soup.find("ul", {"id":"ajaxTabsResults"})

    if ul is None:
        ul = soup.find("ul", {"id":"ajaxTabs"})

    if ul is None:
        make_scrape_tournament(tournament, "results/podium")
        return

    lis = ul.findAll("li")

    # first is draws, last is podium; disregard those
    for round_no,li in enumerate(lis[1:-1]):

        url = li.findChildren()[0].attrs['href']
        date = li.findChildren()[0].contents[0].strip()

        make_scrape_round(tournament, round_no, date, url)



def make_scrape_round(tournament, round_no, date, url):
    print "round ", round_no, "at", date

    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.content, "html.parser")

    matches = soup.findAll("a", {"id":"match-link"})

    for match in matches:

        rounds = match.find("div", {"class":"round_time"}).find("div", {"class":"round"}).contents[0].strip().split("-")


        gametype = rounds[0].strip().lower()

        if not(gametype in ["ms", "mens singles", "men's singles"] or 'ms' in gametype):
            # only men's single
            continue

        details = match.find("div", {"class": "score"}).contents[0].strip().lower()
        no_match = "no match" in details or "retirement" in details or "walkover" in details

        if no_match:
            continue
        
        try:
            player1_name = match.find("div", {"class": "player1"}).contents[0].strip().lower()
            player2_name = match.find("div", {"class": "player3"}).contents[0].strip().lower()
        except:
            # no first/second player; walk over
            continue

        if player1_name == '' or player2_name == '':
            continue

        # rm digigts
        player1_name = ''.join([i for i in player1_name if not i.isdigit()])
        player2_name = ''.join([i for i in player2_name if not i.isdigit()])

        # rm brackets
        player1_name = ''.join([i for i in player1_name if not i in '[]']).strip()
        player2_name = ''.join([i for i in player2_name if not i in '[]']).strip()

        try:
            player1 = get_player_name(player1_name)
        except:
            player1 = Player()
            player1.name = player1_name
            db.add(player1)

        try:
            player2 = get_player_name(player2_name)
        except:
            player2 = Player()
            player2.name = player2_name
            db.add(player2)

        match_link = match.attrs['href']
        match_link = match_link.replace("&stab=result", "&stab=match")

        r = requests.get(match_link, verify=False)
        soup = BeautifulSoup(r.content, "html.parser")

        duration = soup.find("h3", {"class":"match-duration"}).contents[0].strip()
        try:
            duration = int(re.findall('\d+', duration)[0])
        except:
            duration = 0

        try:
            m = Match()

            m.tournament = tournament
            m.player1 = player1
            m.player2 = player2
            m.round_no = round_no
            m.duration = duration

            data = soup.find("div", {"class":"live-profile-row"}).findAll("tr")

            ms1 = MatchStats()
            ms1.max_consecutive_points = getint(data[0].findChildren()[0].contents[0].strip())
            ms1.game_points = getint(data[1].findChildren()[0].contents[0].strip())
            ms1.rallies_played = getint(data[2].findChildren()[0].contents[0].strip())
            ms1.rallies_won = getint(data[3].findChildren()[0].contents[0].strip())
            ms1.smash_winners   = getint(data[4].findChildren()[0].contents[0].strip())
            ms1.net_winners = getint(data[5].findChildren()[0].contents[0].strip())
            ms1.clear_winners = getint(data[6].findChildren()[0].contents[0].strip())
            ms1.total_points_played = getint(data[7].findChildren()[0].contents[0].strip())
            ms1.total_points_won = getint(data[8].findChildren()[0].contents[0].strip())

            db.add(ms1)

            ms2 = MatchStats()
            ms2.max_consecutive_points = getint(data[0].findChildren()[-1].contents[0].strip())
            ms2.game_points = getint(data[1].findChildren()[-1].contents[0].strip())
            ms2.rallies_played = getint(data[2].findChildren()[-1].contents[0].strip())
            ms2.rallies_won  = getint(data[3].findChildren()[-1].contents[0].strip())
            ms2.smash_winners = getint(data[4].findChildren()[-1].contents[0].strip())
            ms2.net_winners = getint(data[5].findChildren()[-1].contents[0].strip())
            ms2.clear_winners = getint(data[6].findChildren()[-1].contents[0].strip())
            ms2.total_points_played  = getint(data[7].findChildren()[-1].contents[0].strip())
            ms2.total_points_won = getint(data[8].findChildren()[-1].contents[0].strip())

            db.add(ms2)

            m.stat1 = ms1
            m.stat2 = ms2

            print "> added match ", m.player1.name, "vs", m.player2.name

            db.add(m)

            sets = match.find("div", {"class": "score"}).contents[0].strip().split(",")

            for i,game_set in enumerate(sets):
                scores = game_set.split("-")
                s = Set()
                s.match = m
                s.index = i
                s.score_1 = scores[0]
                s.score_2 = scores[1]

                db.add(s)
        except:
            # no match
            continue




def make_scrape_page(year):
    url = make_url(year)
    
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.content, "html.parser")

    rows = soup.findAll("tr")

    for tr in rows[1:]:
        tds = tr.findAll("td")

        week = tds[0].contents[0].strip()

        try:
            country = tds[1].findChildren()[0].findChildren()[0].contents[0].strip()
        except IndexError:
            continue

        dates = tds[2].contents[0].strip()
        name = tds[3].findChildren()[0].findChildren()[0].contents[0].strip()
        url = tds[3].findChildren()[0].findChildren()[0].attrs['href']
        money = tds[4].findChildren()[0].contents[0].strip()

        if not "bwfbadminton.com" in url:
            continue

        if money == "-":
            prizemoney = 0
        else:
            prizemoney = int(re.sub(r'[^\d.]', '', money))

        category = tds[5].findChildren()[0].findChildren()[0].contents[0].strip()
        city = tds[6].findChildren()[0].contents[0].strip()

        tours = db.query(Tournament).filter(Tournament.name == name, Tournament.year == year).all()
        has_tournament = len(tours) > 0

        if has_tournament:
            continue

        t = Tournament()
        t.week = week
        t.start_date = dates.split("-")[0]
        t.end_date = dates.split("-")[1]
        t.name = name
        t.url = url
        t.country = country
        t.prizemoney = prizemoney
        t.category = category
        t.city = city
        t.year = year

        print "new tournament", t.name
        print t.url

        def go(t):

            try:
                make_scrape_tournament(t)
            except requests.exceptions.SSLError:
                print "bwfbadminton.com is down 1"
                return False
            except requests.exceptions.ConnectionError:
                # does not exist
                print "bad connection"
                return False
            except Exception as e:
                # e.g., timeout ...

                print "<<<<TRY AGAIN>>>>>"
                traceback.print_exc()

                # try again
                return go(t)

            return True

        success = go(t)
        if success:
            db.add(t)
            db.commit()
        else:
            db.rollback()



    
if __name__ == "__main__":
    # t = Tournament()
    # t.url = "https://bwfworldtour.bwfbadminton.com/tournament/3139/princess-sirivannavari-thailand-masters-2018/"
    # make_scrape_tournament(t)

    if(len(sys.argv) > 1):
        years = [int(sys.argv[1])]

    for year in years:
        print year
        try:
            make_scrape_page(year)
        except requests.exceptions.SSLError:
            print "bwfbadminton.com is down 2"
            break


