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

    return None

def getTeamGameStats(teamId, gameId, season, gameCount, db):
    # Do API call for gameId
    url = "https://api-web.nhle.com/v1/gamecenter/" + str(gameId) + "/boxscore"
    gameObj = makeRequest(url)

    # Check opponent id for given team.id
    team_status = "homeTeam" if gameObj["homeTeam"]["abbrev"] == teamId else "awayTeam"
    opp_status = "homeTeam" if team_status == "away" else "awayTeam"

    goals_allowed = gameObj[opp_status]["score"]
    penalties = gameObj[team_status]["pim"]

    document = {
        "teamID": teamId,
        "penalties": penalties,
        "goalsAllowed": goals_allowed,
        "season": season,
        "gameCount": gameCount,
    }

    db.insert("Ops V2", document)

def getTeams():
    # Make API call to get all team abbreviatins (in NHL history)
    url = 'https://api.nhle.com/stats/rest/en/team'
    data = makeRequest(url)
    
    try:
        res = []
        for team in data["data"]:
            res.append(team['triCode'])
        # return array of ids
        return res
    except KeyError:
        print("Error: JSON structure does not match expectations")
    exit()

def getGames(teamId, season):
    # Make API call to get schedule of given team during given season
    url = 'https://api-web.nhle.com/v1/club-schedule-season/' + teamId + '/' + season
    data = makeRequest(url)

    gameIds = []

    # If team was not playing that season (e.g. an old NHL team)
    if (data == None): return gameIds

    # Collect all gameIds, and update team.games
    for game in data["games"]:
        # If not a regular season game, ignore it!
        if (game["gameType"] != 2): continue

        gameId = game["id"]
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
seasons = generate_seasons(2010, 2023)
teams = getTeams()
for season in seasons:
    threads = []
    for team in teams:
        print("STARTING TEAM:", team)
        gameIds = getGames(team, season)
        print("FETCHED GAMES:", len(gameIds))
        for i, gameId in enumerate(gameIds):
            thread = threading.Thread(target=getTeamGameStats, args=(team, gameId, season, i+1, db))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
            
    print("Done with season " + season)
print("Done pre-processing")
