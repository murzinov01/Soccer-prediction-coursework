from selenium import webdriver
from time import sleep
import csv

MAIN_URL = 'https://1xbet.whoscored.com/'


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
        self.PLAYER_TABLE = self.driver.find_element_by_id("player-table-statistics-body").find_elements_by_tag_name("tr")

    # Собираем информацию и записываем ее в csv файл
    def collecting_info_from_player_table(self):
        # Открываем файл с помощью конструкции with, которая автоматически закроет его в конце работы
        with open("players_score_data.csv", 'w', encoding='utf-8', newline='') as file:
            # атрибут fieldnames отвечает за ключи в csv файле. CSV файл - таблица-словарь, в которой в ПЕРВОЙ строке присутствуют ключи словаря. Каждый ключ соответсвует столбцу таблицы.
            writer = csv.DictWriter(file, fieldnames=["Name", "Meta_data", "Apps", "Mins", "Goals", "Assists", "Yel_card", "Red_card",
                                                      "ShotsPerGame", "PassSuccess", "AerialWonPerGame", "ManOfTheMatch", "Rating"])
            # Этот метод записывает заголовки из fieldnames в первую строку файла
            writer.writeheader()
            # Crawl pages
            span = self.driver.find_element_by_id("statistics-paging-summary").find_element_by_tag_name("b").text
            for page in range(int(span[span.find('/') + 1: span.find('|') - 1])):
                # Through the raws
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


class ParseLeagueResults (WhoScoredParser):
    TABLE_BUTTONS = list()

    def __init__(self, driver):
        super().__init__(driver)

    def start_parse(self):
        self.find_leagues_buttons()
        self.parse_leagues()

    def find_leagues_buttons(self):
        self.TABLE_BUTTONS = self.driver.find_element_by_id('popular-tournaments-list').find_elements_by_tag_name('li')

    def parse_leagues(self):
        for league_num in range(len(self.TABLE_BUTTONS)):
            league_name = self.TABLE_BUTTONS[league_num].text
            print(league_name)
            # click league
            self.TABLE_BUTTONS[league_num].click()
            # click "Fixtures" button
            sleep(2)
            self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].click()
            # create file
            with open(league_name + "_results_data.csv", 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Time", "TeamHome", "ResultTeamHome", "ResultTeamAway",
                                                          "TeamAway", "Date"])
                writer.writeheader()
                # Crawl seasons
                for i in range(5):
                    sleep(3)
                    # Crawl months
                    prev_month_button = ''
                    flag = True
                    while flag or prev_month_button.get_attribute('title') != 'No data for previous month':
                        sleep(2)
                        current_table = self.driver.find_element_by_id('tournament-fixture-wrapper').find_elements_by_tag_name('tr')
                        date = ''
                        for row in current_table:
                            # refresh date
                            if row.get_attribute("class") == "rowgroupheader":
                                date = row.text[row.text.find(',') + 2:]
                                continue
                            # take info
                            match_info = row.find_elements_by_tag_name('td')
                            # skip failed match
                            if match_info[4].text == 'vs':
                                continue

                            match = {
                                "Time": match_info[1].text,
                                "TeamHome": match_info[3].find_element_by_tag_name('a').text,
                                "ResultTeamHome": match_info[4].text[: match_info[4].text.find(':') - 1].lstrip('*'),
                                "ResultTeamAway": match_info[4].text[match_info[4].text.find(':') + 2:].rstrip('*'),
                                "TeamAway": match_info[5].find_element_by_tag_name('a').text,
                                "Date": date

                            }
                            writer.writerow(match)
                            print(match)
                        # make exception for CL and EL
                        flag = False
                        if len(self.driver.find_elements_by_id('date-controller')) == 0:
                            break
                        else:
                            prev_month_button = self.driver.find_element_by_id('date-controller').find_element_by_tag_name('a')
                        prev_month_button.click()
                        # sleep(1)
                        # refresh button
                        prev_month_button = self.driver.find_element_by_id('date-controller').find_element_by_tag_name('a')
                    # change season
                    self.driver.find_element_by_id('seasons').find_elements_by_tag_name('option')[i + 1].click()
                    # click "Fixtures" button
                    sleep(3)
                    self.driver.find_element_by_id('sub-navigation').find_elements_by_tag_name('a')[1].click()
            self.find_leagues_buttons()


def main():
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome("/Users/sanduser/PycharmProjects/Parser/chromedriver")
    # Parsing players scores
    #ParsePlayers = ParsePlayersScore(driver)
    #ParsePlayers.accept_cookies()
    #ParsePlayers.start_parse()
    # Parsing match results
    Parser = ParseLeagueResults(driver)
    Parser.accept_cookies()
    Parser.start_parse()


if __name__ == '__main__':
    main()
