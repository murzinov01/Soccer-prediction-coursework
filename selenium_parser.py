import csv
import sys
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


MAIN_URL = 'https://whoscored.com/'


def progressBar(value: int, end_value: int, team_home: str, team_away: str, bar_length=100) -> None:
    percent = float(value) / end_value
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f"\r| {team_home} vs {team_away} | [{arrow + spaces}] {int(round(percent * 100))}%")
    sys.stdout.flush()


# Parser
class WhoScoredParser:
    PLAYER_TABLE = ""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)

    def go_to_target_page(self, url: str) -> None:
        self.driver.get(url)

    def go_to_main_page(self) -> None:
        self.driver.get(MAIN_URL)

    # Find the button 'accept' and press on it
    def accept_cookies(self) -> None:
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'qc-cmp-button')))
        self.driver.find_elements_by_class_name('qc-cmp-button')[1].click()

    def find_leagues_buttons(self):
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'hover-target')))
        return self.driver.find_element_by_id('popular-tournaments-list').find_elements_by_tag_name('li')


class ParsePlayersScore(WhoScoredParser):
    URL = 'https://1xbet.whoscored.com/statistics'

    # find the player's statistic table
    def __init__(self, driver):
        super().__init__(driver)

    def start_parse(self) -> None:
        self.go_to_target_page(self.URL)
        self.find_players_table()
        self.collecting_info_from_player_table()

    def find_players_table(self) -> None:
        sleep(3)
        self.PLAYER_TABLE = self.driver.find_element_by_id("player-table-statistics-body").find_elements_by_tag_name(
            "tr")

    # Collect information and write it in file
    def collecting_info_from_player_table(self) -> None:
        with open("players_score_data.csv", 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file,
                                    fieldnames=["Name", "Meta_data", "Apps", "Mins", "Goals", "Assists", "Yel_card",
                                                "Red_card",
                                                "ShotsPerGame", "PassSuccess", "AerialWonPerGame", "ManOfTheMatch",
                                                "Rating"])
            writer.writeheader()

            # Crawl pages
            span = self.driver.find_element_by_id("statistics-paging-summary").find_element_by_tag_name("b").text
            max_page = int(span[span.find('/') + 1: span.find('|') - 1])
            for page in range(max_page):
                # Through the rows
                print(f"Collecting data: page {page + 1}/{max_page}...")
                for tr in self.PLAYER_TABLE:
                    player = tr.find_elements_by_tag_name("td")
                    row = {
                        "Name": player[2].text[:player[2].text.find('\n')],
                        "Meta_data": player[2].text[player[2].text.find('\n') + 1:],
                        "Apps": player[3].text,
                        "Mins": player[4].text,
                        "Goals": player[5].text,
                        "Assists": player[6].text,
                        "Yel_card": player[7].text,
                        "Red_card": player[8].text,
                        "ShotsPerGame": player[9].text,
                        "PassSuccess": player[10].text,
                        "AerialWonPerGame": player[11].text,
                        "ManOfTheMatch": player[12].text,
                        "Rating": player[13].text,
                    }
                    writer.writerow(row)

                # press the next button
                self.driver.find_element_by_id("statistics-paging-summary").find_element_by_id("next").click()
                sleep(3)

                # found player table in new page
                self.find_players_table()


class ParseLeagueResults(WhoScoredParser):

    TABLE_BUTTONS = list()
    SEASONS_URL = list()
    SEASONS_NAME = list()
    MATCHES_URL = list()

    def __init__(self, driver, start_league=0, start_season=0, start_month="", start_match=0):
        self.start_league = start_league
        self.start_season = start_season
        self.start_month = start_month
        self.start_match = start_match
        super().__init__(driver)

    def start_parse(self) -> None:
        self.load_check_point()
        self.TABLE_BUTTONS = self.find_leagues_buttons()
        self.parse_leagues()

    @staticmethod
    def do_check_point(point: str) -> None:
        with open("save.txt", "w") as file:
            file.write(point)

    def load_check_point(self) -> None:
        with open("save.txt", "r") as file:
            params = file.readline().split(",")
            self.start_league = int(params[0])
            self.start_season = int(params[1])
            self.start_match = int(params[2])
            print(f"\nCheck_point: League № {params[0]}, Season № {params[1]}, Match № {params[2]}")

    @staticmethod
    def parse_match_moments(match_moments: dict, incidents, team_key: str) -> None:
        for incident in incidents:
            for moment in incident.find_elements_by_class_name('match-centre-header-team-key-incident'):
                # Cards
                if moment.get_attribute('data-type') == '17':
                    card = moment.find_element_by_tag_name("div").get_attribute('data-card-type')
                    if card in ('31', '32'):
                        match_moments[team_key]["yellow_cards"] += 1
                    if card in ('33', '32'):
                        match_moments[team_key]["red_cards"] += 1
                # Goals
                elif moment.get_attribute('data-type') == '16':
                    text = moment.text
                    match_moments[team_key]["goals"] += text.replace(text[text.find('('): text.find(')') + 1],                                                                 "") + ", "
                # Assists
                elif moment.get_attribute('data-type') == '1':
                    match_moments[team_key]["assists"] += moment.text + ", "

    def parse_match(self, match: str) -> dict:
        # *** MATCH SUMMARY PARSING ***
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.go_to_target_page(match)
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'player')))

        # Match content
        date = self.driver.find_element_by_id("match-header").find_elements_by_class_name("info-block")[
            2].find_elements_by_tag_name("dd")
        teams = self.driver.find_element_by_class_name("match-header").find_element_by_tag_name(
            "tr").find_elements_by_tag_name("td")
        team_info = [self.driver.find_elements_by_class_name("team-info")[0].find_elements_by_tag_name("div"),
                     self.driver.find_elements_by_class_name("team-info")[1].find_elements_by_tag_name("div")]
        match_info = self.driver.find_element_by_class_name("match-info").find_elements_by_tag_name("span")
        # Players content
        pitch = self.driver.find_element_by_class_name("pitch")
        substitutes = self.driver.find_elements_by_class_name("substitutes")

        # Detailed players content
        stats = self.driver.find_element_by_class_name('match-centre-stats').find_elements_by_class_name('has-stats')
        detailed_info = list()
        for i in range(8):
            detailed_info.append(stats[i].find_elements_by_tag_name('span'))

        # **** PARSING PLAYERS AND THEIR STATS ******
        # Parse team line-up
        players = pitch.find_elements_by_class_name("player-name-wrapper")
        players_score = pitch.find_elements_by_class_name("player-stat")
        for i in range(len(players)):
            players[i] = players[i].get_attribute("title")
            players_score[i] = players_score[i].text

        # Parse substitutions
        subs_home = dict()
        subs_away = dict()
        subs_home["players"] = substitutes[0].find_elements_by_class_name("player-name-wrapper")
        subs_home["stats"] = substitutes[0].find_elements_by_class_name("player-stat")
        subs_away["players"] = substitutes[1].find_elements_by_class_name("player-name-wrapper")
        subs_away["stats"] = substitutes[1].find_elements_by_class_name("player-stat")

        for i in range(len(subs_home["players"])):
            subs_home["players"][i] = subs_home["players"][i].get_attribute("title")
            rating = subs_home["stats"][i].text
            subs_home["stats"][i] = rating if rating else "-1"

        for i in range(len(subs_away["players"])):
            subs_away["players"][i] = subs_away["players"][i].get_attribute("title")
            rating = subs_away["stats"][i].text
            subs_away["stats"][i] = rating if rating else "-1"

        # *** PARSING MATCH MOMENTS ***
        incidents_home = self.driver.find_element_by_id('live-incidents').find_elements_by_class_name('home-incident')
        incidents_away = self.driver.find_element_by_id('live-incidents').find_elements_by_class_name('away-incident')
        match_moments = {
            "home": {
                "goals": "",
                "assists": "",
                "yellow_cards": 0,
                "red_cards": 0},
            "away": {
                "goals": "",
                "assists": "",
                "yellow_cards": 0,
                "red_cards": 0}}
        self.parse_match_moments(match_moments, incidents_home, "home")
        self.parse_match_moments(match_moments, incidents_away, "away")

        # Collecting data in row
        data = {
            #  Detailed information about match
            "Date": date[1].text[date[1].text.find(',') + 2:],
            "Time": date[0].text,
            "TeamHome": teams[0].text,
            "ResultTeamHome": teams[1].text[:teams[1].text.find(" ")],
            "TeamAway": teams[2].text,
            "ResultTeamAway": teams[1].text[teams[1].text.find(":") + 2:],
            "ManagerHome": team_info[0][1].text[team_info[0][1].text.find(":") + 2:],
            "ManagerAway": team_info[1][1].text[team_info[1][1].text.find(":") + 2:],
            "FormationHome": team_info[0][2].text,
            "FormationAway": team_info[1][2].text,
            "RatingTeamHome": team_info[0][0].text,
            "RatingTeamAway": team_info[1][0].text,
            "Stadium": match_info[2].text,
            "Weather": match_info[7].text,
            "Referee": match_info[10].text if len(match_info) > 10 else "NO_REFEREE",
            # Detailed information about teams
            "StartTeamHome": ', '.join(players[:12]),
            "StartTeamAway": ', '.join(players[12:]),
            "RatingStartTeamHome": ', '.join(players_score[:12]),
            "RatingStartTeamAway": ', '.join(players_score[12:]),
            "SubstitutionHome": ', '.join(subs_home["players"]),
            "SubstitutionAway": ', '.join(subs_away["players"]),
            "RatingSubstitutionHome": ', '.join(subs_home["stats"]),
            "RatingSubstitutionAway": ', '.join(subs_away["stats"]),
            "TotalShotsHome": detailed_info[0][0].text,
            "TotalShotsAway": detailed_info[0][2].text,
            "PossessionHome": detailed_info[1][0].text,
            "PossessionAway": detailed_info[1][2].text,
            "PassAccuracyHome": detailed_info[2][0].text,
            "PassAccuracyAway": detailed_info[2][2].text,
            "DribblesHome": detailed_info[3][0].text,
            "DribblesAway": detailed_info[3][2].text,
            "AerialsWonHome": detailed_info[4][0].text,
            "AerialsWonAway": detailed_info[4][2].text,
            "TacklesHome": detailed_info[5][0].text,
            "TacklesAway": detailed_info[5][2].text,
            "CornersHome": detailed_info[6][0].text,
            "CornersAway": detailed_info[6][2].text,
            "DispossessedHome": detailed_info[7][0].text,
            "DispossessedAway": detailed_info[7][2].text,
            # Detailed information about cards
            "GoalsHome": match_moments['home']['goals'][:-2],
            "GoalsAway": match_moments['away']['goals'][:-2],
            "AssistsHome": match_moments['home']['assists'][:-2],
            "AssistsAway": match_moments['away']['assists'][:-2],
            "YellowCardHome": match_moments['home']['yellow_cards'],
            "YellowCardAway": match_moments['away']['yellow_cards'],
            "RedCardHome": match_moments['home']['red_cards'],
            "RedCardAway": match_moments['away']['red_cards']}

        self.driver.close()
        return data

    def parse_leagues(self) -> None:
        for league_num in range(self.start_league, len(self.TABLE_BUTTONS)):
            print(f"Collecting data: {round(league_num / len(self.TABLE_BUTTONS) * 100, 2)} %...")
            league_name = self.TABLE_BUTTONS[league_num].text + ' (' + \
                self.TABLE_BUTTONS[league_num].find_element_by_tag_name('a').get_attribute('title') + ') '
            print(league_name)

            # *** CHOOSE LEAGUE ***
            self.TABLE_BUTTONS[league_num].click()
            self.wait.until(EC.element_to_be_clickable((By.ID, 'seasons')))

            # *** SAVE SEASON URL
            for season in self.driver.find_element_by_id('seasons').find_elements_by_tag_name('option')[:5]:
                self.SEASONS_URL.append(MAIN_URL + season.get_attribute('value'))
                self.SEASONS_NAME.append(season.text)

            # create file
            with open(league_name + "_results_data.csv", 'a+', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[
                                                    "Date", "Season", "Time", "TeamHome", "ResultTeamHome", "ResultTeamAway",
                                                    "TeamAway", "ManagerHome", "ManagerAway",
                                                    "FormationHome", "FormationAway", "RatingTeamHome",
                                                    "RatingTeamAway", "Stadium", "Weather", "Referee",
                                                    "StartTeamHome", "RatingStartTeamHome", "SubstitutionHome",
                                                    "RatingSubstitutionHome",
                                                    "StartTeamAway", "RatingStartTeamAway", "SubstitutionAway",
                                                    "RatingSubstitutionAway",
                                                    "TotalShotsHome", "TotalShotsAway", "PossessionHome",
                                                    "PossessionAway",
                                                    "PassAccuracyHome", "PassAccuracyAway", "DribblesHome",
                                                    "DribblesAway",
                                                    "AerialsWonHome", "AerialsWonAway", "TacklesHome", "TacklesAway",
                                                    "CornersHome", "CornersAway", "DispossessedHome",
                                                    "DispossessedAway",
                                                    "GoalsHome", "GoalsAway", "AssistsHome", "AssistsAway",
                                                    "YellowCardHome", "YellowCardAway", "RedCardHome", "RedCardAway"])

                # check if the file is exist
                if not os.path.getsize(league_name + "_results_data.csv"):
                    writer.writeheader()

                # go to target season
                if self.start_season:
                    self.go_to_target_page(self.SEASONS_URL[self.start_season])

                # click "Fixtures" button
                self.wait.until(EC.element_to_be_clickable((By.ID, 'sub-navigation')))
                self.go_to_target_page(
                    self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].get_attribute("href"))

                # Crawl seasons
                for i in range(self.start_season, 5):
                    # *** SAVE URL OF MATCHES ***
                    while True:
                        sleep(1)
                        current_table = self.driver.find_element_by_id(
                            'tournament-fixture-wrapper').find_elements_by_tag_name('tr')
                        for row in current_table:
                            # refresh date
                            if row.get_attribute("class") == "rowgroupheader":
                                continue
                            match_info = row.find_elements_by_tag_name('td')
                            # skip failed match
                            if match_info[4].text == 'vs':
                                continue
                            self.MATCHES_URL.append(
                                match_info[-1].find_element_by_tag_name('a').get_attribute('href').replace(
                                    "MatchReport", "Live"))

                        # make exception for CL and ELe
                        if len(self.driver.find_elements_by_id('date-controller')) == 0 or\
                                self.driver.find_element_by_id('date-controller').find_element_by_tag_name(
                                'a').get_attribute('title') == 'No data for previous month':
                            break
                        else:
                            prev_month_button = self.driver.find_element_by_id(
                                'date-controller').find_element_by_tag_name('a')
                        prev_month_button.click()

                    # *** PARSE MATCHES ***
                    last_match = len(self.MATCHES_URL)
                    for match_index in range(self.start_match, last_match):
                        # Make save
                        self.do_check_point(f"""{league_num},{i},{match_index}""")

                        # Collect information
                        row = self.parse_match(self.MATCHES_URL[match_index])
                        row["Season"] = self.SEASONS_NAME[i]

                        # Check progress
                        progressBar(match_index, last_match, row["TeamHome"], row["TeamAway"])

                        # Write information
                        writer.writerow(row)

                    self.start_match = 0
                    self.MATCHES_URL = []
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    if i != 4:
                        # save season
                        self.do_check_point(f"""{league_num},{i + 1},{0}""")

                        # change season
                        self.go_to_target_page(self.SEASONS_URL[i + 1])
                        self.wait.until(EC.element_to_be_clickable((By.ID, 'sub-navigation')))

                        # click "Fixtures" button
                        self.go_to_target_page(
                            self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].get_attribute("href"))
                    else:
                        self.do_check_point(f"""{league_num + 1},{0},{0}""")

            self.start_season = 0
            self.TABLE_BUTTONS = self.find_leagues_buttons()
        print("Collecting data: 100 %...")


class ParseTeamsScore(WhoScoredParser):
    TABLE_BUTTONS = list()

    def __init__(self, driver):
        super().__init__(driver)

    def start_parse(self) -> None:
        self.TABLE_BUTTONS = self.find_leagues_buttons()
        self.parse_teams()

    def parse_teams(self) -> None:
        # create file
        with open("teams_score_data.csv", 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file,
                                    fieldnames=["League", "Team", "Place", "Score", "Points", "Form", "Discipline",
                                                "Goal per game", "Possession", "Pass Accuracy", "Shots per game",
                                                "Tackles per game", "Dribbles per game",
                                                'P', 'W', 'D', 'L', 'GF', 'GA', 'GD'])
            writer.writeheader()

            for league_num in range(len(self.TABLE_BUTTONS)):
                print(f"Collecting data: {round(league_num / len(self.TABLE_BUTTONS) * 100, 2)} %...")
                league_name = self.TABLE_BUTTONS[league_num].text + ' (' + \
                    self.TABLE_BUTTONS[league_num].find_element_by_tag_name('a').get_attribute('title') + ') '

                # click league
                self.TABLE_BUTTONS[league_num].click()
                sleep(2)

                # find season table
                teams_table = self.driver.find_element_by_class_name('standings').find_elements_by_tag_name('tr')

                # make buffer for team stats
                teams = list()
                teams_url = list()
                for row in teams_table:
                    # parse each team
                    team_stats = row.find_elements_by_tag_name('td')
                    team_form = (3 * len(team_stats[10].find_elements_by_class_name('w')) +
                                 len(team_stats[10].find_elements_by_class_name('d')) -
                                 3 * len(team_stats[10].find_elements_by_class_name('l')) + 18) / 0.36
                    team = {
                        "League": league_name,
                        "Team": team_stats[1].text,
                        "Place": team_stats[0].text,
                        "Points": team_stats[9].text,
                        "Form": round(team_form, 2),
                        'P': team_stats[2].text,
                        'W': team_stats[3].text,
                        'D': team_stats[4].text,
                        'L': team_stats[5].text,
                        'GF': team_stats[6].text,
                        'GA': team_stats[7].text,
                        'GD': team_stats[8].text
                    }
                    teams.append(team)
                    # save url
                    teams_url.append(team_stats[1].find_element_by_tag_name('a').get_attribute('href'))

                # now visit pages of each club for detailed stats
                for page in range(len(teams_table)):
                    self.go_to_target_page(teams_url[page])

                    # find a team profile box
                    side_box = self.driver.find_element_by_class_name('team-profile-side-box')
                    teams[page]['Score'] = side_box.find_element_by_class_name('rating').text
                    stats = side_box.find_element_by_class_name('stats-container').find_elements_by_tag_name('dd')

                    # value a discipline
                    discipline = int(stats[8].find_elements_by_tag_name('span')[0].text) + \
                        2 * int(stats[8].find_elements_by_tag_name('span')[1].text)

                    # save stats
                    teams[page]['Goal per game'] = stats[2].text
                    teams[page]['Possession'] = stats[3].text
                    teams[page]['Pass Accuracy'] = stats[4].text
                    teams[page]['Shots per game'] = stats[5].text
                    teams[page]['Tackles per game'] = stats[6].text
                    teams[page]['Dribbles per game'] = stats[7].text
                    teams[page]['Discipline'] = discipline

                    # write one team row
                    writer.writerow(teams[page])
                    progressBar(page, len(teams_table), league_name)
                self.TABLE_BUTTONS = self.find_leagues_buttons()
                print('')
