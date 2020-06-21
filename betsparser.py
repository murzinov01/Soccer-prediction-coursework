import csv
import os
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium import webdriver


MAIN_URL = 'https://www.oddsportal.com/soccer/'


class OddsPortalParser:

    SEASON_LINKS = list()
    MATCHES = list()

    def __init__(self, new_driver) -> None:
        self.driver = new_driver
        self.wait = WebDriverWait(self.driver, 20)
        self.league_name = ""

    def go_to_target_page(self, url_ending: str) -> None:
        self.driver.get(MAIN_URL + url_ending)
        sleep(3)
        self.league_name = url_ending[url_ending.find("/") + 1:]
        self.league_name = self.league_name[:self.league_name.find("/")]

    def save_season_links(self) -> None:
        links = self.driver.find_elements_by_class_name("main-filter")[1]
        links = links.find_elements_by_tag_name("a")[:5]
        self.SEASON_LINKS = list(map(lambda x: x.get_attribute("href"), links))

    def find_matches(self) -> None:
        self.MATCHES = self.driver.find_elements_by_class_name("deactivate")

    def collect_data(self) -> None:
        with open(self.league_name + "_bets.csv", 'a+', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["TeamHome", "TeamAway", "ResultTeamHome", "ResultTeamAway",
                                                      "Bet1", "BetX", "Bet2"])
            if not os.path.getsize(self.league_name + "_bets.csv"):
                writer.writeheader()
            for season_link in self.SEASON_LINKS:
                self.driver.get(season_link)
                sleep(2)
                max_pages_len = len(self.driver.find_element_by_id("pagination").find_elements_by_tag_name("a")) - 3
                for page_num in range(1, max_pages_len + 1):
                    self.driver.get(season_link + f"/#/page/{page_num}/")
                    sleep(1)
                    self.find_matches()
                    for match in self.MATCHES:
                        if match.find_element_by_class_name("table-odds").text != "postp.":
                            TeamHome = match.find_element_by_class_name("table-participant").find_element_by_tag_name("a").text
                            TeamAway = TeamHome[TeamHome.find("-") + 2:]
                            TeamHome = TeamHome[:TeamHome.find("-") - 1]
                            result = match.find_element_by_class_name("table-odds").text
                            bets = match.find_elements_by_class_name("odds-nowrp")
                            row = {
                                "TeamHome": TeamHome,
                                "TeamAway": TeamAway,
                                "ResultTeamHome": result[:result.find(":")],
                                "ResultTeamAway": result[result.find(":") + 1:],
                                "Bet1": bets[0].text,
                                "BetX": bets[1].text,
                                "Bet2": bets[2].text,
                            }
                            print(row)
                            writer.writerow(row)


# driver = webdriver.Chrome()  # for Misha
driver = webdriver.Chrome("/Users/sanduser/PycharmProjects/Parser/chromedriver")  # for Andrey
example = OddsPortalParser(driver)
example.go_to_target_page("england/premier-league/results/")
example.save_season_links()
example.collect_data()
