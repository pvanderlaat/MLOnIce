import requests
import mongo
import threading

def makeRequest(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except KeyError:
        print("Error: JSON structure does not match expectations")
    # return array of ids
    exit()

def getTeamGameStats(teamId, gameId, season, gameCount, db):
    # Do API call for gameId
    url = "https://statsapi.web.nhl.com/api/v1/game/" + str(gameId) + "/boxscore"
    gameObj = makeRequest(url)

    # Check opponent id for given team.id
    team_status = "home" if gameObj["teams"]["home"]["team"]["id"] == teamId else "away"
    opp_status = "home" if team_status == "away" else "away"

    goals_allowed = gameObj["teams"][opp_status]["teamStats"]["teamSkaterStats"]["goals"]
    penalties = gameObj["teams"][team_status]["teamStats"]["teamSkaterStats"]["pim"]

    document = {
        "teamID": teamId,
        "penalties": penalties,
        "goalsAllowed": goals_allowed,
        "season": season,
        "gameCount": gameCount,
    }

    db.insert("Ops", document)

def getTeamsForThisYear(season):
    # Make API call to get all team ids for this season
    url = 'https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster&season=' + season
    data = makeRequest(url)
    
    # Note about team ids:
        # Team ids are unique across the NHL history.
        # For example:
            # The year 20102011 contains a team id of 11 (Atlanta Thrashers)
            # The year 20222023 does not contain team 11 since the team was sold in 2011 
    try:
        res = []
        for team in data["teams"]:
            res.append(team['id'])
        # return array of ids
        return res
    except KeyError:
        print("Error: JSON structure does not match expectations")
    exit()

def getGames(teamId, season):
    # Make API call to get schedule of given team during given season (only regular games)
    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=" + season + "&expand=schedule.linescore&teamId=" + str(teamId) + "&gameType=R"
    data = makeRequest(url)

    gameIds = []

    # Collect all gameIds, and update team.games
    for date in data["dates"]:
        for game in date["games"]:
            # print(game["gamePk"])
            gameId = game["gamePk"]
            gameIds.append(gameId)

    return gameIds

def generate_seasons(start_year=2000, end_year=2023):
    seasons = []
    for year in range(start_year, end_year):
        season_start = str(year)
        season_end = str(year + 1)
        season = season_start + season_end
        seasons.append(season)

    return seasons

db = mongo.DB()
# seasons = [20002001, ..., 20222023]
seasons = generate_seasons(2000, 2023)
for season in seasons:
    teams = getTeamsForThisYear(season)
    threads = []
    for team in teams:
        gameIds = getGames(team, season)
        for i, gameId in enumerate(gameIds):
            thread = threading.Thread(target=getTeamGameStats, args=(team, gameId, season, i+1, db))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
            
    print("Done with season " + season)
print("Done pre-processing")
