import csv


def ReadFile(file_name):
    # *** READ CSV FILE ***
    ALL_MATCHES = list()

    with open(file_name, 'r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        for match in reader:
            ALL_MATCHES.append(match)


    with open(file_name + "_corrected.csv", 'w', encoding='utf-8', newline='') as file:
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
        writer.writeheader()

        month_matches = list()
        month = ALL_MATCHES[0]["Date"]
        month = month[month.find("-")+1: month.rfind("-")]
        for match in ALL_MATCHES:
            current_month = match["Date"]
            current_month = current_month[current_month.find("-") + 1: current_month.rfind("-")]
            if current_month == month:
                month_matches.append(match)
            else:
                month_matches = month_matches[::-1]
                writer.writerows(month_matches)
                month_matches = list()
                month = current_month
                month_matches.append(match)

        month_matches = month_matches[::-1]
        writer.writerows(month_matches)



ReadFile("Premier League (Russia) _results_data.csv")