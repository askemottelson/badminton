from db.db_handler import db
from db.models import *
import datetime

now = datetime.datetime.now()
thisyear = now.year
thisweek = now.isocalendar()[1]

# remove future rankings
rankings = db.query(PlayerRanking).filter(PlayerRanking.year == thisyear, PlayerRanking.week > thisweek).all()
[db.delete(r) for r in rankings]
print "removed", len(rankings), "rankings"
db.commit()




