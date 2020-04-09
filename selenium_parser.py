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
        sleep(5)
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
        with open("data.csv", 'w', encoding='utf-8', newline='') as file:
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


def main():
    driver = webdriver.Chrome()
    # driver = webdriver.Chrome("/Users/sanduser/PycharmProjects/Parser/chromedriver")
    # Parsing players scores
    ParsePlayers = ParsePlayersScore(driver)
    ParsePlayers.accept_cookies()
    ParsePlayers.start_parse()


if __name__ == '__main__':
    main()
