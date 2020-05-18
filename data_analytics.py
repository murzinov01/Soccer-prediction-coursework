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
        with open(self.league_name + "_results_data.csv", 'r', encoding='utf-8', newline='') as file:
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

    @staticmethod
    def rating_help(target_player: str, line_up: dict, match_line_up: list, r_match_line_up: list, period=-1) -> None:
        index = line_up["Players"].index(target_player)
        if period != -1 and line_up["Games_num"][index] >= period:
            return
        if target_player in match_line_up:
            index_r = match_line_up.index(target_player)
            print(line_up["Ratings"])
            print(index, index_r)
            line_up["Ratings"][index] += r_match_line_up[index_r] if r_match_line_up[index_r] != -1 else -0.5
            line_up["Games_num"][index] += 1

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

            r_match_home_line_up = match["RatingStartTeamHome"].split(', ')
            r_match_away_line_up = match["RatingStartTeamAway"].split(', ')
            r_match_home_subs = match["RatingSubstitutionHome"].split(', ')
            r_match_away_subs = match["RatingSubstitutionAway"].split(', ')

            for line_up in (home_line_up, away_line_up, home_line_up, away_line_up):
                for target_player in line_up["Players"]:
                    self.rating_help(target_player, line_up, match_home_line_up, r_match_home_line_up, period)
                    self.rating_help(target_player, line_up, match_away_line_up, r_match_away_line_up, period)
                    self.rating_help(target_player, line_up, match_home_subs, r_match_home_subs, period)
                    self.rating_help(target_player, line_up, match_away_subs, r_match_away_subs, period)

        # calculate average
        for line_up in (home_line_up, away_line_up, home_line_up, away_line_up):
            line_up["Ratings"] = [line_up["Ratings"][i] / line_up["Games_num"][i] for i in range(len(line_up["Ratings"]))]
            line_up["Ratings"] = list(map(lambda x: x if x > self.MIN_PLAYER_RATING else self.MIN_PLAYER_RATING, line_up["Ratings"]))
            # for player_i in range(len(line_up["Ratings"])):
            #     line_up["Ratings"][player_i] /= line_up["Games_num"][player_i]

        ratings = {
            "TeamHome": {
                "Start": sum(home_line_up["Ratings"]) / len(home_line_up["Ratings"]),
                "Subs": sum(home_subs["Ratings"]) / len(home_subs["Ratings"]),
            },
            "TeamAway": {
                "Start": sum(away_line_up["Ratings"]) / len(away_line_up["Ratings"]),
                "Subs": sum(away_subs["Ratings"]) / len(away_subs["Ratings"]),
            }
        }

        return ratings


class StringsTransfer:

    CONTENT = list()

    def __init__(self):
        pass

    def read_content(self) -> None:
        with open("Premier League (England) _results_data.csv", 'r', encoding='utf-8', newline='') as file:
            self.CONTENT = file.readlines()

    def write_content(self) -> None:
        with open("Coding_data.csv", 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Team", "Manager", "Formation", "Stadium", "Referee"])
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
                row = {"Team": "", "Manager": "", "Formation": "", "Stadium": "", "Referee": ""}
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

example = MatchesDataAnalytics("Premier League (Russia) ")
print(example.calculate_players_rating(0))
# example = StringsTransfer()
# print(example.code_string("Referee", "Misha"))
# print(example.code_string("Referee", "Andrey"))
# print(example.code_string("Team", "Zenit"))
# print(example.code_string("Referee", "Misha"))