from db.db_handler import db
from db.models import *
from sqlalchemy import or_, and_
import numpy as np
from scipy import stats
import datetime
from model.help import removed_keys
import datetime

MAX_RANKING = 400
now = datetime.datetime.now()
thisyear = now.year
thisweek = now.isocalendar()[1]

class NoMatches(Exception):
    pass


class PlayerRepresentation():

    def __init__(self, player, match):
        self.player = player

        # only rankings from before this match
        filtered_rankings = []
        for ranking in player.rankings:
            if ranking.year < match.tournament.year or (ranking.year == match.tournament.year and ranking.week < match.tournament.week):
                filtered_rankings.append(ranking)
        player.rankings = filtered_rankings


        self.birthyear = player.get_birthyear()
        self.birthmonth = player.get_birthmonth()
        self.birthday = player.get_birthday()

        # most recent ranking
        self.ranking = self.make_ranking(player)

        # ranking change in this year, last year
        self.delta_ranking0 = self.make_delta_ranking(player, 0)
        self.delta_ranking1 = self.make_delta_ranking(player, 1)

        try:
            self.season = self.good_season(player, match)
        except:
            self.season = [.0, .0]

        try:
            self.shape = self.good_year(player, match)
        except:
            self.shape = [.0, .0]

        if player.country is None:
            player.country = ""

        self.home_advantage = int(match.tournament.country.lower() == player.country.lower())


    def __str__(self):
        return str(self.__dict__)

    def recent_ranking(self, player):
        return sorted(player.rankings, key = lambda x: (x.year, x.week), reverse = True)[0]


    def make_ranking(self, player):
        try:
            return self.recent_ranking(player).rank
        except IndexError:
            # never ranked
            return MAX_RANKING

    def make_delta_ranking(self, player, dY):
        try:
            recent = self.recent_ranking(player)
        except IndexError:
            # was never ranked
            return [0,0,0,0,0,0]

        try:
            old_ranks = [r for r in player.rankings if r.year <= recent.year - dY]
            old_rank = sorted(old_ranks, key = lambda x: (x.year, x.week), reverse = True)[0]
        except IndexError:
            # player wasn't active back then
            # find oldest rank
            old_rank = sorted(player.rankings, key = lambda x: (x.year, x.week), reverse = False)[0]

        row = [
            (old_rank.rank - recent.rank),
            (old_rank.wins - recent.wins),
            (old_rank.losses - recent.losses),
            (old_rank.points - recent.points),
            (old_rank.tournaments - recent.tournaments),
            (old_rank.prizemoney - recent.prizemoney)
        ]

        return row

    def good_season(self, player, match):
        week = match.tournament.week
        matches = get_matches(player, match)
        tournaments = get_tournaments(player, match)

        matches_won = [m.did_win(player) for m in matches]
        tournament_placements = [t.player_placement(player) for t in tournaments]

        avg_wins = sum(matches_won) / float(len(matches))
        avg_tournament_placement = sum(tournament_placements) / float(len(tournaments))

        season = week / 13
        season_matches = [m for m in matches if (m.tournament.week / 13) == season]
        season_tournaments = [t for t in tournaments if (t.week / 13) == season]

        season_matches_won = [m.did_win(player) for m in season_matches]
        season_tournament_placements = [t.player_placement(player) for t in season_tournaments]

        season_avg_wins = sum(season_matches_won) / float(len(season_matches))
        season_avg_tournament_placement = sum(season_tournament_placements) / float(len(season_tournaments))

        return [
            avg_wins - season_avg_wins,
            avg_tournament_placement - season_avg_tournament_placement
        ]

    def good_year(self, player, match):
        week = match.tournament.week
        matches = get_matches(player, match)
        tournaments = get_tournaments(player, match)

        matches_won = [m.did_win(player) for m in matches]
        tournament_placements = [t.player_placement(player) for t in tournaments]

        avg_wins = sum(matches_won) / float(len(matches))
        avg_tournament_placement = sum(tournament_placements) / float(len(tournaments))

        year_matches = [m for m in matches if m.tournament.year == match.year()]
        year_tournaments = [t for t in tournaments  if t.year == match.year()]

        year_matches_won = [m.did_win(player) for m in year_matches]
        year_tournament_placements = [t.player_placement(player) for t in year_tournaments]

        year_avg_wins = sum(year_matches_won) / float(len(year_matches))
        year_avg_tournament_placement = sum(year_tournament_placements) / float(len(year_tournaments))

        return [
            avg_wins - year_avg_wins,
            avg_tournament_placement - year_avg_tournament_placement
        ]


def placement(matches):
    tot = {}
    for m in matches:
        if not m.tournament in tot:
            tot[m.tournament] = []
        tot[m.tournament].append(m.round_no)

    ds = []
    for tournament in tot.keys():
        ds.append(max(tot[tournament]))
    
    return np.std(ds), np.mean(ds), max(ds)



cats = []
def get_country_cat(player):
    global cats

    if player.country not in cats:
        cats.append(player.country)

    return cats.index(player.country)

def country(player, matches, country):
    matches = [m for m in matches if m.tournament.country == country]
    won = 0
    for m in matches:
        if(m.did_win(player)):
            won += 1
    try:
        return won/float(len(matches))
    except ZeroDivisionError:
        return 0


def get_matches(player, match):
    matches = db.query(Match).filter(
    	or_(Match.player1 == player, Match.player2 == player)
    ).all()

    # get matches from previous year, or this year and previous week ...
    # to not influence modelling using future data
    return [m for m in matches if m.year() < match.year() or (m.year() == match.year() and m.week() < match.week())]

def get_tournaments(player, match):
    return set(
        [m.tournament for m in get_matches(player, match)]
    )

def get_player_representation(player, match):
    rep = PlayerRepresentation(player, match)

    return rep

def get_vector(rep):
    return np.array([rep[key] for key in sorted(rep.keys()) if key not in removed_keys])

def busy(player, match, matches):
    matches = sorted(matches, key = lambda x: (x.year(), x.week()), reverse = True)
    maxyear = max([m.tournament.year for m in matches])

    matches = [m for m in matches if m.tournament.year == maxyear]

    this_week = len([m for m in matches if m.tournament.week == thisweek])
    two_weeks = len([m for m in matches if thisweek - m.tournament.week <= 1])
    five_weeks = len([m for m in matches if thisweek - m.tournament.week <= 5])

    return thisweek, two_weeks, five_weeks

def streak(player, match, matches=None):
    if matches is None:
        matches = get_matches(player, match)

    matches = sorted(matches, key = lambda x: (x.year(), x.week()), reverse = True)

    count = 0
    for m in matches:
        if m.did_win(player):
            count += 1
        else:
            break

    # won last match, streak
    return matches[0].did_win(player), count

size0 = None
def get_pvp_representation(p1model, p2model, match):
    global size0

    ### FIRST THE FACTUAL STUFF
    d1 = p1model.__dict__
    d2 = p2model.__dict__

    keys = d1.keys()

    res = {}

    for key in keys:
        if key in ["player","hand","year"]:
            continue

        var1 = d1[key]
        var2 = d2[key]

        if var1 is None:
            var1 = 0
        if var2 is None:
            var2 = 0

        if type(var1) is not type(var2):
            print key
            print type(var1), var1
            print type(var2), var2
            raise Exception("type mismatch!")

        if isinstance(var1, list):
            for i,_ in enumerate(var1):
                res[key + "_" + str(i)] = var1[i] - var2[i]
                # res[key + "1_"] = var1[i]
                # res[key + "2_"] = var2[i]
        else:
            res[key] = var1 - var2
            # res[key + "1_"] = var1
            # res[key + "2_"] = var2

    ### HEADS UP STUFF
    p1 = p1model.player
    p2 = p2model.player

    matches = db.query(Match).filter(
        or_(
            Match.player1 == p1, Match.player1 == p2
        ),
        or_(
            Match.player2 == p1, Match.player2 == p2
        )
    ).all()

    matches = [m for m in matches if m.year() < match.year() or (m.year() == match.year() and m.week() < match.week())]

    wins = [0,0]
    losses = [0,0]

    max_consecutive_points = [[],[]]
    game_points = [[],[]]
    rallies = [[],[]]

    smash_winners   = [[],[]]
    net_winners = [[],[]]
    clear_winners   = [[],[]]
    total_points = [[],[]]

    for match in matches:
        p1_m = match.player1
        p2_m = match.player2

        id1 = -1
        id2 = -1
        # check order
        if p1_m == p1 and p2_m == p2:
            id1 = 0
            id2 = 1
        else:
            id1 = 1
            id2 = 0

        stat1 = match.stat1
        stat2 = match.stat2

        # player1 is always match winner
        wins[id1] += 1
        losses[id2] += 1

        if stat1.rallies_played == 0 or stat2.rallies_played == 0:
            # no further stats
            continue

        if stat1.total_points_played == 0 or stat2.total_points_played == 0:
            # no further stats
            continue

        max_consecutive_points[id1].append(stat1.max_consecutive_points)
        max_consecutive_points[id2].append(stat2.max_consecutive_points)

        game_points[id1].append(stat1.game_points / float(len(matches)))
        game_points[id2].append(stat2.game_points / float(len(matches)))

        rallies[id1].append(stat1.rallies_won / float(stat1.rallies_played))
        rallies[id2].append(stat2.rallies_won / float(stat2.rallies_played))

        smash_winners[id1].append(stat1.smash_winners / float(stat1.rallies_played))
        smash_winners[id2].append(stat2.smash_winners / float(stat2.rallies_played))

        net_winners[id1].append(stat1.net_winners / float(stat1.rallies_played))
        net_winners[id2].append(stat2.net_winners / float(stat2.rallies_played))

        clear_winners[id1].append(stat1.clear_winners / float(stat1.rallies_played))
        clear_winners[id2].append(stat2.clear_winners / float(stat2.rallies_played))

        total_points[id1].append(stat1.total_points_won / float(stat1.total_points_played))
        total_points[id2].append(stat2.total_points_won / float(stat2.total_points_played))

    res["heads_wins"] = wins[0] - wins[1]
    # res["heads_wins1_"] = wins[0]
    # res["heads_wins2_"] = wins[1]

    d = float(sum(wins))
    if d == 0:
        res["heads_pct_wins"] = 0.0
        # res["heads_pct_wins1_"] = 0.0
        # res["heads_pct_wins2_"] = 0.0
    else:   
        res["heads_pct_wins"] = (wins[0]/d) - (wins[1]/d)
        # res["heads_pct_wins1_"] = wins[0]/d
        # res["heads_pct_wins2_"] = wins[1]/d

    
    def feature_pack(name, data):
        if len(data[0]) == 0 or len(data[1]) == 0:
            res["heads_"+name+"_mean"] = 0
            res["heads_"+name+"_max"] = 0
            res["heads_"+name+"_min"] = 0
            res["heads_"+name+"_SD"] = 0
            # res["heads_"+name+"_mean1_"] = 0
            # res["heads_"+name+"_max1_"] = 0
            # res["heads_"+name+"_min1_"] = 0
            # res["heads_"+name+"_SD1_"] = 0
            # res["heads_"+name+"_mean2_"] = 0
            # res["heads_"+name+"_max2_"] = 0
            # res["heads_"+name+"_min2_"] = 0
            # res["heads_"+name+"_SD2_"] = 0
            return

        res["heads_"+name+"_mean"] = np.mean(data[0]) - np.mean(data[1])
        res["heads_"+name+"_max"] = np.max(data[0]) - np.max(data[1])
        res["heads_"+name+"_min"] = np.min(data[0]) - np.min(data[1])
        res["heads_"+name+"_SD"] = np.std(data[0]) - np.std(data[1])

        # res["heads_"+name+"_mean1_"] = np.mean(data[0]) 
        # res["heads_"+name+"_max1_"] = np.max(data[0])
        # res["heads_"+name+"_min1_"] = np.min(data[0])
        # res["heads_"+name+"_SD1_"] = np.std(data[0])

        # res["heads_"+name+"_mean2_"] = np.mean(data[1]) 
        # res["heads_"+name+"_max2_"] = np.max(data[1])
        # res["heads_"+name+"_min2_"] = np.min(data[1])
        # res["heads_"+name+"_SD2_"] = np.std(data[1])

    feature_pack("max_consecutive_points",max_consecutive_points)
    feature_pack("game_points",game_points)
    feature_pack("rallies",rallies)
    feature_pack("smash_winners",smash_winners)
    feature_pack("net_winners",net_winners)
    feature_pack("clear_winners",clear_winners)
    feature_pack("total_points",total_points)

    # how well agains the other's type
    p1matches = get_matches(p1, match)
    p2matches = get_matches(p2, match)

    if len(p1matches) == 0 or len(p2matches) == 0:
        raise NoMatches()

    p1_one_year_matches = [m for m in p1matches if m.tournament.year == match.year()]
    p2_one_year_matches = [m for m in p2matches if m.tournament.year == match.year()]

    res["number_matches_year"] = len(p1_one_year_matches) - len(p2_one_year_matches)
    res["number_matches_years"] = len(p1_one_year_matches)/float(match.year()) - len(p2_one_year_matches)/float(match.year())

    # res["number_matches_year1_"] = len(p1_one_year_matches)
    # res["number_matches_years1_"] = len(p1_one_year_matches)/float(match.year())
    # res["number_matches_year2_"] = len(p2_one_year_matches)
    # res["number_matches_years2_"] = len(p2_one_year_matches)/float(match.year())

    # ## type that wins the long matches
    # # linear regression of no_sets vs winning
    # x1, y1 = [len(m.sets) for m in p1matches], [int(m.did_win(p1)) for m in p1matches]
    # x2, y2 = [len(m.sets) for m in p2matches], [int(m.did_win(p2)) for m in p2matches]

    # if len(x1) < 3:
    #     x1 = [0,0]
    #     y1 = [0,0]
    # if len(x2) < 3:
    #     x2 = [0,0]
    #     y2 = [0,0]

    # c0_1, c1_1 = stats.pearsonr(x1,y1)
    # c0_2, c1_2 = stats.pearsonr(x2,y2)

    # res["lr_0"] = c0_1 - c0_2
    # res["lr_1"] = c1_1 - c1_2

    
    hand_experience1 = []
    hand_experience2 = []

    country_experience1 = []
    country_experience2 = []

    all_experience1 = []
    all_experience2 = []

    all_ages1 = []
    all_ages2 = []

    win_ages1 = []
    win_ages2 = []

    # filter for handedness
    p1matches_w_hand = [m for m in p1matches if m.player1.handedness in ["left","right"] and m.player2.handedness in ["left","right"]]
    p2matches_w_hand  = [m for m in p2matches if m.player1.handedness in ["left","right"] and m.player2.handedness in ["left","right"]]
    # filter for handedness
    p1matches_w_year = [m for m in p1matches if m.player1.get_birthyear() > 0 and m.player2.get_birthyear() > 0]
    p2matches_w_year = [m for m in p2matches if m.player1.get_birthyear() > 0 and m.player2.get_birthyear() > 0]

    # all data
    for match in p1matches:
        if match.did_win(p1):
            all_experience1.append(1)
        else:
            all_experience1.append(0)

        if match.other_player(p1).country == p2.country and not match.other_player(p1) == p2:
            if match.did_win(p1):
                country_experience1.append(1)
            else:
                country_experience1.append(0)
    # ---
    for match in p2matches:
        if match.did_win(p2):
            all_experience2.append(1)
        else:
            all_experience2.append(0)

        if match.other_player(p2).country == p1.country and not match.other_player(p2) == p1:
            if match.did_win(p2):
                country_experience2.append(1)
            else:
                country_experience2.append(0)

    # hand data
    for match in p1matches_w_hand:
        if match.did_win(p1):
            all_experience1.append(1)
        else:
            all_experience1.append(0)

        # hand match with other person
        if match.other_player(p1).handedness == p2.handedness and not match.other_player(p1) == p2:
            if match.did_win(p1):   
                hand_experience1.append(1)
            else:
                hand_experience1.append(0)
    # ----
    for match in p2matches_w_hand:

        if match.did_win(p2):
            all_experience2.append(1)
        else:
            all_experience2.append(0)

        # hand match with other person
        if match.other_player(p2).handedness == p1.handedness and not match.other_player(p2) == p1:
            if match.did_win(p2):
                hand_experience2.append(1)
            else:
                hand_experience2.append(0)

    for match in p1matches_w_year:
        if not match.other_player(p1) == p2:
            all_ages1.append(match.other_player(p1).birthyear)
        
        if match.did_win(p1):
            win_ages1.append(match.other_player(p1).birthyear)

    for match in p2matches_w_year:
        if not match.other_player(p2) == p1:
            all_ages2.append(match.other_player(p2).birthyear)

        if match.did_win(p2):
            all_experience2.append(1)
            win_ages2.append(match.other_player(p2).birthyear)

    try:
        # force error when no birthday
        _ = 1/p1.birthyear
        _ = 1/p2.birthyear

        all_ages1 = [x-p2.birthyear for x in all_ages1 if x > 0]
        all_ages2 = [x-p1.birthyear for x in all_ages2 if x > 0]
        win_ages1 = [x-p2.birthyear for x in win_ages1 if x > 0]
        win_ages2 = [x-p1.birthyear for x in win_ages2 if x > 0]

        avg_age_win1 = np.mean(win_ages1)
        avg_age_win2 = np.mean(win_ages2)

        avg_age1 = np.mean(all_ages1)
        avg_age2 = np.mean(all_ages2)

        p1_age_rel = avg_age_win1 - avg_age1
        p2_age_rel = avg_age_win2 - avg_age2
    except:
        # no birthyear
        p1_age_rel = 0
        p2_age_rel = 0

        win_ages1 = []
        win_ages2 = []

    # feature_pack("all_hand_relatives", [all_experience1, all_experience2])
    feature_pack("hand_relatives", [hand_experience1, hand_experience2])
    feature_pack("age_relatives", [win_ages1, win_ages2])

    p1_avg = np.mean(all_experience1)
    p2_avg = np.mean(all_experience2)

    p1_avg_p2_hand = np.mean(hand_experience1)
    p2_avg_p1_hand = np.mean(hand_experience2)
    p1_avg_p2_country = np.mean(country_experience1)
    p2_avg_p1_country = np.mean(country_experience2)

    p1_rel = p1_avg - p1_avg_p2_hand
    p2_rel = p2_avg - p2_avg_p1_hand

    p1_rel_country = p1_avg - p1_avg_p2_country
    p2_rel_country = p2_avg - p2_avg_p1_country

    res["hand_relative"] = p1_rel - p2_rel
    res["country_relative"] = p1_rel_country - p2_rel_country
    res["age_relative"] = p1_age_rel - p2_age_rel
    # res["hand_relative1_"] = p1_rel
    # res["country_relative1_"] = p1_rel_country
    # res["age_relative1_"] = p1_age_rel
    # res["hand_relative2_"] = p2_rel
    # res["country_relative2_"] = p2_rel_country
    # res["age_relative2_"] = p2_age_rel
    
    # streak
    wonlast_p1, streak_p1 = streak(p1, match, p1matches)
    wonlast_p2, streak_p2 = streak(p2, match, p2matches)

    res["streak"] = streak_p1 - streak_p2
    res["wonlast_p1"] = int(wonlast_p1)
    res["wonlast_p2"] = int(wonlast_p2)
    res["country_p1"] = get_country_cat(p1)
    res["country_p2"] = get_country_cat(p2)

    if p1.get_birthyear() == 0 or p2.get_birthyear() == 0:
        res["age_diff"] = 0
    else:
        res["age_diff"] = p1.get_birthyear() - p2.get_birthyear()

    res["year"] = match.year()
    res["since"] = thisyear - match.year()
    res["week"] = match.week()
    res["round"] = match.round_no
    res["moneyprize"] = match.tournament.prizemoney

    # avg placement
    p1_place, p2_place = placement(p1matches), placement(p2matches)
    c = 0
    for f1,f2 in zip(p1_place, p2_place):
        res["place_"+str(c)] = f1 - f2
        c += 1

    # good in this country
    p1_country, p2_country = country(p1, p1matches, match.tournament.country), country(p2, p2matches, match.tournament.country)

    res["country_success"] = p1_country - p2_country

    c = 0
    for f1,f2 in zip(busy(p1, match, p1matches), busy(p1, match, p1matches)):
        res["busy_"+str(c)] = f1-f2
        c += 1

    ## fix wrong np's
    for key in res.keys():
        if np.isnan(res[key]) or res[key] is None:
            res[key] = 0

    if size0 is None:
        size0 = len(res.keys())
    else:
        assert len(res.keys()) == size0

    return res