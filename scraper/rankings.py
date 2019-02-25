import sys
import requests
from lxml import html
from bs4 import BeautifulSoup
import requests

from db.db_handler import db
from db.models import Player, PlayerRanking

from methods import get_player_url, make_player


years = range(2010,2019)
weeks = range(1,53)

def make_url(year, week, page):
    year = str(year)
    week = str(week)
    page = str(page)
    return "http://bwfbadminton.com/rankings/2/bwf-world-rankings/6/men-s-singles/"+year+"/"+week+"/?rows=100&page_no="+page


def make_scrape_page(year, week, page):
    url = make_url(year, week, page)
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    rows = soup.findAll("tr")
    del rows[::2] # remove every second item

    for row in rows:
        tds = row.findAll("td")

        rank = int(tds[0].contents[0].strip())
        country = tds[1].findChildren()[0].findChildren()[0].contents[0].strip().upper()
        name = tds[2].findChildren()[0].findChildren()[0].findChildren()[0].contents[0].strip().lower()

        winslosses = tds[4].contents[0].strip().split(" - ")
        wins = int(winslosses[0])
        losses = int(winslosses[1])
        
        try:
            money = float(tds[5].contents[0].strip().replace(',','').replace('$',''))
        except ValueError:
            # N/A
            money = 0.0

        pointstournaments = tds[6].findChildren()[0].contents[0].strip().replace(',','').split(" / ")
        points = int(pointstournaments[0])
        tournaments = int(pointstournaments[1])

        player_url = tds[2].find("a").attrs['href']

        try:
            player = get_player_url(player_url)
        except:
            player = make_player(player_url)

        if player is None:
            # player is no longer active player
            continue

        print ">", player.name

        # if already scraped this week
        hasrank = len(
            db.query(
                PlayerRanking
            ).filter(PlayerRanking.player == player, PlayerRanking.week == week, PlayerRanking.year == year)
             .all()
        ) > 0

        if hasrank:
            print "has rank", year, ":", week
            continue

        ranking = PlayerRanking()
        ranking.player = player
        ranking.week = week
        ranking.year = year
        ranking.rank = rank
        ranking.wins = wins
        ranking.losses = losses
        ranking.points = points
        ranking.tournaments = tournaments
        ranking.prizemoney = money

        db.add(ranking)
        db.commit()

        print "> stored rank", year, ":", week


if __name__ == "__main__":
    pages = range(1,5) # only top 200

    if(len(sys.argv) > 1):
        years = [int(sys.argv[1])]

    for year in years:
        for week in weeks:
            for page in pages:
                print "* ranking page", year, week, page
                make_scrape_page(year, week, page)
    
