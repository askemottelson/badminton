from db.db_handler import db
from db.models import *

from sqlalchemy import or_

# # remove too new rankings

# year = 2018
# max_week = 33

# db.query(
#     PlayerRanking
# ).filter(PlayerRanking.week > max_week, PlayerRanking.year == year).delete()

# db.commit()

# remove players who are never ranked
# players = db.query(Player).all()

# for player in players:
#   rankings = player.rankings

#   if(len(rankings) == 0):
#       db.query(Player).filter(Player.id == player.id).delete()

# db.commit()


# db.query(Tournament).delete()
# db.query(Match).delete()
# db.query(MatchStats).delete()
# db.query(Set).delete()


# db.commit()

def get_matches1(player):
    return db.query(Match).filter(Match.player1 == player).all()
def get_matches2(player):
    return db.query(Match).filter(Match.player2 == player).all()

def get_matches(player):
    return db.query(Match).filter(or_(Match.player1 == player, Match.player2 == player)).all()


# players = db.query(Player).all()

# for i,player in enumerate(players):
#   matches = get_matches(player)
#   if len(matches) <= 1:
#       db.delete(player)
#   print i, "/", len(players)

# db.commit()


counter = 0
matches = db.query(Match).all()
for m in matches:
    if m.player1 is None or m.player2 is None:
        counter += 1
        db.delete(m)
        print counter, "/ 2386"

db.commit()



# res = {}

# for player in players:
#   if not player.name in res:
#       res[player.name] = []

#   res[player.name].append(player)

# keys = res.keys()
# counter = 0
# for key in keys:
#   counter += 1
#   siblings = res[key]
#   if len(siblings) > 1:
#       real = siblings[0] # default
#       print counter, "/", len(keys)
#       for sib in siblings:
#           if sib.url:
#               real = sib
#               break
#       # move all goods to real
#       for sib in siblings:
#           if sib is real:
#               continue

#           for rank in sib.rankings:
#               real.rankings.append(rank)
#           matches1 = get_matches1(sib)
#           matches2 = get_matches2(sib)

#           for m in matches1:
#               m.player1 = real

#           for m in matches2:
#               m.player2 = real

#           db.delete(sib)

# db.commit()


