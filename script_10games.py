import requests
import mongo
from datetime import datetime
import threading

class TeamSeasonStat:
    def __init__(self, id, season):
        self.id = id

        self.season = season
        
        #all players that have ever played in that team's season
        self.players = []
        
        #all games this team played for this season
        self.games = []

        # Tracks the win/loss streak up to point i
        self.win_loss = []
        
        #maps game-id to whether that game is a home or away for this team
        self.is_home = {}

        #maps game-id to opponent id
        self.opps = {}
        
        #maps player-id to that player's age
        self.player_age = {}
        
        #maps (player-id) to the player's position
        self.position = {}

         #maps player-id tuple to the player's name
        self.name_season = {}
        
        #maps (player-id, game_id) tuple to the player#'s TOI in that game
        self.toi = {}

        #maps (player-id, game_id) tuple to the player#'s +/- in that game
        self.plus_minus = {}
        
        #maps (player-id, game_id) tuple to the player's total goals made in that game
        self.goals = {}
                
        #maps (player-id, game_id) tuple to the player's total assists made in that game
        self.assists = {}
        
        #maps (player-id, game_id) tuple to the player's total power-play points made in that game
        self.pow_play_points = {}
        
    #Returns the average for the last 10 games before the specified game
    #Returns None if that player did not play for more than 10 games
    def get_last_10_average(self, i, fn):
        if (i < 10):
            return None

        sum = 0

        for g in self.games[i-10:i]:
            v = fn(g)
            if (v == None):
                return None
                
            sum += v
        
        return sum/10
    
    #Returns the sum for the next 10 games starting at the specified game
    #Returns None if that player did not play for the next 10 games
    def get_next_10_sum(self, i, fn):
        if (i < 10 or i > len(self.games) - 15):
            return None

        sum = 0

        for g in self.games[i:i+10]:
            v = fn(g)
            if (v == None):
                return None
                
            sum += v
        
        return sum

    #Returns the next 10 opponents of a team (in abbreviations)
    def get_next_10_opps(self, i):
        if (i < 10 or i > len(self.games) - 15):
            return None
        
        opps = []

        for g in self.games[i:i+10]:
            opp = self.opps[g]
            opps.append(opp)
        
        return opps
        

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
    return None


# oppIds is now an array of opp IDs. Same as main script, but consider all opp Ids here
def getOpponentStats(oppIds, season, gameCount):
    filter_query = {"teamID": {"$in": oppIds}, "season": season, "gameCount": {"$lt": gameCount}}
    documents = list(db.find("Ops V2", filter_query))

    # returns "False" so that no entries are made for this specific prediction (opponent data not found)
    if len(documents) == 0: return False, -1, -1

    avgGoalsAllowed = 0
    avgPenalties = 0
    
    for document in documents:
        avgGoalsAllowed += document["goalsAllowed"]
        avgPenalties += document["penalties"]

    avgGoalsAllowed = avgGoalsAllowed / len(documents)
    avgPenalties = avgPenalties / len(documents)

    return True, avgGoalsAllowed, avgPenalties

# Additional API call needed to fetch player data (specifically the age)
def getPlayerAge(playerId, season):
    url = "https://api-web.nhle.com/v1/player/" + str(playerId) + "/landing"
    data = makeRequest(url)

    if (data == None): return None

    birthDate = int(data["birthDate"][0:4])
    age = int(season[0:4]) - birthDate

    return age

def storeStats(team):
    for gameId in team.games:
        # Do API call for gameId
        url = "https://api-web.nhle.com/v1/gamecenter/" + str(gameId) + "/boxscore"
        gameObj = makeRequest(url)

        if (gameObj == None):
            print("ERROR:", gameId)
            return False

        team_status = "homeTeam" if team.is_home[gameId] else "awayTeam"

        # Iterate though positions, and then players at each position (omit goalies)
        playerPositions = ["forwards", "defense"]
        for position in playerPositions:
            for player in gameObj["boxscore"]["playerByGameStats"][team_status][position]:
                player_id = player["playerId"]
                player_name_season = player["name"]["default"] + " " + team.season
            
                currPosition = position

                if player_id not in team.players:
                    playerAge = getPlayerAge(player_id, team.season)
                    
                    if (playerAge != None):
                        team.players.append(player_id)
                        team.player_age[player_id] = playerAge
                        team.position[player_id] = currPosition
                        team.name_season[player_id] = player_name_season

                # goals, assits, toi, +/-
                team.goals[(player_id, gameId)] = player["goals"]
                team.assists[(player_id, gameId)] = player["assists"]
                toiSplit = player["toi"].split(":")
                team.toi[(player_id, gameId)] = int(toiSplit[0]) * 60 + int(toiSplit[1])
                team.plus_minus[(player_id, gameId)] = player["plusMinus"]
                team.pow_play_points[(player_id, gameId)] = player["powerPlayPoints"]

    return True

def makeEntries(team):
    # Iterate from index 10 to the "15th to last game" (make sure we have 10 future games for data)
    
    # For each game id
    for i, g in enumerate(team.games):
        if i < 10 or i > len(team.games) - 15:
            continue

        winLossStreak = team.win_loss[i]
        opps = team.get_next_10_opps(i)
        valid, avgOppGoalsAllowed, avgOppPenalties = getOpponentStats(opps, team.season, i + 1)
        
        if (valid == False): continue
        
        # For each player
        # Create variables for (avgGoals, avgAssists, avgTOI, avgPlusMinus, avgPowerPlay, ) i
        for _, p in enumerate(team.players):
            actualGoals = team.get_next_10_sum(i, lambda g_: team.goals.get((p, g_)))
            actualAssists = team.get_next_10_sum(i, lambda g_:  team.assists.get((p, g_)))
            
            if actualGoals == None or actualAssists == None: continue
            
            avgGoals = team.get_last_10_average(i, lambda g_: team.goals.get((p, g_)))
            if avgGoals == None:
                continue

            avgAssists = team.get_last_10_average(i, lambda g_: team.assists.get((p, g_)))
            if avgAssists == None:
                continue

            avgTOI = team.get_last_10_average(i, lambda g_: team.toi.get((p, g_)))
            if avgTOI == None:
                continue

            avgPlusMinus = team.get_last_10_average(i, lambda g_: team.plus_minus.get((p, g_)))
            if avgPlusMinus == None:
                continue

            avgPowerPlay = team.get_last_10_average(i, lambda g_: team.pow_play_points.get((p, g_)))
            if avgPowerPlay == None:
                continue

            powPlayGoalProb = avgPowerPlay * avgOppPenalties

            document = {
                "playerNameSeason": team.name_season[p],
                "playerAge": team.player_age[p],
                "playerPosition": team.position[p],
                "avgGoals": avgGoals,
                "avgAssists": avgAssists,
                "avgTOI": avgTOI,
                "avgPlusMinus": avgPlusMinus,
                "powPlayGoalProb": powPlayGoalProb,
                "winLossStreak": winLossStreak,
                "avgOppGoalsAllowed": avgOppGoalsAllowed,
                "actualGoals": actualGoals,
                "actualAssists": actualAssists
            }
            
            db.insert("Entries V2", document)

    print("Finished entries for:", team.id, team.season)

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

def getGames(team):
    # Make API call to get schedule of given team during given season (only regular games)
    url = url = 'https://api-web.nhle.com/v1/club-schedule-season/' + str(team.id) + '/' + team.season
    data = makeRequest(url)

    # If team was not playing that season (e.g. an old NHL team)
    if (data == None): return False
        
    # Collect all gameIds, and update team.games
    for game in data["games"]:
        # If not a regular season game, ignore it!
        if (game["gameType"] != 2): continue
            
        gameId = game["id"]
        team.games.append(gameId)
        
        # Check opponent id for given team.id
        team.is_home[gameId] = game["homeTeam"]["abbrev"] == team.id
        team_status = ""
        opp_status = ""
        if team.is_home[gameId]:
            team_status = "homeTeam"
            opp_status = "awayTeam"
        else:
            team_status = "awayTeam"
            opp_status = "homeTeam"
        
        # Check if game is win/loss for given team.id. Also, store opp_id
        did_team_win = game[team_status]["score"] > game[opp_status]["score"]
        team.opps[gameId] = game[opp_status]["abbrev"]
        if (len(team.win_loss) > 0):
            # Win during win streak. ++
            # Loss during win streak. -1
            # Win during lose streak. 1
            # Loss during lose streak. --
            lastStreak = team.win_loss[-1]
            if did_team_win:
                team.win_loss.append((lastStreak + 1 )if lastStreak > 0 else 1)
            else:
                team.win_loss.append((lastStreak - 1)if lastStreak < 0 else -1)
        else:
            team.win_loss.append(1 if did_team_win else -1)

    return len(team.games) > 0
            
def calcStats(teamID, season):
    team = TeamSeasonStat(teamID, season)
    success = getGames(team)
    # If team actually played that season (could be an old team)
    if success:
        success = storeStats(team)
        # Only if we were able to fetch team data (new API sometimes has bugs)
        if success:
            makeEntries(team)

def generate_seasons(start_year=2000, end_year=2023):
    seasons = []
    for year in range(start_year, end_year):
        season_start = str(year)
        season_end = str(year + 1)
        season = season_start + season_end
        seasons.append(season)

    return seasons


now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)


db = mongo.DB()
seasons = generate_seasons(2010, 2023)
teams = getTeams()
for season in seasons:
    threads = []
    for teamID in teams:
        thread = threading.Thread(target=calcStats, args=(teamID, season))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    print("Finished season " + season)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)