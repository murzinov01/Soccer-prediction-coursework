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

    def find_match_id(self, date: str, team_home: str, team_away="", season=""):
        for index in range(0, len(self.ALL_MATCHES)):
            match = self.ALL_MATCHES[index]
            if match["Date"] == date and match["TeamHome"] == team_home:
                return index

    def CreateActualTable(self, match_id: int, use_prev_season=False, period=0):
        table = {
            "Home": dict(),
            "Away": dict()
        }
        prev_table = {
            "Home": dict(),
            "Away": dict()
        }

        # *** FIND CURRENT SEASON MATCHES ***
        self.LAST_SEASON_MATCHES = list()
        self.recent_matches(match_id)
        end_season = self.ALL_MATCHES[match_id]["Season"]

        for match in self.RECENT_MATCHES:
            # search for season end
            if match["Date"] + " " + match["TeamHome"] != end_season:
                self.LAST_SEASON_MATCHES.append(match)
        # creating a finished season table
        if period == -1:
            self.LAST_SEASON_MATCHES.insert(0, self.ALL_MATCHES[match_id])

        # *** RETURN LAST SEASON FINISHED TABLE ***
        if use_prev_season:
            cur_season_last_match_index = self.find_match_id(self.LAST_SEASON_MATCHES[-1]["Date"],
                                                         self.LAST_SEASON_MATCHES[-1]["TeamHome"])
            self.recent_matches(cur_season_last_match_index)
            prev_table = self.CreateActualTable(cur_season_last_match_index+1, period=-1)
            self.recent_matches(match_id)

        # *** ANALYSE DATA ***
        
        TEAMS = dict()

        #end_season = match["Season"]
        #year2 = int(end_season[: end_season.find("/")]) - (1 if use_prev_season else 0)
        #year1 = year2 - 1
        #end_season = str(year1) + "/" + str(year2)
        return table