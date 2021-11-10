
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson

Program description: 
   Find ratings of all players in the last round
   
Algorithm: 
    
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
import fitting_functions as ff

# Statistical fitting of models
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import RobustScaler

# For tables
from tabulate import tabulate

# Ignore Future Warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#%%
# - Read in data KPI data
"---------------------------------------------------------------------------"



# Test to load in and store as dataframe per_90 dont have all collumns yet
# with open('Json_files/KPI_per_90_All.json') as f:
#     data_kpi = json.load(f)
    
with open('../Json_files/KPI_tot_All_v2.json') as f:
    data_kpi = json.load(f)
    
df_KPI = pd.DataFrame(data_kpi)


# Create match dataframes
df_England_matches = pd.read_json('../../Wyscout/matches/matches_England.json', encoding="unicode_escape")


#%%
# - Read in minutes played data
"---------------------------------------------------------------------------"

with open('../Json_files/minutes_played_All.json') as f:
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
# - Set filter and scaler varables
"---------------------------------------------------------------------------"

# Now we want to filter out those who have not played at least 
# 10 matches with 20 minutes in each match (can change)
min_minutes = 20

# Choose method for normalizaion
scaler = MinMaxScaler()
#scaler = preprocessing.QuantileTransformer(random_state=0)
#scaler = RobustScaler()


#%%
# - Create test and train dataset and preprocess data
"---------------------------------------------------------------------------"

# Seperate df_KPI beteween PL and the rest of the legaues
mask_PL = df_KPI.league == "England"
df_KPI_PL = df_KPI.loc[mask_PL]
df_KPI_EU_train = df_KPI.loc[~mask_PL]


#%%
# - Rank the players 
"---------------------------------------------------------------------------"

# Positions to fit for
positions_fitting = [['LB', 'RB'], ['CB'], ['LM', 'RM'], ['CM'], ['LW', 'RW'], ['ST']]

# Initiate rating and info dataframe
df_final_rating = pd.DataFrame(columns = ['matchId', 'teamName', 'playerId',
                                          'shortName', 'position', 'tot_rating',
                                          'match_events_rating', 'fitting_rating_off',
                                          'fitting_rating_def',
                                          'final_rating', 'match_info',
                                          'gameweek'])

# Initiate rating and info dataframe
df_final_rating2 = pd.DataFrame(columns = ['matchId', 'teamName', 'playerId',
                                          'shortName', 'position', 'tot_rating',
                                          'match_events_rating', 'fitting_rating_off',
                                          'fitting_rating_def',
                                          'final_rating', 'match_info',
                                          'gameweek'])


# Do fitting for all the positins
for position in positions_fitting:
    # print(position)

    ################################################
    # - Kpis to fit for
    "----------------------------------------------"
    
    list_kpi_all = ['passing%', 
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
            'red_card',
            'own_goals',
            'yellow_cards',
            'danger_ball_loses',
            'def_actions%',
            'p_adj_succ_def_actions'
            ] 
        
    # KPIs when using KPI_tot_All
    list_kpi_off = ['passing%', 
                'completed_passes',
                'fouls',
                #'aerial%',
                #'aerial_wins',
                'shots',
                'dribbles%',
                #'succesful_dribbles',
                'key_passes',
                #'succesful_through_passes',
                'events_in_box',
                'passes_to_box',
                #'creative_passes',
                #'succesful_def_actions', 
                #'progressive_carries',
                'red_card',
                'own_goals',
                'yellow_cards',
                'danger_ball_loses',
                #'def_actions%',
                'p_adj_succ_def_actions'
                ] 
    
    list_kpi_def = ['passing%', 
                'completed_passes',
                'fouls',
                #'aerial%',
                #'aerial_wins',
                #'shots',
                'dribbles%',
                #'succesful_dribbles',
                #'key_passes',
                #'succesful_through_passes',
                #'events_in_box',
                #'passes_to_box',
                #'creative_passes',
                #'succesful_def_actions',
                #'progressive_carries',
                'red_card',
                'own_goals',
                'yellow_cards',
                'danger_ball_loses',
                #'def_actions%',
                'p_adj_succ_def_actions'
                ] 

    ################################################
    # - Find model coeficients, r-squared and statisticly significant kpis
    "----------------------------------------------"
    # Call to fitting function to find coeficient and independent variables
    dep_var_off = 'team_xG'
    model_coef_off, r_squared_off, list_kpi_off_fitting = ff.KPI_fitting(df_KPI_EU_train, scaler,
                                                  list_kpi_off, dep_var_off,
                                                  position, min_minutes)
    
    # Call to fitting function to find coeficient and independent variables
    dep_var_def = 'opponent_xG'
    model_coef_def, r_squared_def, list_kpi_def_fitting = ff.KPI_fitting(df_KPI_EU_train, scaler,
                                                  list_kpi_def, dep_var_def,
                                                  position, min_minutes)
    
    
    ################################################
    # - Use the coefficients from EU to compute percentiles
    #   in the PL gameweek 1-37, filtered PL training data
    "----------------------------------------------"
    
    # Filter and normalise the PL data (including GW 38)
    df_filtered_PL = pf.filter_dataframe(df_KPI_PL, position, list_kpi_all, min_minutes, 1)
    df_filtered_PL[list_kpi_all] = scaler.fit_transform(df_filtered_PL[list_kpi_all]) 
    
    # Seperate gameweek 38 from PL
    test_gameweek = 38
    df_PL_gameweek_38 = df_England_matches.loc[df_England_matches.gameweek == test_gameweek]
    list_gameweek_38_matchId = df_PL_gameweek_38['wyId'].unique().tolist()
    mask_last_gameweeks = df_filtered_PL.matchId.isin(list_gameweek_38_matchId)
    
    # KPIs GW 1-37
    df_KPI_PL_train = df_filtered_PL.loc[~mask_last_gameweeks]
    
    # Initiate rating dataframe for GW 1-37
    df_ratings = pd.DataFrame()
    
    # Loop through players in gameweek 1-37
    for i, player in df_KPI_PL_train.iterrows():
        
        # Add some info to dataframe
        df_ratings.loc[i, 'matchId'] = player['matchId']
        df_ratings.loc[i, 'teamName'] = player['teamName']
        df_ratings.loc[i, 'playerId'] = player['playerId']
        df_ratings.loc[i, 'shortName'] = player['shortName']
        
        ################################################
        # - xG-Fit
        "----------------------------------------------"
    
        # Find the fitted xG 
        xG_fitting_rating_off = ff.compute_fitting_ratings(player, model_coef_off, list_kpi_off_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xG_fitting_rating_off = xG_fitting_rating_off * r_squared_off
        
        # Add to df
        df_ratings.loc[i, 'fitting_rating_off'] = xG_fitting_rating_off
        
        ################################################
        # - opponent_xG-Fit (xGC)
        "----------------------------------------------"
        # Find the fitted opponent xG (xGC)
        xGC_fitting_rating_def = ff.compute_fitting_ratings(player, model_coef_def, list_kpi_def_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xGC_fitting_rating_def = xGC_fitting_rating_def * r_squared_def
        
        # Add to df
        df_ratings.loc[i, 'fitting_rating_def'] = xGC_fitting_rating_def
        
        ################################################
        # - Match event-rating
        "----------------------------------------------"
        
        # Find the event rating and add to dataframe
        match_event_rating = ff.compute_events_rating(player, position, df_KPI)
        df_ratings.loc[i, 'match_events_rating'] = match_event_rating
        
        # Sum fitting rating and add to dataframe
        tot_fit_rating = xG_fitting_rating_off - xGC_fitting_rating_def
        df_ratings.loc[i, 'tot_fit_rating'] = tot_fit_rating
        
        

    # Find percentiles from the rankings in gameweek 1-37 PL 
    percentiles = np.arange(0.01, 1, 0.01)
    percentiles_fit = df_ratings['tot_fit_rating'].quantile(percentiles)
    percentiles_events = df_ratings['match_events_rating'].quantile(percentiles)
    
    ################################################
    # - Compute the rankings of gameweek 38 for the position
    "----------------------------------------------"
    # KPIs GW 38
    df_KPI_PL_gameweek_38 = df_filtered_PL.loc[mask_last_gameweeks] 
    
    # Initiate rating dataframe for GW 38
    df_ratings_test = pd.DataFrame()
    
    # Loop through players in gameweek 38
    for i, player in df_KPI_PL_gameweek_38.iterrows():
        
        # Add some info to dataframe
        df_ratings_test.loc[i, 'matchId'] = player['matchId']
        df_ratings_test.loc[i, 'teamName'] = player['teamName']
        df_ratings_test.loc[i, 'playerId'] = player['playerId']
        df_ratings_test.loc[i, 'shortName'] = player['shortName']
        
        ################################################
        # - xG-Fit
        "----------------------------------------------"
        
        # Find the fitted xG 
        xG_fitting_rating_off = ff.compute_fitting_ratings(player, model_coef_off, list_kpi_off_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xG_fitting_rating_off = xG_fitting_rating_off * r_squared_off
        
        # Add to df
        df_ratings_test.loc[i, 'fitting_rating_off'] = xG_fitting_rating_off
        
        ################################################
        # - opponent_xG-Fit (xGC)
        "----------------------------------------------"

        # Find the fitted opponent xG (xGC)
        xGC_fitting_rating_def = ff.compute_fitting_ratings(player, model_coef_def, list_kpi_def_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xGC_fitting_rating_def = xGC_fitting_rating_def * r_squared_def
        
        # Add to df
        df_ratings_test.loc[i, 'fitting_rating_def'] = xGC_fitting_rating_def
        
        ################################################
        # - Match event-rating
        "----------------------------------------------"
        
        # Find the event rating and add to dataframe
        match_event_rating = ff.compute_events_rating(player, position, df_KPI)
        df_ratings_test.loc[i, 'match_events_rating'] = match_event_rating
        
        # Sum fitting rating and add to dataframe
        tot_fit_rating = xG_fitting_rating_off - xGC_fitting_rating_def
        df_ratings_test.loc[i, 'tot_fit_rating'] = tot_fit_rating
    
    # Modify the df_rating_test dataframe and the gameweek 38 dataframe
    ff.create_rating_dataframe(df_ratings_test, df_KPI_PL, df_KPI_PL_gameweek_38,
                               percentiles_fit, percentiles_events, df_England_matches)
    
    # Modify the rating dataframe from gameweek 1-37
    ff.create_rating_dataframe(df_ratings, df_KPI, df_KPI_PL_train,
                               percentiles_fit, percentiles_events, df_England_matches)

    
    # Merge the rating dataframe GW 38
    frames = [df_final_rating, df_ratings_test]
    df_final_rating = pd.concat(frames) 
    
    # Merge the rating dataframe [GW1-37]
    frames = [df_final_rating2, df_ratings]
    df_final_rating2 = pd.concat(frames)


#%%
# Check the mean rating from gameweek 1-37
df_mean_rating = df_final_rating2.groupby(['shortName', 'teamName'], as_index=False)["final_rating"].mean()
df_sum_rating = df_final_rating2.groupby(['shortName'], as_index=False)["final_rating"].sum()

# # Save to Excel file
with pd.ExcelWriter("Gameweek_38.xlsx", mode="a", engine="openpyxl", if_sheet_exists = "new") as writer:
    df_mean_rating.to_excel(writer, sheet_name="mean_rating",
                            #columns=['shortName', 'position', 'teamName', 'final_rating'],
                    header=True, index=False)
    
# # Save to Excel file
with pd.ExcelWriter("Gameweek_38.xlsx", mode="a", engine="openpyxl", if_sheet_exists = "new") as writer:
    df_sum_rating.to_excel(writer, sheet_name="sum_rating",
                            #columns=['shortName', 'position', 'teamName', 'final_rating'],
                    header=True, index=False)

#%%
# - Print and save the ratings
"---------------------------------------------------------------------------"
# Print matches from last gameweek ratings
df_gameweek_38 = df_final_rating.loc[df_final_rating.gameweek == 38]
rated_matches = df_gameweek_38['matchId'].unique().tolist()

for match in rated_matches:
    the_match = df_final_rating.loc[df_final_rating['matchId'] == match]
    print(the_match.match_info.values[0])
    table = the_match[['teamName', 'shortName', 'position', 'final_rating']]
    print(tabulate(table))
    
# # Save to Excel file
with pd.ExcelWriter("Gameweek_38.xlsx", mode="a", engine="openpyxl", if_sheet_exists = "new") as writer:
    df_gameweek_38.to_excel(writer, sheet_name="testing_MinMax_new",
                            columns=['teamName', 'shortName', 'position', 'final_rating'],
                    header=True, index=False)








