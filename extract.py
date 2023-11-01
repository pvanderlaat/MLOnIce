import pandas as pd
import numpy as np
import mongo
import joblib

# Assuming each document is a dictionary
db = mongo.DB()
documents = list(db.find("Entries (skaterStat Fix)", {}))

# Extract relevant data from the documents and store them in a list
data_list = []
for doc in documents:
    # Example: Assuming the keys are the column names
    data = {
        'playerAge': doc.get('playerAge'), 
        'playerPosition': doc.get('playerPosition'),
        'avgGoals': doc.get('avgGoals'),
        'avgAssists': doc.get('avgAssists'),
        'avgTOI': doc.get('avgTOI'),
        'avgPlusMinus': doc.get('avgPlusMinus'),
        'powPlayGoalProb': doc.get('powPlayGoalProb'),
        'isHome': doc.get('isHome'),
        'winLossStreak': doc.get('winLossStreak'),
        'avgOppGoalsAllowed': doc.get('avgOppGoalsAllowed'),
        'actualGoals': doc.get('actualGoals'),
        'actualAssists': doc.get('actualAssists'),
    }
    data_list.append(data)

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data_list)

# Print the DataFrame and its shape
# print(df)

# joblib.dump(df, 'testDf.pkl')
df.to_csv('hockeyData.csv', index=False)