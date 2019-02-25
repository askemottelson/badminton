import sys
from scraper.methods import get_player_name
from methods import get_player_representation, get_pvp_representation
from db.models import Tournament
import pprint

p1_name = "Viktor Axelsen".lower()
p2_name = "Lin Dan".lower()

tournament = Tournament()
tournament.week = 1
tournament.country = "den"


p1 = get_player_name(p1_name)
p2 = get_player_name(p2_name)

p1_model = get_player_representation(p1, tournament)
p2_model = get_player_representation(p2, tournament)

rep = get_pvp_representation(p1_model, p2_model)

pp = pprint.PrettyPrinter()
pp.pprint(rep)
