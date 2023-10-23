import requests
import mongo
from datetime import datetime
# a = game h/a
# b = team's winning/losing streak
# c = player position (F/D)
# d = player age
# e = player's average goals per game (for the last 10 game) 
# f = player's average assists per game (for the last 10 game) 
# g = player's average +/- (for the last 10 games)
# h = opponent teams average goals allowed per game (this season... so far)
# i = (Player’s avg # of powerplay POINTS per game this season... so far) * (opponent team’s average # of penalties per game this season... so far)
# j = player's average TOI (for the last 10 games)

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
        
        #maps (player-id, game_id) tuple to the player's position in that game
        self.position = {}
        
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
        
    #Returns the average for the last 10 games before the specidied game
    #Returns None if that player did not play for more than 10 games
    def get_last_10_average(self,i, fn):
        if (i < 10):
            return None

        sum = 0

        for g in self.games[i-10:i]:
            v = fn(g)
            if (v == None):
                return None
                
            sum += v
        
        return sum/10

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
# Mongo v2 document model

# teamId
# penalties
# goalsAllowed
# season (ex: 20172018, 20052006)
# gameCount

def getOpponentStats(oppId, season, gameCount):
    # Figure out how to connect to Mongo
    # documents =  mongoDB.findAll({
    #     teamId: oppId,
    #     season,
    #     # filter gameCount < gameCount
    # })
    filter_query = {"teamID": oppId, "season": season, "gameCount": {"$lt": gameCount}}
    documents = list(db.find("Ops", filter_query))

    avgGoalsAllowed = 0
    avgPenalties = 0
    
    for document in documents:
        avgGoalsAllowed += document["goalsAllowed"]
        avgPenalties += document["penalties"]

    avgGoalsAllowed = avgGoalsAllowed / len(documents)
    avgPenalties = avgPenalties / len(documents)

    return avgGoalsAllowed, avgPenalties


def makeEntry(team):
    for player in team.players:
        # player avg goal
        avgGoals = 0
        for goals in player.goals[:10]:
            avgGoals += goals
        avgGoals = avgGoals / 10
        
        # Calculate rest of values
        # Make an entry

def storeStats(team):
    for gameId in team.games:
        # Do API call for gameId
        url = "https://statsapi.web.nhl.com/api/v1/game/" + str(gameId) + "/boxscore"
        gameObj = makeRequest(url)

        # Check game h/a for given team.id + win_loss
            # done below
            # done below

        team_status = "home" if team.is_home[gameId] == "home" else "away"

        # Iterate though players in roster[team.id]
        for _, player in gameObj["teams"][team_status]["players"].items():
            player_id = player["person"]["id"]
            # player_id = gameObj["teams"][team_status]["players"][player]
            
            # Don't use goalies
            currPosition = player["person"]["primaryPosition"]["type"]
            if (currPosition != "Forward" or currPosition != "Defenseman"):
                continue
            
            if player_id not in team.players:
                team.players.append(player_id)
                team.player_age[player_id] = player["person"]["currentAge"]
                team.position[player_id] = currPosition

            # enter player stats (goals, assists, toi, +/-, power play points)
            skaterStats = player["stats"]["skaterStats"]

            # goals, assits, toi, +/-
            team.goals[(player_id, gameId)] = skaterStats["goals"]
            team.assists[(player_id, gameId)] = skaterStats["assists"]
            toiSplit = skaterStats["timeOnIce"].split(":")
            team.toi[(player_id, gameId)] = int(toiSplit[0]) * 60 + int(toiSplit[1])
            team.plus_minus[(player_id, gameId)] = skaterStats["plusMinus"]
            team.pow_play_points = skaterStats["powerPlayAssists"] + skaterStats["powerPlayGoals"]

def makeEntries(team):
    # Iterate from index 10 to end of team.games
    
    # For each game id
    for i, g in enumerate(team.games):
        if i < 10:
            continue
        # Create variables for (homeOrAway, WinningLosingStreak, oppId)
        homeOrAway = team.is_home[g]
        winLossStreak = team.win_loss[i]
        oppId = team.opps[g]
        avgOppGoalsAllowed, avgOppPenalties = getOpponentStats(oppId, team.season, i + 1)
        
        # For each player
        # Create variables for (avgGoals, avgAssists, avgTOI, avgPlusMinus, avgPowerPlay, ) i
        for p in team.player:
            avgGoals = team.get_last_10_average(i, lambda g_: team.goals[(p, g_)])
            if avgGoals == None:
                continue

            avgAssists = team.get_last_10_average(i, lambda g_: team.assists[(p, g_)])
            if avgAssists == None:
                continue

            avgTOI = team.get_last_10_average(i, lambda g_: team.toi[(p, g_)])
            if avgTOI == None:
                continue

            avgPlusMinus = team.get_last_10_average(i, lambda g_: team.plus_minus[(p, g_)])
            if avgPlusMinus == None:
                continue

            avgPowerPlay = team.get_last_10_average(i, lambda g_: team.assists[(p, g_)])
            if avgPowerPlay == None:
                continue

            powPlayGoalProb = avgPowerPlay * avgOppPenalties
            actualGoals = teams.goals[(p,g)]
            actualAssists = teams.assists[(p,g)]
            
            # make entry
            mongoDB.create(
                homeOrAway, 
                winLossStreak, 
                team.player_age[p],
                team.position[p],
                avgGoals, 
                avgAssists, 
                avgTOI, 
                avgPlusMinus, 
                powPlayGoalProb,
                avgOppGoalsAllowed,
                actualGoals,
                actualAssists
            )

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

def getGames(team):
    # Make API call to get schedule of given team during given season (only regular games)
    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=" + team.season + "&expand=schedule.linescore&teamId=" + str(team.id) + "&gameType=R"
    data = makeRequest(url)
    # Collect all gameIds, and update team.games
    for date in data["dates"]:
        for game in date["games"]:
            # print(game["gamePk"])
            gameId = game["gamePk"]
            team.games.append(gameId)
            
            # Check opponent id for given team.id
            team.is_home[gameId] = game["teams"]["home"]["team"]["id"] == team.id
            team_status = ""
            opp_status = ""
            if team.is_home[gameId]:
                team_status = "home"
                opp_status = "away"
            else:
                team_status = "away"
                opp_status = "home"
            
            # Check if game is win/loss for given team.id. Also, store opp_id
            did_team_win = game["teams"][team_status]["score"] > game["teams"][opp_status]["score"]
            team.opps[gameId] = game["teams"][opp_status]["team"]["id"]
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
# Notes: 
# - I ran what I have for this script so far to estimate the time needed for completion.
# - The first season took ~5.5 minutes.
# - This would mean our entire script would need AT LEAST ~115 minutes (2 hrs)
#   - (These 105 minutes are not including db entries)
seasons = generate_seasons(2000, 2023)
for season in seasons:
    teamIDs = getTeamsForThisYear(season)
    for teamID in teamIDs:
        testTeam = teamID
        team = TeamSeasonStat(teamID, season)
        getGames(team)
        storeStats(team)
        makeEntries(team)
    print("Finished season " + season)
print("done")

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)