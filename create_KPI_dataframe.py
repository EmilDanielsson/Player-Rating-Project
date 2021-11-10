#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 16:54:33 2021

@author: emildanielsson & JakobEP

Program description: 
    1. Read in data
    2. Creates two dataframes; 
        df_KPI      - Dataframe of all the player's KPI's from each game
        df_KPI_info - Dataframe with info of player's KPI's 
    (3.) Creates and stores the two dataframes as json-files in the working directory
    
"""

# The basics
import pandas as pd
import numpy as np
import json


# Statistical fitting of models
# import statsmodels.api as sm
# import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
# from sklearn.preprocessing import PolynomialFeatures

# Import KPI-funcion
import KPI_functions as kpi


#%%
# - Create dataframes from the Wyscout data
"---------------------------------------------------------------------------"

# Create event dataframe
#df_Europe_events = pd.read_json('Json_files/events_All.json', encoding="unicode_escape") #SLOWER
with open('Json_files/events_All.json') as f:
    data_Europe= json.load(f)
    
df_Europe_events = pd.DataFrame(data_Europe)

# Create match dataframes
df_England_matches = pd.read_json('../Wyscout/matches/matches_England.json', encoding="unicode_escape")

df_France_matches = pd.read_json('../Wyscout/matches/matches_France.json', encoding="unicode_escape")

df_Germany_matches = pd.read_json('../Wyscout/matches/matches_Germany.json', encoding="unicode_escape")

df_Italy_matches = pd.read_json('../Wyscout/matches/matches_Italy.json', encoding="unicode_escape")

df_Spain_matches = pd.read_json('../Wyscout/matches/matches_Spain.json', encoding="unicode_escape")


# Create players and teams dataframes
df_players = pd.read_json("../Wyscout/players.json", encoding="unicode_escape")
df_teams = pd.read_json("../Wyscout/teams.json", encoding="unicode_escape")



#%%
# - Merge matches dataframes from all leagues 
"---------------------------------------------------------------------------"

frames_matches = [df_England_matches, df_France_matches, df_Germany_matches, 
                  df_Italy_matches, df_Spain_matches]

df_Europe_matches = pd.concat(frames_matches, keys = ["England", "France",
                                                      "Germany", "Italy", "Spain"])


#%%
# - Read in minutes played data
"---------------------------------------------------------------------------"

with open('Json_files/minutes_played_All.json') as f:
    data_minutes = json.load(f)
    
df_minutes = pd.DataFrame(data_minutes)


#%%
# - Read in data for xG-model
"---------------------------------------------------------------------------"  

with open('Json_files/xG_model_v2_All_except_Eng.json') as f:
    data_xG_model = json.load(f)

# Create dataframes
df_xG_model = pd.DataFrame(data_xG_model)  


#%%
# - Filter out headers and freekicks
"---------------------------------------------------------------------------"

mask_headers = df_xG_model.header == 1
mask_free_kicks = df_xG_model.free_kick == 1

df_xG_shots = df_xG_model[(~mask_headers) & (~mask_free_kicks)]
df_xG_headers = df_xG_model[mask_headers]
df_xG_free_kicks = df_xG_model[mask_free_kicks]


#%%
# - Split data into test and training sets, 
#   looking at distance (dist) and angle (ang) in radians. xG-shots.
"---------------------------------------------------------------------------"

df_trainSet = df_xG_shots[['goal', 'distance', 'angle_rad']].copy()

# Adding distance squared to df
squaredD = df_trainSet['distance']**2
df_trainSet = df_trainSet.assign(distance_sq = squaredD)

# y(x) where y = shot result, x1 = distance, x2 = angle
x_train, x_test, y_train, y_test = train_test_split(df_trainSet.drop('goal', axis=1), 
                                                    df_trainSet['goal'], test_size=0.20, 
                                                    random_state=10)



#%%
# - Create logistic model and fit it to data. xG-shots.
"---------------------------------------------------------------------------"

# Create instance
log_model = LogisticRegression()

# Fit model with training data
log_model.fit(x_train, y_train)

# Read out coefficent(s) into df
log_model_coef = log_model.coef_[0]

# Create df of fit
df_log_model_coef = pd.DataFrame(log_model_coef, 
             x_train.columns, 
             columns=['coef']).sort_values(by='coef', ascending=False)

# Add to df
df_log_model_coef.loc['intercept'] = log_model.intercept_[0]
print(df_log_model_coef)


#%%
# - Split data into test and training sets, 
#   looking at distance (dist) and angle (ang) in radians. xG-headers.
"---------------------------------------------------------------------------"

df_trainSet_headers = df_xG_headers[['goal', 'distance', 'angle_rad']].copy()

# Adding distance squared to df
squaredD = df_trainSet_headers['distance']**2
df_trainSet_headers = df_trainSet_headers.assign(distance_sq = squaredD)

# y(x) where y = shot result, x1 = distance, x2 = angle
x_train_h, x_test_h, y_train_h, y_test_h = train_test_split(df_trainSet_headers.drop('goal', axis=1), 
                                                    df_trainSet_headers['goal'], test_size=0.20, 
                                                    random_state=10)


#%%
# - Create logistic model and fit it to data. xG-headers.
"---------------------------------------------------------------------------"

# Create instance
log_model_headers = LogisticRegression()

# Fit model with training data
log_model_headers.fit(x_train_h, y_train_h)

# Read out coefficent(s) into df
log_model_headers_coef = log_model_headers.coef_[0]

# Create df of fit
df_log_model_headers_coef = pd.DataFrame(log_model_headers_coef, 
             x_train_h.columns, 
             columns=['coef']).sort_values(by='coef', ascending=False)

# Add to df
df_log_model_headers_coef.loc['intercept'] = log_model_headers.intercept_[0]
print(df_log_model_headers_coef)


#%%
# - Split data into test and training sets, 
#   looking at distance (dist) and angle (ang) in radians. xG-free-kicks.
"---------------------------------------------------------------------------"

df_trainSet_free_kicks = df_xG_free_kicks[['goal', 'distance', 'angle_rad']].copy()

# Adding distance squared to df
squaredD = df_trainSet_free_kicks['distance']**2
df_trainSet_free_kicks = df_trainSet_free_kicks.assign(distance_sq = squaredD)

# y(x) where y = shot result, x1 = distance, x2 = angle
x_train_f, x_test_f, y_train_f, y_test_f = train_test_split(df_trainSet_free_kicks.drop('goal', axis=1), 
                                                    df_trainSet_free_kicks['goal'], test_size=0.20, 
                                                    random_state=10)


#%%
# - Create logistic model and fit it to data. xG-free-kicks.
"---------------------------------------------------------------------------"

# Create instance
log_model_free_kicks = LogisticRegression()

# Fit model with training data
log_model_free_kicks.fit(x_train_f, y_train_f)

# Read out coefficent(s) into df
log_model_free_kicks_coef = log_model_free_kicks.coef_[0]

# Create df of fit
df_log_model_free_kicks_coef = pd.DataFrame(log_model_free_kicks_coef, 
             x_train_f.columns, 
             columns=['coef']).sort_values(by='coef', ascending=False)

# Add to df
df_log_model_free_kicks_coef.loc['intercept'] = log_model_free_kicks.intercept_[0]
print(df_log_model_free_kicks_coef)



#%%
# - Create the dataframe of all KPI's
"---------------------------------------------------------------------------"

# Prepare the dataframe with the columns we need
df_KPI_p90 = pd.DataFrame(columns=['matchId',
                                   'league',
                               'teamName',
                               'playerId',
                               'shortName',
                               'role',
                               'minutesPlayed',
                               'team_goals',
                               'team_conceded_goals',
                               'red_card',
                               # KPI's from here
                               'goals',
                               'assists',
                               'passing%',
                               'completed_passes_p90',
                               'fouls_p90',
                               'aerial%',
                               'aerial_wins_p90',
                               'shots_p90',
                               'dribbles%',
                               'succesful_dribbles_p90',
                               'key_passes_p90',
                               'succesful_through_passes_p90',
                               'plus_minus',
                               'events_in_box_p90',
                               'passes_to_box_p90',
                               'creative_passes_p90',
                               'succesful_def_actions_p90',
                               'progressive_carries_p90',
                               'xG_p90',
                               'xG_tot',
                               'xG_shots',
                               'xG_headers',
                               'xG_free_kicks',
                               'xG_penalties'])

# Prepare the dataframe with the columns we need
df_KPI_tot = pd.DataFrame(columns=['matchId',
                                   'league',
                               'teamName',
                               'playerId',
                               'shortName',
                               'role',
                               'minutesPlayed',
                               'team_goals',
                               'team_conceded_goals',
                               'red_card',
                               # KPI's from here
                               'goals',
                               'assists',
                               'passing%',
                               'completed_passes',
                               'fouls',
                               'aerial%',
                               'aerial_wins',
                               'shots',
                               'dribbles%',
                               'succesful_dribbles',
                               'key_passes',
                               'succesful_through_passes',
                               'plus_minus',
                               'events_in_box',
                               'passes_to_box',
                               'creative_passes',
                               'succesful_def_actions',
                               'progressive_carries',
                               'xG_tot',
                               'xG_shots',
                               'xG_headers',
                               'xG_free_kicks',
                               'xG_penalties'])

# Prepare the dataframe with the columns we need
df_KPI_info = pd.DataFrame(columns=['matchId',
                                    'league',
                               'playerId',
                               'shortName',                              
                               # KPI-info's from here
                               'info_goals',
                               'info_assists',
                               'info_passing%',
                               'info_completed_passes',
                               'info_fouls',
                               'info_aerial%',
                               'info_aerial_wins',
                               'info_shots',
                               'info_dribbles%',
                               'info_succesful_dribbles',
                               'info_key_passes',
                               'info_succesful_through_passes',
                               'info_plus_minus',
                               'info_events_in_box',
                               'info_passes_to_box',
                               'info_creative_passes',
                               'info_succesful_def_actions',
                               'info_progressive_carries',
                               'info_xG'])


# Match id checkpoints
loop_checkpoints = np.arange(0, 2100, 5)
j = 0

# Loop trough all matches
for i, match in df_Europe_matches.iterrows():
    
    # Find the events from match_i
    mask_match = df_Europe_events.matchId == match.wyId
    df_events_match = df_Europe_events.loc[mask_match]
    
    # List of all the players involved in match_i
    player_match_list = df_events_match['playerId'].unique().tolist()
    
    ################################################
    # - Find home and away score
    "----------------------------------------------"
    
    # Find teamIds in the match
    teams_match_list = df_events_match['teamId'].unique().tolist()
    
    # Find the match data from df_matches
    mask_score = df_Europe_matches.wyId == match.wyId
    df_the_match = df_Europe_matches.loc[mask_score]
    team_data = df_the_match.teamsData
    
    ################################################
    # - Get home and away teams and scores
    "----------------------------------------------"
    home_team_list = []
    away_team_list = []
    for i in range(2):
        team_data_i = team_data[0][str(teams_match_list[i])]
        team_lineup = team_data_i['formation']['lineup']
        team_bench = team_data_i['formation']['bench']
        
        # Get the lineup players
        for player in team_lineup:
            if team_data_i['side'] == "home":
                home_team_list.append(player['playerId'])
            elif team_data_i['side'] == "away":
                away_team_list.append(player['playerId'])
            else:
                print("Error: " + team_data_i['side'])
        
        # Get the bench players
        for player in team_bench:
            if team_data_i['side'] == "home":
                home_team_list.append(player['playerId'])
            elif team_data_i['side'] == "away":
                away_team_list.append(player['playerId'])
            else:
                print("Error: " + team_data_i['side'])
                
        # Set home and away score
        if team_data_i['side'] == "home":
            home_team_score = team_data_i['score']
        elif team_data_i['side'] == "away":
            away_team_score = team_data_i['score']
        else:
            print("Error: " + team_data_i['score'])
                    
    # End of finding home and away teams and score
    "----------------------------------------------"

    
    # Loop trough all players and get their average position and compute KPI's
    for player in player_match_list:
        
        # Find the minutes played, team and red card
        mask_minutes = (df_minutes.playerId == player) & (df_minutes.matchId == match.wyId)
        df_player_minutes = df_minutes.loc[mask_minutes]
        
        # Some players are not registered the subbed in but their events are registerd
        # If they are not subbed in correctly in Wyscout matches "df_player_minutes"
        # will be empty. Thus we check this here. 
        if len(df_player_minutes != 0):
            player_minutes = df_player_minutes['minutesPlayed'][0]
            player_in_min = df_player_minutes['player_in_min'][0]
            player_out_min = df_player_minutes['player_out_min'][0]
            player_team = df_player_minutes['teamId'][0]
            player_team_name = df_player_minutes['teamName'][0]
            red_card_bool = df_player_minutes['red_card'][0]
            
            # mask to find the given player-events
            mask_player = df_events_match.playerId == player
            
            # New dataframe with all events from 'player' in match
            df_events_player = df_events_match.loc[mask_player]
            
            # Get the role of the player
            position = df_events_player['Position'][0]
            
            # Get the league
            league = df_events_player["league"][0]
            
            # Get the shortName
            name = df_events_player['shortName'][0]
            
            # Get the team goal and goals conceded
            if (player in home_team_list):
                team_goals = home_team_score
                team_conceded_goals = away_team_score
            elif (player in away_team_list):
                team_goals = away_team_score
                team_conceded_goals = home_team_score
            else:
                print("Error: cant find player in list")
            
            
            ################################################
            # - All function calls to compute kpi's
            "----------------------------------------------"
            
            # goals
            goals, goals_info = kpi.nr_goals(df_events_player, player_minutes)
            
            # assists
            assists, assists_info = kpi.nr_assists(df_events_player, player_minutes)
            
            # passing%
            pass_percent, pass_percent_info = kpi.percent_passes_completed(df_events_player, player_minutes)
            
            # passes_completed
            pass_comp, pass_comp_p90, pass_comp_info = kpi.passes_completed(df_events_player, player_minutes)
            
            # fouls
            fouls, fouls_p90, fouls_info = kpi.fouls(df_events_player, player_minutes)
            
            # aerials%
            aerials_percent, aerials_percent_info = kpi.percent_aerial_wins(df_events_player, player_minutes)
            
            # aerials_won
            aerial_wins, aerial_wins_p90, aerial_wins_info = kpi.aerials_won(df_events_player, player_minutes)
            
            # shots
            shots, shots_p90, shots_info = kpi.shots(df_events_player, player_minutes)
            
            # dribbles%
            dribbles_percent, dribbles_percent_info = kpi.percent_succesful_dribbles(df_events_player, player_minutes)
            
            # succesful_dribbles
            succesful_dribbles, succesful_dribbles_p90, succesful_dribbles_info = kpi.succesful_dribbles(df_events_player, player_minutes)
            
            # key_passes
            key_passes, key_passes_p90, key_passes_info = kpi.key_passes(df_events_player, player_minutes)
            
            # succesful_through_passes
            succesful_through_passes, succesful_through_passes_p90, succesful_through_passes_info = kpi.succesful_through_passes(df_events_player, player_minutes)
            
            # plus-minus
            plus_minus, plus_minus_info = kpi.plus_minus(df_events_match, player_team, player_minutes, player_in_min, player_out_min)
            
            # events_in_box
            events_in_box, events_in_box_p90, event_in_box_info = kpi.events_in_box(df_events_player, player_minutes)
            
            # passes_to_box
            passes_to_box, passes_to_box_p90, passes_to_box_info = kpi.passes_to_box(df_events_player, player_minutes)
            
            # creative_passes
            creative_passes, creative_passes_p90, creative_passes_info = kpi.creative_passes(df_events_player, player_minutes)
            
            # defensive_actions
            succesful_def_actions, succesful_def_actions_p90, succesful_def_actions_info = kpi.succesful_def_actions(df_events_player, player_minutes)
            
            # progressive_carries 
            progressive_carries, progressive_carries_p90, progressive_carries_info = kpi.progressive_carries(df_events_player, player_minutes) 
            
            # xG
            xG_tot, xG_tot_p90, xG_info, xG_shots, xG_headers, xG_free_kicks, xG_penalties = kpi.xG(df_events_player, player_minutes, df_log_model_coef, df_log_model_headers_coef, df_log_model_free_kicks_coef)
            
            
            
            ########################################################
            # - Add rows to df_KPI_p90, df_KPI_tot and df_KPI_info
            "------------------------------------------------------"
            
            # df_KPI_p90
            df_KPI_p90.loc[df_KPI_p90.shape[0]] = [match.wyId, league, player_team_name, player, name,
                                           position, player_minutes, team_goals, 
                                           team_conceded_goals, red_card_bool,
                                           goals,
                                           assists,
                                           pass_percent,
                                           pass_comp_p90,
                                           fouls_p90,
                                           aerials_percent,
                                           aerial_wins_p90,
                                           shots_p90,
                                           dribbles_percent,
                                           succesful_dribbles_p90,
                                           key_passes_p90,
                                           succesful_through_passes_p90,
                                           plus_minus,
                                           events_in_box_p90,
                                           passes_to_box_p90,
                                           creative_passes_p90,
                                           succesful_def_actions_p90,
                                           progressive_carries_p90,
                                           xG_tot_p90,
                                           xG_tot,
                                           xG_shots,
                                           xG_headers,
                                           xG_free_kicks,
                                           xG_penalties]
            
            # df_KPI_tot
            df_KPI_tot.loc[df_KPI_tot.shape[0]] = [match.wyId, league, player_team_name, player, name,
                                           position, player_minutes, team_goals, 
                                           team_conceded_goals, red_card_bool,
                                           goals,
                                           assists,
                                           pass_percent,
                                           pass_comp,
                                           fouls,
                                           aerials_percent,
                                           aerial_wins,
                                           shots,
                                           dribbles_percent,
                                           succesful_dribbles,
                                           key_passes,
                                           succesful_through_passes,
                                           plus_minus,
                                           events_in_box,
                                           passes_to_box,
                                           creative_passes,
                                           succesful_def_actions,
                                           progressive_carries,
                                           xG_tot,
                                           xG_shots,
                                           xG_headers,
                                           xG_free_kicks,
                                           xG_penalties]
            
            
            # df_KPI_info
            df_KPI_info.loc[df_KPI_info.shape[0]] = [match.wyId, league, player, name,
                                                      goals_info,
                                                      assists_info,
                                                      pass_percent_info,
                                                      pass_comp_info,
                                                      fouls_info,
                                                      aerials_percent_info,
                                                      aerial_wins_info,
                                                      shots_info,
                                                      dribbles_percent_info,
                                                      succesful_dribbles_info,
                                                      key_passes_info,
                                                      succesful_through_passes_info,
                                                      plus_minus_info,
                                                      event_in_box_info,
                                                      passes_to_box_info,
                                                      creative_passes_info,
                                                      succesful_def_actions_info,
                                                      progressive_carries_info,
                                                      xG_info]
        
        
    if (j in loop_checkpoints):
        print(f"Number of matches with computed KPI's': {j}\n")

    j+=1


# - Save dataframes to json-files
"---------------------------------------------------------------------------" 
df_KPI_p90.to_json("Json_files/KPI_per_90_All.json")
df_KPI_tot.to_json("Json_files/KPI_tot_All.json")
df_KPI_info.to_json("Json_files/KPI_info_All.json")

        
#%%        
        