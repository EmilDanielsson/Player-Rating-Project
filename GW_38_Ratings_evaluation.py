
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson & JakobEP

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
import statistics

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
    
with open('Json_files/KPI_tot_All_v2.json') as f:
    data_kpi = json.load(f)
    
df_KPI = pd.DataFrame(data_kpi)


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
#positions_fitting = [['LB', 'RB'], ['CB'], ['LM', 'RM'], ['CM'], ['LW', 'RW'], ['ST']]
positions_fitting = [['ST']]
#positions_fitting = [['CB']]


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
            'p_adj_succ_def_actions',
            'team_xG',
            'opponent_xG'
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
    model_coef_off, r_squared_off, list_kpi_off_fitting, model_off = ff.KPI_fitting(df_KPI_EU_train, scaler,
                                                  list_kpi_off, dep_var_off,
                                                  position, min_minutes)
    
    # Call to fitting function to find coeficient and independent variables
    dep_var_def = 'opponent_xG'
    model_coef_def, r_squared_def, list_kpi_def_fitting, model_def = ff.KPI_fitting(df_KPI_EU_train, scaler,
                                                  list_kpi_def, dep_var_def,
                                                  position, min_minutes)
    
    
    ################################################
    # - Use the coefficients from EU to compute percentiles
    #   in the PL gameweek 1-37, filtered PL training data
    "----------------------------------------------"
    
    # Filter and normalise the PL data (including GW 38)
    df_filtered_PL = pf.filter_dataframe(df_KPI_PL, position, list_kpi_all, min_minutes, 1)
    df_filtered_PL[list_kpi_all[:-2]] = scaler.fit_transform(df_filtered_PL[list_kpi_all[:-2]]) 
    
    # Seperate gameweek 38 from PL
    test_gameweek = 38
    df_PL_gameweek_38 = df_England_matches.loc[df_England_matches.gameweek == test_gameweek]
    list_gameweek_38_matchId = df_PL_gameweek_38['wyId'].unique().tolist()
    mask_last_gameweeks = df_filtered_PL.matchId.isin(list_gameweek_38_matchId)
    
    # KPIs GW 1-37
    df_KPI_PL_test = df_filtered_PL.loc[~mask_last_gameweeks]
    
    # Find test data
    X_test_off = df_KPI_PL_test[list_kpi_off_fitting[:-1]]
    X_test_def = df_KPI_PL_test[list_kpi_def_fitting[:-1]]
    
    # Add constant to test data
    X_test_off = sm.add_constant(X_test_off)
    X_test_def = sm.add_constant(X_test_def)
    
    # Loop through players in gameweek 1-37
    #for i, player in df_KPI_PL_test.iterrows():





#%%
# - Evaluate fitting
"---------------------------------------------------------------------------"

# Out of sample prediction
y_pred_off = model_off.predict(X_test_off)
y_pred_def = model_def.predict(X_test_def)



#%%
# - Plot fitted values and computed team xG-values
"---------------------------------------------------------------------------"

x_plot = np.arange(len(y_pred_off))
y_plot = df_KPI_PL_test['team_xG'].copy()
y_pred_plot = y_pred_off

y_diff = abs(y_plot - y_pred_plot)


# Create figure and axes
fig1, ax1 = plt.subplots(figsize=(12, 6))

width = 0.35  # the width of the bars

rects1 = ax1.bar(x_plot[0:30] - width/2, y_plot[0:30], width, label='xG-team actual')
rects2 = ax1.bar(x_plot[0:30] + width/2, y_pred_plot[0:30], width, label='xG-team predicted')

#plt.bar(x_plot[0:50], y_plot[0:50], color='purple', label='xG-team actual')
#plt.bar(x_plot[0:50], y_pred_plot[0:50], color='orange', label='xG-team predicted')
#ax1.plot(x_plot[0:50], y_diff[0:50], '--', color='red', label='xG-team difference')

# x and y labels
ax1.set_xlabel('matches', fontweight='bold', fontsize=20, fontproperties=serif_bold.prop)
ax1.set_ylabel('xG', fontweight='bold', fontsize=20, fontproperties=serif_bold.prop)

# Adding title and subtitle
fig1.text(0.05, 1, f"Actual and predicted xG-team values for position: {positions_fitting[0][0]} \n", fontsize=22,
             fontproperties=serif_bold.prop)
fig1.text(0.05, 1, 'First 30 matches in PL season 2017/18', fontsize=18,
             fontproperties=serif_regular.prop)

# Add legend
ax1.legend(loc='best', prop={"family": "Times New Roman", 'size': 14})

# Add grid and zorder
ax1.grid(ls="dotted", lw=0.3, color="grey", alpha=1, zorder=1)

# The tight_layout() function in pyplot module of matplotlib library is used 
# to automatically adjust subplot parameters to give specified padding.
plt.tight_layout()
plt.show()

#%%
# - Statistics
"---------------------------------------------------------------------------"

# Difference
y_diff_mean = y_diff.mean()
y_diff_var = statistics.variance(y_diff)
#y_diff_covar = statistics.covariance(y_plot, y_pred_plot)
y_diff_stdvar = statistics.stdev(y_diff)

# Actual xG-team
y_plot_mean = y_plot.mean()
y_plot_var = statistics.variance(y_plot)
y_plot_stdvar = statistics.stdev(y_plot)

# Predicted xG-team
y_pred_plot_mean = y_pred_plot.mean()
y_pred_plot_var = statistics.variance(y_pred_plot)
y_pred_plot_stdvar = statistics.stdev(y_pred_plot)


#%%
# - Print stats
"---------------------------------------------------------------------------"
print('\n')
print('=============== y_diff statistics: ================ ')
print(f"Mean: {y_diff_mean}")
print(f"Variance: {y_diff_var}")
print(f"Standard deviation: {y_diff_stdvar}")

print('\n')
print('=============== Actual xG-team statistics: ================ ')
print(f"Mean: {y_plot_mean}")
print(f"Variance: {y_plot_var}")
print(f"Standard deviation: {y_plot_stdvar}")

print('\n')
print('=============== Predicted xG-team statistics: ================ ')
print(f"Mean: {y_pred_plot_mean}")
print(f"Variance: {y_pred_plot_var}")
print(f"Standard deviation: {y_pred_plot_stdvar}")


#%%
# - Plot fitted values and computed team xGC-values
"---------------------------------------------------------------------------"

x_plot2 = np.arange(len(y_pred_def))
y_plot2 = df_KPI_PL_test['opponent_xG'].copy()
y_pred_plot2 = y_pred_def

y_diff2 = abs(y_plot2 - y_pred_plot2)

# Create figure and axes
fig2, ax2 = plt.subplots(figsize=(12, 6))

width = 0.35  # the width of the bars

rects1 = ax2.bar(x_plot2[0:30] - width/2, y_plot2[0:30], width, label='xGC-team actual')
rects2 = ax2.bar(x_plot2[0:30] + width/2, y_pred_plot2[0:30], width, label='xGC-team predicted')

#plt.bar(x_plot[0:50], y_plot[0:50], color='purple', label='xG-team actual')
#plt.bar(x_plot[0:50], y_pred_plot[0:50], color='orange', label='xG-team predicted')
#ax1.plot(x_plot[0:50], y_diff[0:50], '--', color='red', label='xG-team difference')

# x and y labels
ax2.set_xlabel('matches', fontweight='bold', fontsize=20, fontproperties=serif_bold.prop)
ax2.set_ylabel('xGC', fontweight='bold', fontsize=20, fontproperties=serif_bold.prop)

# Add legend
ax2.legend(loc='best', prop={"family": "Times New Roman", 'size': 14})

# Add grid and zorder
ax2.grid(ls="dotted", lw=0.3, color="grey", alpha=1, zorder=1)

# Adding title and subtitle
fig2.text(0.05, 1, f"Actual and predicted xGC-team values for position: {positions_fitting[0][0]} \n", fontsize=22,
             fontproperties=serif_bold.prop)
fig2.text(0.05, 1, 'First 30 matches in PL season 2017/18', fontsize=18,
             fontproperties=serif_regular.prop)

# The tight_layout() function in pyplot module of matplotlib library is used 
# to automatically adjust subplot parameters to give specified padding.
plt.tight_layout()
plt.show()

#%%
# - Statistics
"---------------------------------------------------------------------------"

# Difference
y_diff2_mean = y_diff2.mean()
y_diff2_var = statistics.variance(y_diff2)
#y_diff_covar = statistics.covariance(y_plot, y_pred_plot)
y_diff2_stdvar = statistics.stdev(y_diff2)

# Actual xGC-team
y_plot2_mean = y_plot2.mean()
y_plot2_var = statistics.variance(y_plot2)
y_plot2_stdvar = statistics.stdev(y_plot2)

# Predicted xGC-team
y_pred_plot2_mean = y_pred_plot2.mean()
y_pred_plot2_var = statistics.variance(y_pred_plot2)
y_pred_plot2_stdvar = statistics.stdev(y_pred_plot2)


#%%
# - Print stats
"---------------------------------------------------------------------------"
print('\n')
print('=============== y_diff2 statistics: ================ ')
print(f"Mean: {y_diff2_mean}")
print(f"Variance: {y_diff2_var}")
print(f"Standard deviation: {y_diff2_stdvar}")

print('\n')
print('=============== Actual xGC-team statistics: ================ ')
print(f"Mean: {y_plot2_mean}")
print(f"Variance: {y_plot2_var}")
print(f"Standard deviation: {y_plot2_stdvar}")

print('\n')
print('=============== Predicted xGC-team statistics: ================ ')
print(f"Mean: {y_pred_plot2_mean}")
print(f"Variance: {y_pred_plot2_var}")
print(f"Standard deviation: {y_pred_plot2_stdvar}")




