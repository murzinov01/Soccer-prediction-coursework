import csv
import difflib



def similarity(s1: str, s2: str) -> float:
  normalized1 = s1.lower()
  normalized2 = s2.lower()
  matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
  return matcher.ratio()


class MatchesDataAnalytics:
    ALL_MATCHES = list()
    ALL_SEASON_TEAMS = list()
    RECENT_MATCHES = list()
    LAST_SEASON_MATCHES = list()
    league_name = ''
    MIN_PLAYER_RATING = 3.0

    def __init__(self, league_name):
        self.league_name = league_name
        self.read_matches()

    def read_matches(self) -> None:
        # *** READ CSV FILE ***
        self.ALL_MATCHES = list()
        with open(self.league_name + " _results_data.csv", 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file, delimiter=',')
            for match in reader:
                self.ALL_MATCHES.append(match)

    def recent_matches(self, match_id: int) -> None:
        self.RECENT_MATCHES = self.ALL_MATCHES[match_id+1:]

    def season_matches(self, match_id: int, use_prev_season=False):
        # *** FIND CURRENT SEASON MATCHES ***
        self.LAST_SEASON_MATCHES = list()
        self.recent_matches(match_id)
        end_season = self.ALL_MATCHES[match_id]["Season"]
        year2 = int(end_season[:end_season.find("/")])
        year1 = year2 - 1
        end_season = str(year1) + "/" + str(year2)

        if use_prev_season:
            year2 = int(end_season[:end_season.find("/")])
            year1 = year2 - 1
            end_season = str(year1) + "/" + str(year2)

        for match in self.RECENT_MATCHES:
            # search for season end
            if match["Season"] == end_season:
                return
            self.LAST_SEASON_MATCHES.append(match)

    def find_match_id(self, date: str, team_home: str, team_away="", season=""):
        for index in range(0, len(self.ALL_MATCHES)):
            match = self.ALL_MATCHES[index]
            if match["Date"] == date and match["TeamHome"] == team_home:
                return index

    def number_of_tour(self, match_id: int) -> dict:
        tour = {
            "TeamHome": 0,
            "TeamAway": 0
        }
        my_match = self.ALL_MATCHES[match_id]

        self.season_matches(match_id)
        for match in self.LAST_SEASON_MATCHES:
            if my_match["TeamHome"] in (match["TeamHome"], match["TeamAway"]):
                tour["TeamHome"] += 1
            if my_match["TeamAway"] in (match["TeamHome"], match["TeamAway"]):
                tour["TeamAway"] += 1

        return tour

    @staticmethod
    def calculate_table_stats(table: dict, team_name: str, team_home: bool, match) -> None:

        if team_home:
            team_status1 = "Home"
            team_status2 = "Away"
        else:
            team_status2 = "Home"
            team_status1 = "Away"

        # calculate
        table[team_name]["P"] += 1

        if int(match["ResultTeam" + team_status1]) > int(match["ResultTeam" + team_status2]):
            table[team_name]["W"] += 1
        elif int(match["ResultTeam" + team_status1]) == int(match["ResultTeam" + team_status2]):
            table[team_name]["D"] += 1
        else:
            table[team_name]["L"] += 1

        table[team_name]["GF"] += int(match["ResultTeam" + team_status1])
        table[team_name]["GA"] += int(match["ResultTeam" + team_status2])
        table[team_name]["GD"] = table[team_name]["GF"] - table[team_name]["GA"]
        table[team_name]["Points"] = 3 * table[team_name]["W"] + table[team_name]["D"]

    @staticmethod
    def null_stats(min_stats=False) -> dict:
        return {
            "RatingTeam": 0.0 if not min_stats else 5.0,
            "TotalShots": 0.0 if not min_stats else 5.0,
            "Possession": 0.0 if not min_stats else 25.0,
            "PassAccuracy": 0.0 if not min_stats else 50.0,
            "Dribbles": 0.0 if not min_stats else 0.0,
            "AerialsWon": 0.0 if not min_stats else 3.0,
            "Tackles": 0.0 if not min_stats else 3.0,
            "Corners": 0.0 if not min_stats else 0.0,
            "Dispossessed": 0.0 if not min_stats else 10.0,
            "YellowCard": 0,
            "RedCard": 0,
            "Period": 1
        }

    @staticmethod
    def calculate_stats(match: dict, team_status: str, set_null=False) -> dict:
        match_stats = {
            "RatingTeam": float(match["RatingTeam" + team_status]),
            "TotalShots": float(match["TotalShots" + team_status]),
            "Possession": float(match["Possession" + team_status]),
            "PassAccuracy": float(match["PassAccuracy" + team_status]),
            "Dribbles": float(match["Dribbles" + team_status]),
            "AerialsWon": float(match["AerialsWon" + team_status]),
            "Tackles": float(match["Tackles" + team_status]),
            "Corners": float(match["Corners" + team_status]),
            "Dispossessed": float(match["Dispossessed" + team_status]),
            "YellowCard": int(match["YellowCard" + team_status]),
            "RedCard": int(match["RedCard" + team_status]),
            "Period": 1
        }
        return match_stats

    def calculate_stats_average(self, stats: dict):
        # check if empty
        if not stats:
            return
        if stats["RatingTeam"] == 0:
            min_stats = self.null_stats(min_stats=True)
            for key in stats.keys():
                stats[key] = min_stats[key]
            return
        period = stats["Period"]
        for key in stats.keys():
            if key in ("Period", "RedCard", "YellowCard"):
                continue
            value = stats[key]/period
            stats[key] = float(format(value, '.3f'))

    def find_all_teams(self, match_id: int) -> None:
        self.ALL_SEASON_TEAMS = list()
        cur_season = self.ALL_MATCHES[match_id]["Season"]
        start_season = match_id
        while self.ALL_MATCHES[start_season]["Season"] == cur_season and start_season != 0:
            start_season -= 1
        if start_season != 0:
            start_season += 1
        while self.ALL_MATCHES[start_season]["Season"] == cur_season:
            TeamHome = self.ALL_MATCHES[start_season]["TeamHome"]
            TeamAway = self.ALL_MATCHES[start_season]["TeamAway"]
            if TeamHome not in self.ALL_SEASON_TEAMS:
                self.ALL_SEASON_TEAMS.append(TeamHome)
            if TeamAway not in self.ALL_SEASON_TEAMS:
                self.ALL_SEASON_TEAMS.append(TeamAway)
            start_season += 1
            if len(self.ALL_MATCHES) == start_season:
                break

    def create_actual_table(self, match_id: int, use_prev_season=False) -> dict:
        TABLE = dict()

        self.find_all_teams(match_id)
        # print(self.ALL_SEASON_TEAMS)
        for key in self.ALL_SEASON_TEAMS:
            TABLE[key] = {
                "Points": 0,
                'P': 0,
                'W': 0,
                'D': 0,
                'L': 0,
                'GF': 0,
                'GA': 0,
                'GD': 0,
                'Place': 0
            }

        self.season_matches(match_id, use_prev_season)

        # *** ANALYSE DATA ***
        for i in range(len(self.LAST_SEASON_MATCHES)):
            match = self.LAST_SEASON_MATCHES[i]
            team_home_name = match["TeamHome"]
            team_away_name = match["TeamAway"]

            # build table
            self.calculate_table_stats(TABLE, team_home_name, True, match)
            self.calculate_table_stats(TABLE, team_away_name, False, match)

        # sort table
        temp = list(TABLE.items())
        temp.sort(key=lambda value: value[1]["Points"])
        temp = temp[::-1]

        for i in range(len(temp)):
            TABLE[temp[i][0]]["Place"] = i+1

        return TABLE

    def summarise_statistic(self, match_id: int, use_prev_season=False, period=-1) -> dict():

        self.season_matches(match_id, use_prev_season)
        STATS = {
            "TeamHome": {
                "HomeStats": self.null_stats(),
                "AwayStats": self.null_stats()
            },
            "TeamAway": {
                "HomeStats": self.null_stats(),
                "AwayStats": self.null_stats()
            },
        }

        team_home_name = self.ALL_MATCHES[match_id]["TeamHome"]
        team_away_name = self.ALL_MATCHES[match_id]["TeamAway"]

        period_counter_home_home = 0
        period_counter_home_away = 0
        period_counter_away_home = 0
        period_counter_away_away = 0

        concrete_period = len(self.LAST_SEASON_MATCHES) if period == -1 else period

        # *** SUM ALL STATS ***
        for match in self.LAST_SEASON_MATCHES:
            # main condition
            if period_counter_home_home >= concrete_period and period_counter_away_home >= concrete_period \
                    and period_counter_home_away >= concrete_period and period_counter_away_away >= concrete_period:
                break

            if period_counter_home_home < concrete_period and match["TeamHome"] == team_home_name:
                # our first team stats in home games
                stats = self.calculate_stats(match, "Home")
                for key in stats.keys():
                    STATS["TeamHome"]["HomeStats"][key] = (0 if key not in STATS["TeamHome"]["HomeStats"].keys() else
                                                           STATS["TeamHome"]["HomeStats"][key]) + stats[key]
                period_counter_home_home += 1

            elif period_counter_home_away < concrete_period and match["TeamAway"] == team_home_name:
                # our first team stats in away games
                stats = self.calculate_stats(match, "Away")
                for key in stats.keys():
                    STATS["TeamHome"]["AwayStats"][key] = (0 if key not in STATS["TeamHome"]["AwayStats"].keys() else
                                                           STATS["TeamHome"]["AwayStats"][key]) + stats[key]
                period_counter_home_away += 1

            if period_counter_away_home < concrete_period and match["TeamHome"] == team_away_name:
                # our second team stats in home games
                # print(self.ALL_MATCHES.index(match))
                stats = self.calculate_stats(match, "Home")
                for key in stats.keys():
                    STATS["TeamAway"]["HomeStats"][key] = (0 if key not in STATS["TeamAway"]["HomeStats"].keys() else
                                                           STATS["TeamAway"]["HomeStats"][key]) + stats[key]
                period_counter_away_home += 1

            elif period_counter_away_away < concrete_period and match["TeamAway"] == team_away_name:
                # our second team stats in away games
                stats = self.calculate_stats(match, "Away")
                for key in stats.keys():
                    STATS["TeamAway"]["AwayStats"][key] = (0 if key not in STATS["TeamAway"]["AwayStats"].keys() else
                                                           STATS["TeamAway"]["AwayStats"][key]) + stats[key]
                period_counter_away_away += 1

        STATS["TeamHome"]["HomeStats"]["Period"] -= 1 if STATS["TeamHome"]["HomeStats"]["Period"] > 1 else 0
        STATS["TeamHome"]["AwayStats"]["Period"] -= 1 if STATS["TeamHome"]["AwayStats"]["Period"] > 1 else 0
        STATS["TeamAway"]["HomeStats"]["Period"] -= 1 if STATS["TeamAway"]["HomeStats"]["Period"] > 1 else 0
        STATS["TeamAway"]["AwayStats"]["Period"] -= 1 if STATS["TeamAway"]["AwayStats"]["Period"] > 1 else 0

        if match_id == 157:
            print(STATS)
            print (len(self.LAST_SEASON_MATCHES))
        # *** CALCULATE AVERAGE ***
        self.calculate_stats_average(STATS["TeamHome"]["HomeStats"])
        self.calculate_stats_average(STATS["TeamHome"]["AwayStats"])
        self.calculate_stats_average(STATS["TeamAway"]["HomeStats"])
        self.calculate_stats_average(STATS["TeamAway"]["AwayStats"])

        return STATS

    def calculate_goals_assists(self, match_id: int) -> dict:
        results = {
            "TeamHome": {
                "Goals": 0,
                "Assists": 0
            },
            "TeamAway": {
                "Goals": 0,
                "Assists": 0
            }
        }
        home_line_up = (self.ALL_MATCHES[match_id]["StartTeamHome"] + ", " + self.ALL_MATCHES[match_id]["SubstitutionHome"]).split(', ')
        away_line_up = (self.ALL_MATCHES[match_id]["StartTeamAway"] + ", " + self.ALL_MATCHES[match_id]["SubstitutionAway"]).split(', ')
        self.season_matches(match_id)

        for match in self.LAST_SEASON_MATCHES:
            goalee = (match["GoalsHome"] + ", " + match["GoalsAway"]).split(', ')
            assistant = (match["AssistsHome"] + ", " + match["AssistsAway"]).split(', ')
            # calculate goals
            for goal in goalee:
                if goal in home_line_up:
                    results["TeamHome"]["Goals"] += 1
                if goal in away_line_up:
                    results["TeamAway"]["Goals"] += 1

            # calculate assists
            for assist in assistant:
                if assist in home_line_up:
                    results["TeamHome"]["Assists"] += 1
                if assist in away_line_up:
                    results["TeamAway"]["Assists"] += 1

        return results

    def rating_help(self, target_player: str, line_up: dict, match_line_up: list, r_match_line_up: list, period=-1) -> None:
        index = line_up["Players"].index(target_player)
        if period != -1 and line_up["Games_num"][index] >= period:
            return
        if target_player in match_line_up:
            index_r = match_line_up.index(target_player)
            # print (target_player, r_match_line_up[index_r])
            line_up["Ratings"][index] += r_match_line_up[index_r] if r_match_line_up[index_r] != -1 else self.MIN_PLAYER_RATING
            line_up["Games_num"][index] += 1

    def calculate_players_rating(self, match_id: int, period=-1, use_prev_season=False) -> dict:
        self.season_matches(match_id, use_prev_season=use_prev_season)

        home_size = len(self.ALL_MATCHES[match_id]["SubstitutionHome"].split(', '))
        away_size = len(self.ALL_MATCHES[match_id]["SubstitutionAway"].split(', '))

        home_line_up = {
            "Players": self.ALL_MATCHES[match_id]["StartTeamHome"].split(', '),
            "Ratings": [0 for i in range(11)],
            "Games_num": [0 for i in range(11)]
        }
        away_line_up = {
            "Players": self.ALL_MATCHES[match_id]["StartTeamAway"].split(', '),
            "Ratings": [0 for i in range(11)],
            "Games_num": [0 for i in range(11)]
        }
        home_subs = {
            "Players": self.ALL_MATCHES[match_id]["SubstitutionHome"].split(', '),
            "Ratings": [0 for i in range(home_size)],
            "Games_num": [0 for i in range(home_size)]
        }
        away_subs = {
            "Players": self.ALL_MATCHES[match_id]["SubstitutionAway"].split(', '),
            "Ratings": [0 for i in range(away_size)],
            "Games_num": [0 for i in range(away_size)]
        }

        # get data
        # print("LSM: ",len(self.LAST_SEASON_MATCHES))
        # print(self.LAST_SEASON_MATCHES[len(self.LAST_SEASON_MATCHES) - 1])
        for match in self.LAST_SEASON_MATCHES:
            match_home_line_up = match["StartTeamHome"].split(', ')
            match_away_line_up = match["StartTeamAway"].split(', ')
            match_home_subs = match["SubstitutionHome"].split(', ')
            match_away_subs = match["SubstitutionAway"].split(', ')

            r_match_home_line_up = list(map(float, match["RatingStartTeamHome"].split(', ')))
            r_match_away_line_up = list(map(float, match["RatingStartTeamAway"].split(', ')))
            r_match_home_subs = list(map(float, match["RatingSubstitutionHome"].split(', ')))
            r_match_away_subs = list(map(float, match["RatingSubstitutionAway"].split(', ')))

            for line_up in (home_line_up, away_line_up, home_subs, away_subs):
                for target_player in line_up["Players"]:
                    self.rating_help(target_player, line_up, match_home_line_up, r_match_home_line_up, period)
                    self.rating_help(target_player, line_up, match_away_line_up, r_match_away_line_up, period)
                    self.rating_help(target_player, line_up, match_home_subs, r_match_home_subs, period)
                    self.rating_help(target_player, line_up, match_away_subs, r_match_away_subs, period)
        # print(home_line_up, away_line_up, home_subs, away_subs)
        # calculate average
        for line_up in (home_line_up, away_line_up, home_subs, away_subs):
            line_up["Games_num"] = list(map(lambda x: x if x else 1, line_up["Games_num"]))
            line_up["Ratings"] = [line_up["Ratings"][i] / line_up["Games_num"][i] for i in range(len(line_up["Ratings"]))]
            line_up["Ratings"] = list(map(lambda x: x if x > self.MIN_PLAYER_RATING else self.MIN_PLAYER_RATING, line_up["Ratings"]))
            # for player_i in range(len(line_up["Ratings"])):
            #     line_up["Ratings"][player_i] /= line_up["Games_num"][player_i]

        ratings = {
            "TeamHome": {
                "Start": sum(home_line_up["Ratings"]) / len(home_line_up["Ratings"]),
                "Subs": sum(home_subs["Ratings"]) / len(home_subs["Ratings"]),
                "StartGamePerPlayer": sum(home_line_up["Games_num"]) / len(home_line_up["Games_num"]),
                "SubsGamePerPlayer": sum(home_subs["Games_num"]) / len(home_subs["Games_num"])
            },
            "TeamAway": {
                "Start": sum(away_line_up["Ratings"]) / len(away_line_up["Ratings"]),
                "Subs": sum(away_subs["Ratings"]) / len(away_subs["Ratings"]),
                "StartGamePerPlayer": sum(away_line_up["Games_num"]) / len(away_line_up["Games_num"]),
                "SubsGamePerPlayer": sum(away_subs["Games_num"]) / len(away_subs["Games_num"])
            }
        }
        # print(ratings)
        return ratings

    def upcoming_match(self, match_id: int) -> dict:
        upcoming = {
            "TeamHome": {
                "TeamName": "",
                "MatchStatus": 0
            },
            "TeamAway": {
                "TeamName": "",
                "MatchStatus": 0
            }
        }

        team_home_f = False
        team_away_f = False

        cur_team_home = self.ALL_MATCHES[match_id]["TeamHome"]
        cur_team_away = self.ALL_MATCHES[match_id]["TeamAway"]

        cur_season = self.ALL_MATCHES[match_id]["Season"]

        for match in self.ALL_MATCHES[match_id - 1:: -1]:
            if (team_away_f and team_home_f) or cur_season != match["Season"]:
                break
            if match["TeamHome"] == cur_team_home and not team_home_f:
                upcoming["TeamHome"]["TeamName"] = match["TeamAway"]
                upcoming["TeamHome"]["MatchStatus"] = 1
                team_home_f = True
            if match["TeamAway"] == cur_team_home and not team_home_f:
                upcoming["TeamHome"]["TeamName"] = match["TeamHome"]
                upcoming["TeamHome"]["MatchStatus"] = 2
                team_home_f = True
            if match["TeamHome"] == cur_team_away and not team_away_f:
                upcoming["TeamAway"]["TeamName"] = match["TeamAway"]
                upcoming["TeamAway"]["MatchStatus"] = 1
                team_away_f = True
            if match["TeamAway"] == cur_team_away and not team_away_f:
                upcoming["TeamAway"]["TeamName"] = match["TeamHome"]
                upcoming["TeamAway"]["MatchStatus"] = 2
                team_away_f = True

        return upcoming

    def get_match_result(self, match_id: int) -> int:
        match = self.ALL_MATCHES[match_id]

        if match["ResultTeamHome"] > match["ResultTeamAway"]:
            return 1

        if match["ResultTeamHome"] < match["ResultTeamAway"]:
            return -1

        return 0

    def calculate_form(self, match_id: int, period=6) -> dict:
        form = {
            "TeamHome": 0,
            "TeamAway": 0
        }
        self.season_matches(match_id)

        team_home = self.ALL_MATCHES[match_id]["TeamHome"]
        team_away = self.ALL_MATCHES[match_id]["TeamAway"]

        counter_h = 0
        counter_a = 0

        for match in self.LAST_SEASON_MATCHES:

            if counter_h >= period and counter_a >= period:
                break

            if match["TeamHome"] == team_home and counter_h < period:
                result = self.get_match_result(self.ALL_MATCHES.index(match))
                form["TeamHome"] += 1 if not result else 3 * result
                counter_h += 1

            if match["TeamAway"] == team_home and counter_h < period:
                result = self.get_match_result(self.ALL_MATCHES.index(match))
                form["TeamHome"] += 1 if not result else -3 * result
                counter_h += 1

            if match["TeamHome"] == team_away and counter_a < period:
                result = self.get_match_result(self.ALL_MATCHES.index(match))
                form["TeamAway"] += 1 if not result else 3 * result
                counter_a += 1

            if match["TeamAway"] == team_away and counter_a < period:
                result = self.get_match_result(self.ALL_MATCHES.index(match))
                form["TeamAway"] += 1 if not result else -3 * result
                counter_a += 1

        form["TeamHome"] = round((form["TeamHome"] + 3 * period) / (period * 0.06), 2)
        form["TeamAway"] = round((form["TeamAway"] + 3 * period) / (period * 0.06), 2)

        return form


class DataPackager:

    MIN_GAMES = 3
    BETS = list()

    def __init__(self, league_name: str):
        self.league_name = league_name
        self.AL = MatchesDataAnalytics(self.league_name)
        self.ST = StringsTransfer()

    def read_bets(self, file_name):
        self.BETS = list()
        with open(file_name + '.csv', 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            for match in reader:
                self.BETS.append(match)

    def convert_match_data(self, match: dict, data: dict) -> dict:
        match_id = self.AL.ALL_MATCHES.index(match)

        data["BetHome"] = 0
        data["BetDraw"] = 0
        data["BetAway"] = 0

        match_string_name = [match["TeamHome"], match["TeamAway"]]
        match_string_result = match["ResultTeamHome"] + match["ResultTeamAway"]
        for match_bet in self.BETS:
            match_result = match_bet["ResultTeamHome"] + match_bet["ResultTeamAway"]
            if match_result != match_string_result:
                continue
            if abs(self.AL.ALL_MATCHES.index(match) - self.BETS.index(match_bet)) > 15:
                continue
            if similarity(match_string_name[0], match_bet["TeamHome"]) > 0.6 and \
                similarity(match_string_name[1], match_bet["TeamAway"]) > 0.6:
                data["BetHome"] = match_bet["Bet1"]
                data["BetDraw"] = match_bet["BetX"]
                data["BetAway"] = match_bet["Bet2"]
                break

        if data["BetHome"] == 0:
            return data

        data["Result"] = self.AL.get_match_result(match_id)
        data["Total2.5"] = 1 if int(match["ResultTeamHome"]) + int(match["ResultTeamAway"]) > 2.5 else 0
        data["Total1.5"] = 1 if int(match["ResultTeamHome"]) + int(match["ResultTeamAway"]) > 1.5 else 0
        data["League"] = self.ST.code_string("League", self.league_name)
        data["Time"] = self.ST.code_time(match["Time"])
        data["TeamHome"] = self.ST.code_string("Team", match["TeamHome"])
        data["TeamAway"] = self.ST.code_string("Team", match["TeamAway"])
        data["ManagerHome"] = self.ST.code_string("Manager", match["ManagerHome"])
        data["ManagerAway"] = self.ST.code_string("Manager", match["ManagerAway"])
        data["FormationHome"] = self.ST.code_string("Formation", match["FormationHome"])
        data["FormationAway"] = self.ST.code_string("Formation", match["FormationAway"])
        data["Stadium"] = self.ST.code_string("Stadium", match["Stadium"])
        data["Referee"] = self.ST.code_string("Referee", match["Referee"])

        d_var = self.AL.calculate_players_rating(match_id)
        data["RatingStartTeamHome"] = format(d_var["TeamHome"]["Start"], '.3f')
        data["RatingSubstitutionHome"] = format(d_var["TeamHome"]["Subs"], '.3f')
        data["RatingStartTeamAway"] = format(d_var["TeamAway"]["Start"], '.3f')
        data["RatingSubstitutionAway"] = format(d_var["TeamAway"]["Subs"], '.3f')

        data["GPP_StartHome"] = format(d_var["TeamHome"]["StartGamePerPlayer"], '.3f')
        data["GPP_StartAway"] = format(d_var["TeamAway"]["StartGamePerPlayer"], '.3f')
        data["GPP_SubsHome"] = format(d_var["TeamHome"]["SubsGamePerPlayer"], '.3f')
        data["GPP_SubsAway"] = format(d_var["TeamAway"]["SubsGamePerPlayer"], '.3f')

        d_var = self.AL.calculate_players_rating(match_id, 3)
        data["RatingStartTeamHome3"] = format(d_var["TeamHome"]["Start"], '.3f')
        data["RatingSubstitutionHome3"] = format(d_var["TeamHome"]["Subs"], '.3f')
        data["RatingStartTeamAway3"] = format(d_var["TeamAway"]["Start"], '.3f')
        data["RatingSubstitutionAway3"] = format(d_var["TeamAway"]["Subs"], '.3f')


        d_var = self.AL.calculate_goals_assists(match_id)
        data["GoalsTeamHome"] = d_var["TeamHome"]["Goals"]
        data["GoalsTeamAway"] = d_var["TeamAway"]["Goals"]
        data["AssistsTeamHome"] = d_var["TeamHome"]["Assists"]
        data["AssistsTeamAway"] = d_var["TeamAway"]["Assists"]

        d_var = self.AL.calculate_form(match_id, 3)
        data["FormTeamHome3"] = d_var["TeamHome"]
        data["FormTeamAway3"] = d_var["TeamAway"]
        d_var = self.AL.calculate_form(match_id, 6)
        data["FormTeamHome6"] = d_var["TeamHome"]
        data["FormTeamAway6"] = d_var["TeamAway"]

        endings = ["", "A", "3", "3A"]

        for end in endings:
            period = -1 if endings.index(end) < 2 else 3
            d_var = self.AL.summarise_statistic(match_id, use_prev_season=False if self.AL.number_of_tour(match_id)["TeamHome"] >= self.MIN_GAMES else True, period=period)
            for key in d_var["TeamHome"]["HomeStats"].keys():
                if key == "Period":
                    break
                # print(d_var["TeamHome"]["HomeStats"][key], type(d_var["TeamHome"]["HomeStats"][key]), d_var["TeamHome"]["AwayStats"][key], type(d_var["TeamHome"]["AwayStats"][key]))
                stats = d_var["TeamHome"]["HomeStats"][key] if endings.index(end) % 2 == 0 else \
                    (d_var["TeamHome"]["HomeStats"][key] + d_var["TeamHome"]["AwayStats"][key]) / 2
                data[key + "Home" + end] = format(stats, '.3f')

            d_var = self.AL.summarise_statistic(match_id, use_prev_season=False if self.AL.number_of_tour(match_id)["TeamAway"] >= self.MIN_GAMES else True, period=period)
            for key in d_var["TeamAway"]["AwayStats"].keys():
                if key == "Period":
                    break
                stats = d_var["TeamAway"]["AwayStats"][key] if endings.index(end) % 2 == 0 else \
                    (d_var["TeamAway"]["HomeStats"][key] + d_var["TeamAway"]["AwayStats"][key]) / 2
                data[key + "Away" + end] = format(stats, '.3f')

        for team in ("Home", "Away"):
            # actual_table = self.AL.create_actual_table(match_id, use_prev_season=False if self.AL.number_of_tour(match_id)[
            #                                                                           "Team" + team] == 0 else True)
            actual_table = self.AL.create_actual_table(match_id)
            d_var = actual_table.copy()[match["Team" + team]]
            for key in d_var.keys():
                data[key + team] = d_var[key]
            d_var = self.AL.upcoming_match(match_id)["Team" + team]
            data["FutureTeam" + team] = self.ST.code_string("Team", d_var["TeamName"]) if d_var["TeamName"] else self.ST.code_string("Team", "empty")
            data["FuturePlaceTeam" + team] = actual_table[d_var["TeamName"]]["Place"] if d_var["TeamName"] else -1
            data["FutureStatusTeam" + team] = d_var["MatchStatus"]


        return data

    def assemble_data(self) -> None:
        with open(self.league_name + "_learn_data+.csv", 'w', encoding='utf-8', newline='') as file:
            data = {
                "Result": 0, "Total2.5": 0, "Total1.5": 0,

                "League": 0, "Time": 0, "TeamHome": 0, "TeamAway": 0,
                "ManagerHome": 0, "ManagerAway": 0, "FormationHome": 0, "FormationAway": 0, "Stadium": 0, "Referee": 0,

                "BetHome": 0, "BetDraw": 0, "BetAway": 0,

                "RatingStartTeamHome": 0, "RatingSubstitutionHome": 0,
                "RatingStartTeamAway": 0, "RatingSubstitutionAway": 0,
                "RatingStartTeamHome3": 0, "RatingSubstitutionHome3": 0,
                "RatingStartTeamAway3": 0, "RatingSubstitutionAway3": 0,
                "GPP_StartHome": 0, "GPP_SubsHome": 0, "GPP_StartAway": 0, "GPP_SubsAway": 0,

                "GoalsTeamHome": 0, "AssistsTeamHome": 0, "GoalsTeamAway": 0, "AssistsTeamAway": 0,

                "FormTeamHome3": 0, "FormTeamAway3": 0, "FormTeamHome6": 0, "FormTeamAway6": 0,

                # local stats (Only Home or Away)
                "RatingTeamHome": 0, "RatingTeamAway": 0,
                "TotalShotsHome": 0, "TotalShotsAway": 0, "PossessionHome": 0, "PossessionAway": 0,
                "PassAccuracyHome": 0, "PassAccuracyAway": 0, "DribblesHome": 0, "DribblesAway": 0,
                "AerialsWonHome": 0, "AerialsWonAway": 0, "TacklesHome": 0, "TacklesAway": 0,
                "CornersHome": 0, "CornersAway": 0, "DispossessedHome": 0, "DispossessedAway": 0,
                "YellowCardHome": 0, "YellowCardAway": 0, "RedCardHome": 0, "RedCardAway": 0,

                # average stats (Home + Away)
                "RatingTeamHomeA": 0, "RatingTeamAwayA": 0,
                "TotalShotsHomeA": 0, "TotalShotsAwayA": 0, "PossessionHomeA": 0, "PossessionAwayA": 0,
                "PassAccuracyHomeA": 0, "PassAccuracyAwayA": 0, "DribblesHomeA": 0, "DribblesAwayA": 0,
                "AerialsWonHomeA": 0, "AerialsWonAwayA": 0, "TacklesHomeA": 0, "TacklesAwayA": 0,
                "CornersHomeA": 0, "CornersAwayA": 0, "DispossessedHomeA": 0, "DispossessedAwayA": 0,
                "YellowCardHomeA": 0, "YellowCardAwayA": 0, "RedCardHomeA": 0, "RedCardAwayA": 0,

                # same but for 3 last match
                "RatingTeamHome3": 0, "RatingTeamAway3": 0,
                "TotalShotsHome3": 0, "TotalShotsAway3": 0, "PossessionHome3": 0, "PossessionAway3": 0,
                "PassAccuracyHome3": 0, "PassAccuracyAway3": 0, "DribblesHome3": 0, "DribblesAway3": 0,
                "AerialsWonHome3": 0, "AerialsWonAway3": 0, "TacklesHome3": 0, "TacklesAway3": 0,
                "CornersHome3": 0, "CornersAway3": 0, "DispossessedHome3": 0, "DispossessedAway3": 0,
                "YellowCardHome3": 0, "YellowCardAway3": 0, "RedCardHome3": 0, "RedCardAway3": 0,

                "RatingTeamHome3A": 0, "RatingTeamAway3A": 0,
                "TotalShotsHome3A": 0, "TotalShotsAway3A": 0, "PossessionHome3A": 0, "PossessionAway3A": 0,
                "PassAccuracyHome3A": 0, "PassAccuracyAway3A": 0, "DribblesHome3A": 0, "DribblesAway3A": 0,
                "AerialsWonHome3A": 0, "AerialsWonAway3A": 0, "TacklesHome3A": 0, "TacklesAway3A": 0,
                "CornersHome3A": 0, "CornersAway3A": 0, "DispossessedHome3A": 0, "DispossessedAway3A": 0,
                "YellowCardHome3A": 0, "YellowCardAway3A": 0, "RedCardHome3A": 0, "RedCardAway3A": 0,

                "PHome": 0, "WHome": 0, "DHome": 0, "LHome": 0, "GFHome": 0, "GAHome": 0, "GDHome": 0, "PointsHome": 0, "PlaceHome": 0,
                "PAway": 0, "WAway": 0, "DAway": 0, "LAway": 0, "GFAway": 0, "GAAway": 0, "GDAway": 0, "PointsAway": 0, "PlaceAway": 0,

                "FutureTeamHome": 0, "FuturePlaceTeamHome": 0, "FutureStatusTeamHome": 0,
                "FutureTeamAway": 0, "FuturePlaceTeamAway": 0, "FutureStatusTeamAway": 0
            }
            d_keys = list()
            for key in data.keys():
                d_keys.append(key)
            writer = csv.DictWriter(file, fieldnames=d_keys)
            writer.writeheader()
            for match in self.AL.ALL_MATCHES:
                index = self.AL.ALL_MATCHES.index(match)
                tour = self.AL.number_of_tour(index)
                if tour["TeamHome"] == 0 or tour["TeamAway"] == 0:
                    continue
                if len(self.AL.ALL_MATCHES) - self.AL.ALL_MATCHES.index(match) < 50:
                    break
                data = self.convert_match_data(match, data.copy())
                if data["BetHome"] != 0:
                    writer.writerow(data)


class StringsTransfer:

    CONTENT = list()

    def __init__(self):
        pass

    def write_content(self) -> None:
        with open("Coding_data.csv", 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Team", "Manager", "Formation", "Stadium", "Referee", "League"])
            writer.writeheader()
            if self.CONTENT:
                writer.writerows(self.CONTENT)

    def code_string(self, feature: str, string: str) -> int:
        with open("Coding_data.csv", 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file, delimiter=',')
            counter = 0
            for row in reader:
                self.CONTENT.append(row)
                if not row[feature]:
                    continue
                if row[feature] == string:
                    self.CONTENT = list()
                    return counter
                else:
                    counter += 1

            # write new entry
            if len(self.CONTENT) <= counter:
                row = {"Team": "", "Manager": "", "Formation": "", "Stadium": "", "Referee": "", "League": ""}
                row[feature] = string
                self.CONTENT.append(row)
            else:
                self.CONTENT[counter][feature] = string
            self.write_content()
            self.CONTENT = list()
            return counter

    @staticmethod
    def code_time(time: str) -> float:
        hours = int(time[:time.find(":")])
        minutes = int(time[time.find(":") + 1:]) / 60
        return hours + minutes


class EmbeddingData:

    DATA = list()

    def make_sentences_list(self, league_name: str) -> None:
        with open(league_name + " _results_data.csv", 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            for match in reader:
                start_team1 = match["StartTeamHome"].split(', ')
                start_team2 = match["StartTeamAway"].split(', ')
                # subs_team1 = match["SubstitutionHome"].split(', ')[:3]
                # subs_team2 = match["SubstitutionAway"].split(', ')[:3]
                for team in (start_team1, start_team2):
                    for name_i in range(len(team)):
                        list_name = team[name_i].split(' ')
                        team[name_i] = '_'.join(list_name).lower()
                # start_team1 += subs_team1
                # start_team2 += subs_team2

                self.DATA.append(start_team1)
                self.DATA.append(start_team2)



# example = MatchesDataAnalytics("Premier League (Russia)1")
# example1 = DataPackager("Premier League (England)")
# example1.read_bets("england-premier-league_bets")
# example1.assemble_data()
# example2 = StringsTransfer()
#example2.write_content()
# print(example.calculate_players_rating(0))
# example3 = EmbeddingData()
# example3.make_sentences_list("Premier League (England)")
# print(example3.DATA)

