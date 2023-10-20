import requests

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
        self.home_or_away = {}

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

    avgGoalsAllowed = 0
    avgPenalties = 0
    
    for document in enumerate(documents):
        avgGoalsAllowed += document.goalsAllowed
        avgPenalties += documents.penalties

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
    for i in range(len(team.games)):
        gameId = team.games[i]
        # Do API call for gameId

        # Check game h/a for given team.id
        # Check if game is win/loss for given team.id
        # Check opponent id for given team.id

        # Iterate though players in roster[team.id]
        # if (player.id not in team.players)
            # Add player. Set age and position
        # enter player stats (goals, assists, toi, +/-, power play points) 

def makeEntries(team):
    # Iterate from index 10 to end of team.games
    
    # For each game id
    for i, g in enumerate(team.games):
        # Create variables for (homeOrAway, WinningLosingStreak, oppId)
        homeOrAway = team.home_or_away[g]
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
    try:
        # Send an HTTP GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Access and print the results
            teams = data["teams"]
            for team in teams:
                team_id = team["id"]
                team_name = team["name"]
                roster = team["roster"]["roster"]

                print(f"Team ID: {team_id}")
                print(f"Team Name: {team_name}")
                print("Roster:")
                for player in roster:
                    player_name = f"{player['person']['firstName']} {player['person']['lastName']}"
                    print(f"- {player_name}")

        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except KeyError:
        print("Error: JSON structure does not match expectations")
    # return array of ids
    pass

def getGames(team, season):
    # Make API call to get schedule of given team during given season (only regular games)
    # Collect all gameIds, and update team.games
    pass

# years = [20002001, ..., 20222023]
seasons = ['20142015']
for season in seasons:
    teams = getTeamsForThisYear(season)
    # for team in teams:
    #     team = TeamSeasonStat(team.id)
    #     getGames(team, season)
    #     storeStats(team)
    #     makeEntries(team)