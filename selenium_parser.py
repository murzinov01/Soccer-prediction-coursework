from selenium import webdriver
from time import sleep
import requests
import csv

URL = 'https://1xbet.whoscored.com/statistics'


# Парсер
class WhoScoredParser:
    PLAYER_TABLE = ""

    def __init__(self, driver):
        self.driver = driver

    def start_parse(self):
        self.go_to_target_page()
        self.find_players_table()
        self.collecting_info_from_player_table()

    def go_to_target_page(self):
        self.driver.get(URL)
        sleep(5)
        self.pass_the_warning()

    # Ищем кнопку accept и нажимаем на нее
    def pass_the_warning(self):
        self.driver.find_elements_by_class_name('qc-cmp-button')[1].click()
        sleep(5)

    # Находим таблицу с статистикой играков
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
            # Идем по строкам таблицы
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


def main():
    driver = webdriver.Chrome()
    Parser = WhoScoredParser(driver)
    Parser.start_parse()


if __name__ == '__main__':
    main()
