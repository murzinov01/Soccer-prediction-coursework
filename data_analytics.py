import csv


class MatchesDataAnalytics:
    ALL_MATCHES = list()
    RECENT_MATCHES = list()
    LAST_SEASON_MATCHES = list()
    league_name = ''
    MIN_PLAYER_RATING = 3.0

    def __init__(self, league_name):
        self.league_name = league_name
        self.read_matches()

    def read_matches(self) -> None:
        # *** READ CSV FILE ***
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

        if use_prev_season:
            year2 = int(end_season[:end_season.find("/")])
            year1 = year2 - 1
            end_season = str(year1) + "/" + str(year2)

        for match in self.RECENT_MATCHES:
            # search for season end
            if match["Season"] == end_season:
                self.LAST_SEASON_MATCHES.append(match)

    def find_match_id(self, date: str, team_home: str, team_away="", season=""):
        for index in range(0, len(self.ALL_MATCHES)):
            match = self.ALL_MATCHES[index]
            if match["Date"] == date and match["TeamHome"] == team_home:
                return index

    @staticmethod
    def calculate_table_stats(TABLE: dict, team_name: str, team_home: bool, match) -> None:
        if team_name not in TABLE.keys():
            TABLE[team_name] = {
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

        if team_home:
            team_status1 = "Home"
            team_status2 = "Away"
        else:
            team_status2 = "Home"
            team_status1 = "Away"

        # calculate
        TABLE[team_name]["P"] += 1

        if int(match["ResultTeam" + team_status1]) > int(match["ResultTeam" + team_status2]):
            TABLE[team_name]["W"] += 1
        elif int(match["ResultTeam" + team_status1]) == int(match["ResultTeam" + team_status2]):
            TABLE[team_name]["D"] += 1
        else:
            TABLE[team_name]["L"] += 1

        TABLE[team_name]["GF"] += int(match["ResultTeam" + team_status1])
        TABLE[team_name]["GA"] += int(match["ResultTeam" + team_status2])
        TABLE[team_name]["GD"] = TABLE[team_name]["GF"] - TABLE[team_name]["GA"]
        TABLE[team_name]["Points"] = 3 * TABLE[team_name]["W"] + TABLE[team_name]["D"]

    @staticmethod
    def calculate_stats(match: dict, team_status: str) -> dict:
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

    @staticmethod
    def calculate_stats_average(stats: dict):
        # check if empty
        if not stats:
            return
        period = stats["Period"]
        for key in stats.keys():
            if key in ("Period", "RedCard", "YellowCard"):
                continue
            value = stats[key]/period
            stats[key] = format(value, '.2f')

    def create_actual_table(self, match_id: int, use_prev_season=False) -> dict:
        TABLE = dict()

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
                "HomeStats": dict(),
                "AwayStats": dict()
            },
            "TeamAway": {
                "HomeStats": dict(),
                "AwayStats": dict()
            },
        }

        team_home_name = self.ALL_MATCHES[match_id]["TeamHome"]
        team_away_name = self.ALL_MATCHES[match_id]["TeamAway"]

        period_counter_home = 0
        period_counter_away = 0

        concrete_period = len(self.LAST_SEASON_MATCHES) if period == -1 else period

        # *** SUM ALL STATS ***
        for match in self.LAST_SEASON_MATCHES:
            # main condition
            if period_counter_home >= concrete_period and period_counter_away >= concrete_period:
                break

            if period_counter_home < concrete_period and match["TeamHome"] == team_home_name:
                # our first team stats in home games
                stats = self.calculate_stats(match, "Home")
                for key in stats.keys():
                    STATS["TeamHome"]["HomeStats"][key] = (0 if key not in STATS["TeamHome"]["HomeStats"].keys() else
                                                           STATS["TeamHome"]["HomeStats"][key]) + stats[key]
                period_counter_home += 1

            elif period_counter_home < concrete_period and match["TeamAway"] == team_home_name:
                # our first team stats in away games
                stats = self.calculate_stats(match, "Away")
                for key in stats.keys():
                    STATS["TeamHome"]["AwayStats"][key] = (0 if key not in STATS["TeamHome"]["AwayStats"].keys() else
                                                           STATS["TeamHome"]["AwayStats"][key]) + stats[key]
                period_counter_home += 1

            if period_counter_away < concrete_period and match["TeamHome"] == team_away_name:
                # our second team stats in home games
                stats = self.calculate_stats(match, "Home")
                for key in stats.keys():
                    STATS["TeamAway"]["HomeStats"][key] = (0 if key not in STATS["TeamAway"]["HomeStats"].keys() else
                                                           STATS["TeamAway"]["HomeStats"][key]) + stats[key]
                period_counter_away += 1

            elif period_counter_away < concrete_period and match["TeamAway"] == team_away_name:
                # our second team stats in away games
                stats = self.calculate_stats(match, "Away")
                for key in stats.keys():
                    STATS["TeamAway"]["AwayStats"][key] = (0 if key not in STATS["TeamAway"]["AwayStats"].keys() else
                                                           STATS["TeamAway"]["AwayStats"][key]) + stats[key]
                period_counter_away += 1
        # print(STATS)
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
        print(home_line_up)
        print(away_line_up)
        self.season_matches(match_id)

        for match in self.LAST_SEASON_MATCHES:
            goalee = (match["GoalsHome"] + ", " + match["GoalsAway"]).split(', ')
            assistant = (match["AssistsHome"] + ", " + match["AssistsAway"]).split(', ')
            print(goalee)
            # print(assistant)
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
            # print(line_up["Ratings"])
            # print(index, index_r)
            line_up["Ratings"][index] += r_match_line_up[index_r] if r_match_line_up[index_r] != -1 else self.MIN_PLAYER_RATING
            line_up["Games_num"][index] += 1
            print(line_up["Ratings"], line_up["Games_num"])

    def calculate_players_rating(self, match_id: int, period=-1) -> dict:
        self.season_matches(match_id)

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
        for match in self.LAST_SEASON_MATCHES:
            match_home_line_up = match["StartTeamHome"].split(', ')
            match_away_line_up = match["StartTeamAway"].split(', ')
            match_home_subs = match["SubstitutionHome"].split(', ')
            match_away_subs = match["SubstitutionAway"].split(', ')

            r_match_home_line_up = list(map(lambda x: float(x), match["RatingStartTeamHome"].split(', ')))
            r_match_away_line_up = list(map(lambda x: float(x), match["RatingStartTeamAway"].split(', ')))
            r_match_home_subs = list(map(lambda x: float(x), match["RatingSubstitutionHome"].split(', ')))
            r_match_away_subs = list(map(lambda x: float(x), match["RatingSubstitutionAway"].split(', ')))

            print(self.LAST_SEASON_MATCHES.index(match))
            for line_up in (home_line_up, away_line_up, home_subs, away_subs):
                for target_player in line_up["Players"]:
                    self.rating_help(target_player, line_up, match_home_line_up, r_match_home_line_up, period)
                    self.rating_help(target_player, line_up, match_away_line_up, r_match_away_line_up, period)
                    self.rating_help(target_player, line_up, match_home_subs, r_match_home_subs, period)
                    self.rating_help(target_player, line_up, match_away_subs, r_match_away_subs, period)

        print(home_line_up)
        print(away_line_up)
        print(home_subs)
        print(away_subs)

        # calculate average
        for line_up in (home_line_up, away_line_up, home_subs, away_subs):
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

        print(form)

        form["TeamHome"] = round((form["TeamHome"] + 3 * period) / (period * 0.06), 2)
        form["TeamAway"] = round((form["TeamAway"] + 3 * period) / (period * 0.06), 2)

        return form





#
# class DataPackager:
#
#     ALL_MATCHES = list()
#
#     def __init__(self, league_name: str):
#         self.league_name = league_name
#
#     def read_file(self):
#         with open(self.league_name + " _results_data.csv", 'r', encoding='utf-8', newline='') as file:
#             reader = csv.DictReader(file)
#             self.ALL_MATCHES = [match for match in reader]
#
#     def convert_match_data(self, match: dict) -> dict:
#         new_data = {
#
#         }
#     def assemble_data(self):
#         with open(self.league_name + "_learn_data.csv", 'w', encoding='utf-8', newline='') as file:
#             writer = csv.DictWriter(file, fieldnames=
#                                                 ["League", "Time", "TeamHome",
#                                                  "TeamAway", "ManagerHome", "ManagerAway",
#                                                  "FormationHome", "FormationAway", "Stadium", "Referee",
#
#                                                  "HomeRatingTeamHome", "AwayRatingTeamHome",
#                                                  "HomeRatingTeamAway", "AwayRatingTeamAway",
#                                                  "RatingStartTeamHome", "RatingSubstitutionHome",
#                                                  "RatingStartTeamAway", "RatingSubstitutionAway",
#
#                                                  "TotalShotsHome", "TotalShotsAway", "PossessionHome", "PossessionAway",
#                                                  "PassAccuracyHome", "PassAccuracyAway", "DribblesHome", "DribblesAway",
#                                                  "AerialsWonHome", "AerialsWonAway", "TacklesHome", "TacklesAway",
#                                                  "CornersHome", "CornersAway", "DispossessedHome", "DispossessedAway",
#                                                  "YellowCardHome", "YellowCardAway", "RedCardHome", "RedCardAway",
#
#                                                  "TotalShotsHome3", "TotalShotsAway3", "PossessionHome3", "PossessionAway3",
#                                                  "PassAccuracyHome3", "PassAccuracyAway3", "DribblesHome3", "DribblesAway3",
#                                                  "AerialsWonHome3", "AerialsWonAway3", "TacklesHome3", "TacklesAway3",
#                                                  "CornersHome3", "CornersAway3", "DispossessedHome3", "DispossessedAway3",
#                                                  "YellowCardHome3", "YellowCardAway3", "RedCardHome3", "RedCardAway3",
#
#
#
#
#
#
#
#
#
#             for match in self.ALL_MATCHES:
#                 # function
#                 pass

class StringsTransfer:

    CONTENT = list()

    def __init__(self):
        pass

    def write_content(self) -> None:
        with open("Coding_data.csv", 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Team", "Manager", "Formation", "Stadium", "Referee", "League"])
            writer.writeheader()
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

example = MatchesDataAnalytics("Premier League (Russia)1")
# print(example.upcoming_match(176))
# print (example.calculate_form(9))
# print(example.calculate_players_rating(5))
# example = StringsTransfer()
# print(example.code_string("Referee", "Misha"))
# print(example.code_string("Referee", "Andrey"))
# print(example.code_string("Team", "Zenit"))
# print(example.code_string("Referee", "Misha"))