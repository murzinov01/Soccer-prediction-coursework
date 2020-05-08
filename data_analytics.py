import csv


class MatchesDataAnalytics:
    ALL_MATCHES = list()
    RECENT_MATCHES = list()
    LAST_SEASON_MATCHES = list()
    league_name = ''

    def __init__(self, league_name):
        self.league_name = league_name
        self.read_matches()

    def read_matches(self):
        # *** READ CSV FILE ***
        with open(self.league_name + "_results_data.csv", 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file, delimiter=',')
            for match in reader:
                self.ALL_MATCHES.append(match)

    def recent_matches(self, match_id: int):
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