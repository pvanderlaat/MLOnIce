def getTeamGameStats(teamId, gameId, season, gameCount):
    # Make API call for given gameId
    # Get the goals allowed & penalties for given teamId

    # Make entry into DB. Document model is as followed:

    # document
        # teamId
        # penalties
        # goalsAllowed
        # season (ex: 20172018, 20052006)
        # gameCount
    pass

def getTeamsForThisYear(season):
    # Make API call to get all team ids for this season
    # return array of ids
    pass

def getGames(team, season):
    # Make API call to get schedule of given team during given season (only regular games)
    # Collect all gameIds, and return array
    pass

# seasons = [20002001, ..., 20222023]
seasons = []
for season in seasons:
    teams = getTeamsForThisYear(season)
    for team in teams:
        gameIds = getGames(team, season)
        for i, gameId in enumerate(gameIds):
            getTeamGameStats(team, gameId, season, i)
