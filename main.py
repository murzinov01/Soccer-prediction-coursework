from selenium_parser import ParseLeagueResults, ParseTeamsScore, ParsePlayersScore
from selenium import webdriver


def main():
    driver = webdriver.Chrome()  # for Misha
    # driver = webdriver.Chrome("/Users/sanduser/PycharmProjects/Parser/chromedriver")  # for Andrey

    # ***** PARSING PLAYERS SCORE *****
    # ParsePlayers = ParsePlayersScore(driver)
    # ParsePlayers.accept_cookies()
    # ParsePlayers.start_parse()

    # ***** PARSING MATCH RESULTS *****
    ParserLeagues = ParseLeagueResults(driver)
    ParserLeagues.go_to_main_page()
    ParserLeagues.accept_cookies()
    while True:
        try:
            ParserLeagues.go_to_main_page()
            ParserLeagues.start_parse()
        except:
            continue
        break

# ***** Parse TEAMS SCORE *****
# ParserTeams = ParseTeamsScore(driver)
# ParserTeams.accept_cookies()
# ParserTeams.start_parse()


if __name__ == '__main__':
    main()
