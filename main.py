from selenium_parser import ParseLeagueResults, ParseTeamsScore, ParsePlayersScore
from selenium import webdriver
from data_analytics import MatchesDataAnalytics

def main():
    # driver = webdriver.Chrome()  # for Misha
    # driver = webdriver.Chrome("/Users/sanduser/PycharmProjects/Parser/chromedriver")  # for Andrey

    # ***** PARSING PLAYERS SCORE *****
    # ParsePlayers = ParsePlayersScore(driver)
    # ParsePlayers.accept_cookies()
    # ParsePlayers.start_parse()

    # ***** PARSING MATCH RESULTS *****

    # ParserLeagues = ParseLeagueResults(driver)
    # ParserLeagues.go_to_main_page()
    # ParserLeagues.accept_cookies()
    # while True:
    #     try:
    #         ParserLeagues.start_parse()
    #     except Exception as e:
    #         print(repr(e))
    #         if len(driver.window_handles) > 1:
    #             driver.close()
    #             driver.switch_to.window(driver.window_handles[0])
    #         ParserLeagues.go_to_main_page()
    #         continue
    #     break

    # ***** Parse TEAMS SCORE *****
    # ParserTeams = ParseTeamsScore(driver)
    # ParserTeams.accept_cookies()
    # ParserTeams.start_parse()

    # ***** ANALYTICS ***** (match_id starts from 0) *****
    anal = MatchesDataAnalytics("Premier League (Russia) ")
    print(anal.create_actual_table(0))
    print(anal.summarise_statistic(0))


if __name__ == '__main__':
    main()
