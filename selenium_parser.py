from selenium import webdriver
from time import sleep, time
import csv
import sys
import os

MAIN_URL = 'https://whoscored.com/'


def progressBar(value: int, endvalue: int, name="Percent", bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\r{0}: [{1}] {2}%".format(name, arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


# Парсер
class WhoScoredParser:
    PLAYER_TABLE = ""

    def __init__(self, driver):
        self.driver = driver

    def go_to_target_page(self, url):
        self.driver.get(url)
        sleep(5)

    # Ищем кнопку accept и нажимаем на нее
    def accept_cookies(self):
        self.driver.get(MAIN_URL)
        sleep(6)
        self.driver.find_elements_by_class_name('qc-cmp-button')[1].click()
        sleep(3)

    def find_leagues_buttons(self):
        return self.driver.find_element_by_id('popular-tournaments-list').find_elements_by_tag_name('li')


class ParsePlayersScore(WhoScoredParser):
    URL = 'https://1xbet.whoscored.com/statistics'

    # Находим таблицу с статистикой играков
    def __init__(self, driver):
        super().__init__(driver)

    def start_parse(self):
        self.go_to_target_page(self.URL)
        self.find_players_table()
        self.collecting_info_from_player_table()

    def find_players_table(self):
        sleep(3)
        self.PLAYER_TABLE = self.driver.find_element_by_id("player-table-statistics-body").find_elements_by_tag_name(
            "tr")

    # Собираем информацию и записываем ее в csv файл
    def collecting_info_from_player_table(self):
        # Открываем файл с помощью конструкции with, которая автоматически закроет его в конце работы
        with open("players_score_data.csv", 'w', encoding='utf-8', newline='') as file:
            # атрибут fieldnames отвечает за ключи в csv файле. CSV файл - таблица-словарь, в которой в ПЕРВОЙ строке присутствуют ключи словаря. Каждый ключ соответсвует столбцу таблицы.
            writer = csv.DictWriter(file,
                                    fieldnames=["Name", "Meta_data", "Apps", "Mins", "Goals", "Assists", "Yel_card",
                                                "Red_card",
                                                "ShotsPerGame", "PassSuccess", "AerialWonPerGame", "ManOfTheMatch",
                                                "Rating"])
            # Этот метод записывает заголовки из fieldnames в первую строку файла
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
    MATCHES_URL = list()

    def __init__(self, driver, start_league=0, start_season=0, start_month="", start_match=0):
        self.start_league = start_league
        self.start_season = start_season
        self.start_month = start_month
        self.start_match = start_match
        super().__init__(driver)

    def start_parse(self):
        self.load_check_point()
        self.TABLE_BUTTONS = self.find_leagues_buttons()
        self.parse_leagues()

    @staticmethod
    def do_check_point(point: str):
        with open("save.txt", "w") as file:
            file.write(point)

    def load_check_point(self):
        with open("save.txt", "r") as file:
            params = file.readline().split(",")
            self.start_league = int(params[0])
            self.start_season = int(params[1])
            self.start_month = params[2]
            self.start_match = int(params[3])
            print(params)

    def parse_match(self, match: str):
        # print(match)
        self.go_to_target_page(match)
        date = self.driver.find_element_by_id("match-header").find_elements_by_class_name("info-block")[2].find_elements_by_tag_name("dd")
        teams = self.driver.find_element_by_class_name("match-header").find_element_by_tag_name("tr").find_elements_by_tag_name("td")
        team_info = [self.driver.find_elements_by_class_name("team-info")[0].find_elements_by_tag_name("div"),
                     self.driver.find_elements_by_class_name("team-info")[1].find_elements_by_tag_name("div")]
        match_info = self.driver.find_element_by_class_name("match-info").find_elements_by_tag_name("span")
        pitch_field = self.driver.find_elements_by_class_name("pitch-field")
        players_in_team_home = ""
        players_in_team_away = ""
        for player in pitch_field[0].find_elements_by_class_name("player"):
            players_in_team_home += player.find_element_by_class_name("player-info").find_elements_by_tag_name("div")[0].get_attribute("title") + ","
        for player in pitch_field[1].find_elements_by_class_name("player"):
            players_in_team_away += player.find_element_by_class_name("player-info").find_elements_by_tag_name("div")[0].get_attribute("title") + ","
        data = {
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
            "Referee": match_info[10].text,
            "StartTeamHome": players_in_team_home[:-2],
            "StartTeamAway": players_in_team_away[:-2],
        }
        print(data)
        return data

    def parse_leagues(self):
        for league_num in range(self.start_league, len(self.TABLE_BUTTONS)):
            print(f"Collecting data: {round(league_num / len(self.TABLE_BUTTONS) * 100, 2)} %...")
            league_name = self.TABLE_BUTTONS[league_num].text + ' (' + \
                          self.TABLE_BUTTONS[league_num].find_element_by_tag_name('a').get_attribute('title') + ') '
            print(league_name)
            # click league
            self.TABLE_BUTTONS[league_num].click()
            # click "Fixtures" button
            sleep(2)
            self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].click()
            sleep(2)
            # create file
            with open(league_name + "_results_data.csv", 'a+', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Date", "Time", "TeamHome", "ResultTeamHome", "ResultTeamAway", "TeamAway", "ManagerHome", "ManagerAway",
                                                          "FormationHome", "FormationAway", "Stadium", "Weather", "Referee", "StartTeamHome", "SubstitutionHome",
                                                          "ActiveSubstitutesHome", "ActiveSubstitutesAway", "RatingPlayersHome", "StartTeamAway", "SubstitutionAway",
                                                          "RatingPlayersAway", "RatingTeamHome", "RatingTeamAway", "TotalShotsHome", "TotalShotsAway", "PossessionHome",
                                                          "PossessionAway", "PassAccuracyHome", "PassAccuracyAway", "DribblesHome", "DribblesHome", "TacklesHome", "TacklesAway",
                                                          "CornersHome", "CornersAway", "DispossessedHome", "DispossessedAway"])
                print('File size: ' + str(os.path.getsize(league_name + "_results_data.csv")))
                if not os.path.getsize(league_name + "_results_data.csv"):
                    writer.writeheader()
                if self.start_season:
                    self.driver.find_element_by_id('seasons').find_elements_by_tag_name('option')[self.start_season].click()
                    # click "Fixtures" button
                    sleep(3)
                    self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].click()
                # Crawl seasons
                for i in range(self.start_season, 5):
                    sleep(3)
                    # Crawl months
                    prev_month_button = ''
                    flag = True
                    while flag or prev_month_button.get_attribute('title') != 'No data for previous month':
                        sleep(2)
                        # Go to target month
                        if self.start_month and self.start_month != self.driver.find_element_by_id('date-controller').find_elements_by_tag_name('a')[1].text:
                            # click the previous button
                            self.driver.find_element_by_id('date-controller').find_element_by_tag_name('a').click()
                            # refresh button
                            prev_month_button = self.driver.find_element_by_id('date-controller').find_element_by_tag_name('a')
                            continue

                        current_table = self.driver.find_element_by_id('tournament-fixture-wrapper').find_elements_by_tag_name('tr')
                        for row in current_table:
                            # refresh date
                            if row.get_attribute("class") == "rowgroupheader":
                                continue
                            match_info = row.find_elements_by_tag_name('td')
                            # skip failed match
                            if match_info[4].text == 'vs':
                                continue
                            self.MATCHES_URL.append(match_info[-1].find_element_by_tag_name('a').get_attribute('href').replace("MatchReport", "Live"))

                        # *** PARSE MATCHES ***
                        month_name = ''
                        if len(self.driver.find_elements_by_id('date-controller')):
                            month_name = self.driver.find_element_by_id('date-controller').find_elements_by_tag_name('a')[1].text
                        for match_index in range(self.start_match, len(self.MATCHES_URL)):
                            # make save
                            self.do_check_point(f"""{league_num},{i},{month_name},{match_index}""")
                            # write information
                            writer.writerow(self.parse_match(self.MATCHES_URL[match_index]))
                        self.start_match = 0
                        # make exception for CL and ELe
                        flag = False
                        if len(self.driver.find_elements_by_id('date-controller')) == 0:
                            break
                        else:
                            prev_month_button = self.driver.find_element_by_id(
                                'date-controller').find_element_by_tag_name('a')
                        prev_month_button.click()
                        # refresh button
                        prev_month_button = self.driver.find_element_by_id('date-controller').find_element_by_tag_name(
                            'a')
                    # change season
                    self.start_month = ''
                    self.driver.find_element_by_id('seasons').find_elements_by_tag_name('option')[i + 1].click()
                    # click "Fixtures" button
                    sleep(3)
                    self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].click()
            self.start_season = 0
            self.TABLE_BUTTONS = self.find_leagues_buttons()
        print("Collecting data: 100 %...")


class ParseTeamsScore(WhoScoredParser):
    TABLE_BUTTONS = list()

    def __init__(self, driver):
        super().__init__(driver)

    def start_parse(self):
        self.TABLE_BUTTONS = self.find_leagues_buttons()
        self.parse_teams()

    def parse_teams(self):
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
                    team_form = (3 * len(team_stats[10].find_elements_by_class_name('w')) + \
                                 len(team_stats[10].find_elements_by_class_name('d')) - \
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


def main():
    # times = []
    #driver = webdriver.Chrome()
    driver = webdriver.Chrome("/Users/sanduser/PycharmProjects/Parser/chromedriver")
    # ***** Parsing players scores *****
    # start_time = time()
    # ParsePlayers = ParsePlayersScore(driver)
    # ParsePlayers.accept_cookies()
    # ParsePlayers.start_parse()
    # times.append(time() - start_time)
    # ***** Parsing match results *****
    # start_time = time()
    ParserLeagues = ParseLeagueResults(driver)
    ParserLeagues.accept_cookies()
    ParserLeagues.start_parse()
    # ***** Parse teams score *****
    # start_time = time()
    # ParserTeams = ParseTeamsScore(driver)
    # ParserTeams.accept_cookies()
    # ParserTeams.start_parse()
    # times.append(time() - start_time)
    # print(f"ParsePlayers - {times[0]}\nParserLeagues - {times[1]}")
    # print(f"ParserLeagues - {times[0]}")


if __name__ == '__main__':
    main()
