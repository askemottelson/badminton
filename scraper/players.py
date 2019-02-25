import requests
from lxml import html
from bs4 import BeautifulSoup
import requests

from db.db_handler import db
from db.models import Player, PlayerRanking

from methods import make_player

years = range(2010,2019)
weeks = range(1,53)
players = db.query(Player).all()

player_urls = set([p.url for p in players])


def make_url(page):
    page = str(page)
    return "http://bwfbadminton.com/players/?char=all&country=&page_size=1000&page_no="+page



def make_scrape_page(page):
    url = make_url(page)
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    players = soup.findAll("div", {"class":"player"})

    for player_soup in players:
        player_url = player_soup.findChildren()[1].attrs['href']

        if player_url in player_urls:
            continue

        make_player(player_url)

        player_urls.add(player_url)



if __name__ == "__main__":
    pages = 21

    for page in range(pages):
        make_scrape_page(page)
    


