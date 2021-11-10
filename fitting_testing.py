
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson

Program description: 
   Teting some fitting of KPIs and xG
"""


# The basics
import pandas as pd
import numpy as np
import json

# Plotting
import matplotlib.pyplot as plt
from mplsoccer import FontManager

# Import other functions
import percentile_functions as pf

# Statistical fitting of models
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import preprocessing


#%%
# - Read in data KPI data
"---------------------------------------------------------------------------"

# Test to load in and store as dataframe
with open('Json_files/KPI_tot_All.json') as f:
    data_kpi = json.load(f)
    
df_KPI_test = pd.DataFrame(data_kpi)


# Create match dataframes
df_England_matches = pd.read_json('../Wyscout/matches/matches_England.json', encoding="unicode_escape")


#%%
# - Read in minutes played data
"---------------------------------------------------------------------------"

with open('Json_files/minutes_played_All.json') as f:
    data_minutes = json.load(f)
    
df_minutes = pd.DataFrame(data_minutes)


################################################
# - Load Fonts
"----------------------------------------------"

URL1 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/'
        'fonts/SourceSerifPro-Regular.ttf?raw=true')
serif_regular = FontManager(URL1)
URL2 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/'
        'fonts/SourceSerifPro-ExtraLight.ttf?raw=true')
serif_extra_light = FontManager(URL2)
URL3 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/fonts/'
        'SourceSerifPro-Bold.ttf?raw=true')
serif_bold = FontManager(URL3)


#%%
# - Create the new column team_xG_p90, opponents_xG
"---------------------------------------------------------------------------"
# Find all unique matches 
list_matches = df_KPI_test["matchId"].unique().tolist()

for match in list_matches:
    
    # mask for the match to add team_xG 
    mask_match = df_KPI_test.matchId == match
    df_match = df_KPI_test.loc[mask_match]
    
    # List of the team names
    list_teams = df_match["teamName"].unique().tolist()
    
    for team in list_teams:
        
        # Find the team KPI
        mask_team = df_match.teamName == team
        df_team = df_match.loc[mask_team]
        df_opponent = df_match.loc[~mask_team]
        
        # Find xG and shots
        team_shots = df_team['shots'].sum()
        opponent_shots = df_opponent['shots'].sum()
        team_xG = df_team["xG_tot"].sum()
        opponent_xG = df_opponent["xG_tot"].sum()
        
        # Add to the KPI dataframe
        mask_add_xG = ((df_KPI_test.matchId == match) & (df_KPI_test.teamName == team))
        df_KPI_test.loc[mask_add_xG, 'team_xG'] = team_xG
        df_KPI_test.loc[mask_add_xG, 'opponent_xG'] = opponent_xG
        df_KPI_test.loc[mask_add_xG, 'team_shots'] = team_shots
        df_KPI_test.loc[mask_add_xG, 'opponent_shots'] = opponent_shots
        

# Find the best teams that season
# teams_xG_Europe = df_KPI.groupby("teamName")["xG"].sum() # First way of doing it 

df_teams_xG = df_KPI_test.groupby(['teamName', 'matchId'], as_index = False)['team_xG'].median()
df_teams_opponent_xG = df_KPI_test.groupby(['teamName', 'matchId'], as_index = False)['opponent_xG'].median()
teams_xG = df_teams_xG.groupby('teamName')["team_xG"].sum()
teams_xGC = df_teams_opponent_xG.groupby('teamName')["opponent_xG"].sum()

# Seperate df_KPI beteween PL and the rest of the legaues
mask_PL = df_KPI_test.league == "England"
df_KPI_PL = df_KPI_test.loc[mask_PL]
df_KPI_EU = df_KPI_test.loc[~mask_PL]

#%%
# - Set filter varables
"---------------------------------------------------------------------------"

# List the kpi´s to compute  
list_kpi = ['passing%', 
            'completed_passes',
            'fouls',
            'aerial%',
            'aerial_wins',
            'shots',
            'dribbles%',
            'succesful_dribbles',
            'key_passes',
            'succesful_through_passes',
            'events_in_box',
            'passes_to_box',
            'creative_passes',
            'succesful_def_actions',
            'progressive_carries',
            'opponent_xG'] # Change to xG_p90

# Now we want to filter out those who have not played at least 
# 10 matches with 20 minutes in each match (can change)
min_minutes = 20
min_matches = 10


#%%
# - Rating model for strikers
"---------------------------------------------------------------------------"
list_kpi_off = ['passing%',
                                #'completed_passes',
                               #'fouls',
                               #'aerial%',
                               #'aerial_wins',
                               'shots',
                               #'dribbles%',
                               #'succesful_dribbles',
                               'key_passes',
                               #'succesful_through_passes',
                               'events_in_box',
                               'passes_to_box',
                               #'creative_passes',
                               #'succesful_def_actions',
                               #'progressive_carries',
                               'xG_tot',
                               'team_xG']

# Filter the data
df_filtered_PL_ST = pf.filter_dataframe(df_KPI_PL, ["ST"], list_kpi_off, min_minutes, 1)

df_filtered_EU_ST = pf.filter_dataframe(df_KPI_EU, ["ST"], list_kpi_off, min_minutes, min_matches)

# Linear regression model 
X = df_filtered_EU_ST[list_kpi_off[:-2]]
X = sm.add_constant(X)
y = df_filtered_EU_ST['team_xG']
test_model = sm.OLS(y, X).fit()
print(test_model.summary())        
model_coef = test_model.params

df_ratings_ST = pd.DataFrame(columns=['matchId',
                               'teamName',
                               'playerId',
                               'shortName',
                               'rating',
                               #'xG_tot'
                               ])

for i, player in df_filtered_PL_ST.iterrows():
    df_ratings_ST.loc[i, 'matchId'] = player['matchId']
    df_ratings_ST.loc[i, 'teamName'] = player['teamName']
    df_ratings_ST.loc[i, 'playerId'] = player['playerId']
    df_ratings_ST.loc[i, 'shortName'] = player['shortName']
    #df_ratings_ST.loc[i, 'xG_tot'] = player['xG_tot']
    
    xG_player = 0
    for kpi in list_kpi_off[:-2]:
        xG_player += (model_coef[kpi] * player[kpi])
                      
    xG_player += model_coef['const']   
    df_ratings_ST.loc[i, 'rating'] = xG_player
    
# Sum all the ratings
sum_ratings_ST = df_ratings_ST.groupby(['shortName'])['rating'].sum()

percentiles = np.arange(0.05, 1, .1)
percentiles_ST = df_ratings_ST['rating'].quantile(percentiles)


#%%
# - Rating model LW and RW
"---------------------------------------------------------------------------"
list_kpi_LW_RW = ['passing%',
                               #'completed_passes',
                               #'fouls',
                               #'aerial%',
                               # 'aerial_wins',
                               # 'shots',
                               'dribbles%',
                               #'succesful_dribbles',
                               'key_passes',
                               # 'succesful_through_passes',
                               'events_in_box',
                               'passes_to_box',
                               #'creative_passes',
                               #'succesful_def_actions',
                               #'progressive_carries',
                               'team_xG']

# Filter the data
df_filtered_PL_LW_RW = pf.filter_dataframe(df_KPI_PL, ["RW", "LW"], list_kpi_LW_RW, min_minutes, 1)

df_filtered_EU_LW_RW = pf.filter_dataframe(df_KPI_EU, ["RW", "LW"], list_kpi_LW_RW, min_minutes, min_matches)

# Linear regression model 
X = df_filtered_EU_LW_RW[list_kpi_LW_RW[:-1]]
X = sm.add_constant(X)
y = df_filtered_EU_LW_RW['team_xG']
test_model = sm.OLS(y, X).fit()
print(test_model.summary())        
model_coef = test_model.params

df_ratings_LW_RW = pd.DataFrame(columns=['matchId',
                               'teamName',
                               'playerId',
                               'shortName',
                               'rating',
                               #'xG_tot'
                               ])

for i, player in df_filtered_EU_LW_RW.iterrows():
    df_ratings_LW_RW.loc[i, 'matchId'] = player['matchId']
    df_ratings_LW_RW.loc[i, 'teamName'] = player['teamName']
    df_ratings_LW_RW.loc[i, 'playerId'] = player['playerId']
    df_ratings_LW_RW.loc[i, 'shortName'] = player['shortName']
    #df_ratings_ST.loc[i, 'xG_tot'] = player['xG_tot']
    
    xG_player = 0
    for kpi in list_kpi_LW_RW[:-1]:
        xG_player += (model_coef[kpi] * player[kpi])
                      
    xG_player += model_coef['const']   
    df_ratings_LW_RW.loc[i, 'rating'] = xG_player
    
# Sum all the ratings
sum_ratings_LW_RW = df_ratings_LW_RW.groupby(['shortName'])['rating'].sum()

percentiles = np.arange(0.05, 1, .1)
percentiles_LW_RW = df_ratings_LW_RW['rating'].quantile(percentiles)


#%%
# - Rating model LM and RM
"---------------------------------------------------------------------------"
# List the kpi´s to compute  
list_kpi_LM_RM = ['passing%', 
            #'completed_passes',
            #'fouls',
            #'aerial%',
            #'aerial_wins',
            'shots',
            #'dribbles%',
            #'succesful_dribbles', # negative
            'key_passes',
            #'succesful_through_passes',
            'events_in_box',
            'passes_to_box',
            #'creative_passes',
            #'succesful_def_actions',
            #'progressive_carries',
            'team_xG']

# Filter the data
df_filtered_PL_LM_RM = pf.filter_dataframe(df_KPI_PL, ["RM", "LM"], list_kpi_LM_RM, min_minutes, 1)

df_filtered_EU_LM_RM = pf.filter_dataframe(df_KPI_EU, ["RM", "LM"], list_kpi_LM_RM, min_minutes, min_matches)

# Linear regression model 
X = df_filtered_EU_LM_RM[list_kpi_LM_RM[:-1]]
X = sm.add_constant(X)
y = df_filtered_EU_LM_RM['team_xG']
test_model = sm.OLS(y, X).fit()
print(test_model.summary())        
model_coef = test_model.params

df_ratings_LM_RM = pd.DataFrame(columns=['matchId',
                               'teamName',
                               'playerId',
                               'shortName',
                               'rating',
                               #'xG_tot'
                               ])

for i, player in df_filtered_PL_LM_RM.iterrows():
    df_ratings_LM_RM.loc[i, 'matchId'] = player['matchId']
    df_ratings_LM_RM.loc[i, 'teamName'] = player['teamName']
    df_ratings_LM_RM.loc[i, 'playerId'] = player['playerId']
    df_ratings_LM_RM.loc[i, 'shortName'] = player['shortName']
    #df_ratings_ST.loc[i, 'xG_tot'] = player['xG_tot']
    
    xG_player = 0
    for kpi in list_kpi_LM_RM[:-1]:
        xG_player += (model_coef[kpi] * player[kpi])
                      
    xG_player += model_coef['const']   
    df_ratings_LM_RM.loc[i, 'rating'] = xG_player
    
# Sum all the ratings
sum_ratings_LM_RM = df_ratings_LM_RM.groupby(['shortName'])['rating'].sum()

percentiles = np.arange(0.05, 1, .1)
percentiles_LM_RM = df_ratings_LM_RM['rating'].quantile(percentiles)


#%%
# - Rating model LM, RM, LW, RW (wingers)
"---------------------------------------------------------------------------"
# List the kpi´s to compute  
list_kpi_wingers = ['passing%', 
            #'completed_passes',
            #'fouls',
            #'aerial%',
            #'aerial_wins',
            'shots',
            #'dribbles%',
            # 'succesful_dribbles', # negative
            'key_passes',
            #'succesful_through_passes',
            'events_in_box',
            'passes_to_box',
            #'creative_passes',
            #'succesful_def_actions',
            #'progressive_carries',
            'team_xG']

# Filter the data
df_filtered_PL_Winger = pf.filter_dataframe(df_KPI_PL, ["RW", "LW", 'LM', 'RM'], list_kpi_wingers, min_minutes, 1)

df_filtered_EU_Winger = pf.filter_dataframe(df_KPI_EU, ["RW", "LW", 'LM', 'RM'], list_kpi_wingers, min_minutes, min_matches)

# Linear regression model 
X = df_filtered_EU_Winger[list_kpi_wingers[:-1]]
X = sm.add_constant(X)
y = df_filtered_EU_Winger['team_xG']
test_model = sm.OLS(y, X).fit()
print(test_model.summary())        
model_coef = test_model.params

df_ratings_Winger = pd.DataFrame(columns=['matchId',
                               'teamName',
                               'playerId',
                               'shortName',
                               'rating',
                               #'xG_tot'
                               ])

for i, player in df_filtered_PL_Winger.iterrows():
    df_ratings_Winger.loc[i, 'matchId'] = player['matchId']
    df_ratings_Winger.loc[i, 'teamName'] = player['teamName']
    df_ratings_Winger.loc[i, 'playerId'] = player['playerId']
    df_ratings_Winger.loc[i, 'shortName'] = player['shortName']
    df_ratings_Winger.loc[i, 'passing%'] = player['passing%']
    #df_ratings_ST.loc[i, 'xG_tot'] = player['xG_tot']
    
    xG_player = 0
    for kpi in list_kpi_wingers[:-1]:
        xG_player += (model_coef[kpi] * player[kpi])
                      
    xG_player += model_coef['const']   
    df_ratings_Winger.loc[i, 'rating'] = xG_player
    
# Sum all the ratings
sum_ratings_Winger = df_ratings_Winger.groupby(['shortName'])['rating'].sum()

percentiles = np.arange(0.05, 1, .1)
percentiles_Winger = df_ratings_Winger['rating'].quantile(percentiles)

#%%
# - Rating model for defenders
"---------------------------------------------------------------------------"
list_kpi_def = ['completed_passes',
                               'aerial_wins',
                               'succesful_def_actions',
                               'opponent_xG']

# Filter the data
df_filtered_PL_CB = pf.filter_dataframe(df_KPI_PL, ["CB"], list_kpi_def, min_minutes, min_matches)

df_filtered_EU_CB = pf.filter_dataframe(df_KPI_EU, ["CB"], list_kpi_def, min_minutes, min_matches)

# Linear regression model 
X = df_filtered_EU_CB[list_kpi_def[:-1]]
X = sm.add_constant(X)
y = df_filtered_EU_CB['opponent_xG']
test_model = sm.OLS(y, X).fit()
print(test_model.summary())        
model_coef = test_model.params

df_ratings_CB = pd.DataFrame(columns=['matchId',
                               'teamName',
                               'playerId',
                               'shortName',
                               'rating'])

for i, player in df_filtered_PL_CB.iterrows():
    df_ratings_CB.loc[i, 'matchId'] = player['matchId']
    df_ratings_CB.loc[i, 'teamName'] = player['teamName']
    df_ratings_CB.loc[i, 'playerId'] = player['playerId']
    df_ratings_CB.loc[i, 'shortName'] = player['shortName']
    
    xG_player = 0
    for kpi in list_kpi_def[:-1]:
        xG_player += (model_coef[kpi] * player[kpi])
                      
    xG_player += model_coef['const']   
    df_ratings_CB.loc[i, 'rating'] = xG_player

df_sum_ratings_CB = df_ratings_CB.groupby(['shortName'])['rating'].sum()

percentiles = np.arange(0.05, 1, .1)
percentiles_CB = df_ratings_CB['rating'].quantile(percentiles)








