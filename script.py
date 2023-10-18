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

from collections import deque

class Player:
    def __init__(self, id, age, position):
        self.id = id
        self.age = age
        self.position = position
        self.goals = deque()
        self.assists = deque()
        self.toi = deque()
        self.plusMin = deque()
        self.powPlayGoals = []
        self.powPlayAssits = []

class Team:
    def __init__(self):
        self.players = {}
        self.currWinLossStreak = 0
        self.prevWinLossStreak = 0
    
    def addPlayer(self, player):
        self.players[player.id] = Player(player.id, player.age, player.position)

def getOpponentStats(oppId, gameId):
    # fetch mongodb pre-processing values
    # make a call to get all game stats of oppId (start date -> 09-01-year / end date -> )

    docuements =  mongoDB.getDocument(gameId, oppId)

    # Pre-processing entry:
        # gameId
        # teamnID
        # avgGoalsAllowed
        # avgPenaltiesTaken


def makeEntry(currTeam, homeOrAway, oppAvgGoal, oppAvgPenalties):
    for player in currTeam.players:
        # player avg goal
        avgGoals = 0
        for goals in player.goals[:10]:
            avgGoals += goals
        avgGoals = avgGoals / 10
        
        # Calculate rest of values
        # Make an entry

def StoreStatsForThisYearAndTeam(gameIds, team, year):
    currTeam = Team()
    for i in range(len(gameIds)):
        gameId = gameIds[i]
        homeOrAway, oppId = updateTeamAndReturnHomeOrAway(currTeam, gameId)
        
        if (i > 10):
            oppAvgGoal, oppAvgPenalties = getOpponentStats(oppId, gameId)
            makeEntry()


# years = [20002001, ..., 20222023]
years = []
for year in years:
    teams = GetTeamsForThisYear(year)
    for team in teams:
        games = GetGamesForThisYearAndTeam(team, year)
        StoreStatsForThisYearAndTeam(games, team, year)