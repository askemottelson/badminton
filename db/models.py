from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, relation, backref, column_property

from sqlalchemy_views import CreateView
from sqlalchemy.types import Date

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.types import TIMESTAMP


Base = declarative_base()

class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    
    name = Column(String(1000))
    country = Column(String(100))
    gender = Column(String(100))
    birthyear = Column(Integer)
    birthmonth = Column(Integer)
    birthday = Column(Integer)
    handedness = Column(String(100))
    playertype = Column(String(100))

    url = Column(String(1000), unique=True)

    rankings = relationship("PlayerRanking")

    def birth(self):
        return str(self.birthday) + "/" + str(self.birthmonth) + "/" + str(self.birthyear)

    def get_birthyear(self):
        if self.birthyear is None:
            return 0
        return self.birthyear

    def get_birthmonth(self):
        if self.birthmonth is None:
            return 0
        return self.birthmonth

    def get_birthday(self):
        if self.birthday is None:
            return 0
        return self.birthday
        

class PlayerRanking(Base):
    __tablename__ = "playerrank"
    id = Column(Integer, primary_key=True)

    player_id = Column('Player', Integer, ForeignKey(Player.id))
    player = relationship("Player", foreign_keys=[player_id])

    week = Column(Integer)
    year = Column(Integer)
    rank = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    points = Column(Integer)
    tournaments = Column(Integer)
    prizemoney = Column(Float)

class Tournament(Base):
    __tablename__ = "tournament"
    id = Column(Integer, primary_key=True)

    week = Column(Integer)
    year = Column(Integer)
    start_date = Column(Integer)
    end_date = Column(Integer)
    name = Column(String)
    country = Column(String)
    prizemoney = Column(Integer)
    category = Column(String)
    city = Column(String)
    url = Column(String)

    matches = relationship("Match")


    def player_placement(self, player):
        matches = [m for m in self.matches if m.player1 == player or m.player2 == player]
        very_last_round = sorted(self.matches, key = lambda x: x.round_no, reverse = True)[0]

        if len(matches) == 0:
            return vrery_last_round.round_no

        last_round_reached = sorted(matches, key = lambda x: x.round_no, reverse = True)[0]
        
        return very_last_round.round_no - last_round_reached.round_no





# class TournamentResult(Base):
#     __tablename__ = "tournamentresult"
#     id = Column(Integer, primary_key=True)

#     tournament_id = Column('Tournament', Integer, ForeignKey(Tournament.id))
#     player_id = Column('Player', Integer, ForeignKey(Player.id))

#     position = Column(Integer)
#     prizemoney = Column(Float)
#     points = Column(Float)

#     def top3(self):
#         pass

class MatchStats(Base):
    __tablename__ = "matchstats"
    id = Column(Integer, primary_key=True)

    max_consecutive_points = Column(Integer)
    game_points = Column(Integer)
    rallies_played = Column(Integer)
    rallies_won  = Column(Integer)
    smash_winners   = Column(Integer)
    net_winners = Column(Integer)
    clear_winners   = Column(Integer)
    total_points_played  = Column(Integer)
    total_points_won = Column(Integer)


class Set(Base):
    __tablename__ = "set"
    id = Column(Integer, primary_key=True)

    match_id = Column(Integer, ForeignKey('match.id'))
    match = relationship("Match", foreign_keys=[match_id])

    index = Column(Integer)
    score_1 = Column(Integer)
    score_2 = Column(Integer)



class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True)

    tournament_id = Column('Tournament', Integer, ForeignKey(Tournament.id))
    tournament = relationship("Tournament", foreign_keys=[tournament_id])

    player1_id = Column(Integer, ForeignKey('player.id'), nullable=False)
    player2_id = Column(Integer, ForeignKey('player.id'), nullable=False)
    
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])

    stat1_id = Column(Integer, ForeignKey('matchstats.id'), nullable=False)
    stat2_id = Column(Integer, ForeignKey('matchstats.id'), nullable=False)

    stat1 = relationship("MatchStats", foreign_keys=[stat1_id])
    stat2 = relationship("MatchStats", foreign_keys=[stat2_id])

    round_no = Column(Integer)
    duration = Column(Integer)

    sets = relationship("Set")

    def year(self):
        return self.tournament.year

    def week(self):
        return self.tournament.week

    def did_win(self, player):
        return self.winner() == player

    def winner(self):
        return self.player1

    def other_player(self, player):
        if player == self.player1:
            return self.player2
        else:
            return self.player1




