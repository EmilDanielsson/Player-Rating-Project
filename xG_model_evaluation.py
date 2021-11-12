#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 14:42:31 2021

@author: JakobEP

Program description:
    
    Evaluating and validating created xG-models with test-data.

"""

#%%
# - Imports used
"---------------------------------------------------------------------------"

# Basics
import pandas as pd
import numpy as np
import json

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from mplsoccer import FontManager

# Import other functions
import percentile_functions as pf
import fitting_functions as ff
import KPI_functions as kpi
import FCPython 

# Statistical fitting of models
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

# For tables
#from tabulate import tabulate

#%%
# - Plot settings
"---------------------------------------------------------------------------"

# Read in fonts
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
# - Create dataframes from the Wyscout data, uncomment if needed
"---------------------------------------------------------------------------"

"""

# Create event dataframe
with open('Json_files/events_All.json') as f:
    data_Europe = json.load(f)
    
df_Europe_events = pd.DataFrame(data_Europe)


# Filter out events for England
df_PL_events = df_Europe_events[df_Europe_events.league == 'England']

# Save as .json-file (so it can be read in directly in the future)
df_PL_events.to_json("Json_files/events_PL.json")

"""

#%%
# - Read in event data for PL
"---------------------------------------------------------------------------" 
"""
# Create event dataframe
with open('Json_files/events_PL.json') as f:
    data_PL = json.load(f)
    
df_PL_events = pd.DataFrame(data_PL)

"""

#%%
# - Read in data for xG-model
"---------------------------------------------------------------------------"  

with open('Json_files/xG_model_v2_All_except_Eng.json') as f:
    data_xG_model_All = json.load(f)
    
    
with open('Json_files/xG_model_v2_England_only.json') as f:
    data_xG_model_PL = json.load(f)


# Create dataframes
df_All_xG_model = pd.DataFrame(data_xG_model_All)  
df_PL_xG_model = pd.DataFrame(data_xG_model_PL)


#%%
# - Get the coeficients dataframes
"---------------------------------------------------------------------------"

# Call xG-m function
df_log_model_shots_coef, df_log_model_headers_coef, df_log_model_free_kicks_coef, log_model_shots, log_model_headers, log_model_free_kicks = ff.xG_model(df_All_xG_model)


#%%
# - Print out fitting results
"---------------------------------------------------------------------------"

#print("\n=============== xG-model shots  ======================")

#print(log_model_shots)


#%%
# - Filter out headers and freekicks for PL data
"---------------------------------------------------------------------------"

mask_headers = df_PL_xG_model.header == 1
mask_free_kicks = df_PL_xG_model.free_kick == 1

df_xG_shots = df_PL_xG_model[(~mask_headers) & (~mask_free_kicks)]
df_xG_headers = df_PL_xG_model[mask_headers]
df_xG_free_kicks = df_PL_xG_model[mask_free_kicks]


#%%
# - Split data - PL
"---------------------------------------------------------------------------" 

x_testSet = df_xG_shots[['distance', 'angle_rad']].copy()     # change df
y_testSet = df_xG_shots[['goal']].copy()                      # change df
    
# Adding distance squared to df
squaredD = x_testSet['distance']**2
x_testSet = x_testSet.assign(distance_sq = squaredD)

# y(x) where y = shot result, x1 = distance, x2 = angle
#x_train, x_test, y_train, y_test = train_test_split(df_trainSet.drop('goal', axis=1), 
#                                                    df_trainSet['goal'], test_size=0.99, 
#                                                    random_state=10)


#%%
# - Make predictions - PL
"---------------------------------------------------------------------------" 

# Find prediciton probabilities
y_pred_prob = log_model_shots.predict_proba(x_testSet)         # change model

# Specify thresholds
threshold5 = [0.5]
threshold4 = [0.4]
threshold2 = [0.2]
threshold05 = [0.05]

# Final predicitons
#y_pred = y_pred_prob[y_pred_prob[:, 1] > threshold]

y_pred5 = (y_pred_prob[:, 1] > threshold5).astype('float')
y_pred2 = (y_pred_prob[:, 1] > threshold2).astype('float')
y_pred05 = (y_pred_prob[:, 1] > threshold05).astype('float')
y_pred4 = (y_pred_prob[:, 1] > threshold4).astype('float')

y_pred = (y_pred_prob[:, 1] > threshold4).astype('float')          # change

# Get confusion matrix
cnf_matrix5 = metrics.confusion_matrix(y_testSet, y_pred5)
cnf_matrix2 = metrics.confusion_matrix(y_testSet, y_pred2)
cnf_matrix05 = metrics.confusion_matrix(y_testSet, y_pred05)
cnf_matrix4 = metrics.confusion_matrix(y_testSet, y_pred4)

#%%
# - Visualize the confusion matrix using Heatmap - PL
"---------------------------------------------------------------------------"

class_names = [0, 1] # name  of classes

fig, ax = plt.subplots(figsize=(8, 6))
tick_marks = np.arange(len(class_names))
plt.xticks(tick_marks, class_names)
plt.yticks(tick_marks, class_names)

# create heatmap
sns.heatmap(pd.DataFrame(cnf_matrix4), annot=True, annot_kws={"size": 14},                                                                  # change
            cmap="Oranges", fmt='g', cbar=False, linewidths=2, linecolor='orange')
ax.xaxis.set_label_position("top")
plt.tight_layout()
plt.title(f'Confusion matrix for Threshold: {threshold4[0]}', y=1.1, fontweight='bold', fontsize=20, fontproperties=serif_regular.prop)     # change
plt.ylabel('Actual label', fontweight='bold', fontsize=18, fontproperties=serif_regular.prop)
plt.xlabel('Predicted label', fontweight='bold', fontsize=18, fontproperties=serif_regular.prop)

# Set ticks size
plt.xticks(fontsize=14, fontweight='bold', fontproperties=serif_regular.prop)
plt.yticks(fontsize=14, fontweight='bold', fontproperties=serif_regular.prop)


#%%
# - Print stats - PL
"---------------------------------------------------------------------------"

"""Recall - describes how big proportion among the true positive points that are predicted as positive. A high recall
(close to 1) is good, and a low recall (close to 0) indicates a problem with false negatives. 

Precision - describes what the ratio of true positive points are among the ones predicted as positive. A high precision
(close to 1) is good, and a low recall (close to 0) indicates a problem with false positives."""


cm_5 = confusion_matrix(y_testSet, y_pred5)
cm_2 = confusion_matrix(y_testSet, y_pred2)
cm_05 = confusion_matrix(y_testSet, y_pred05)
cm_4 = confusion_matrix(y_testSet, y_pred4)

#sensitivity = the ability of the model to correctly identify shots that resulted in a goal.
sensitivity_5 = cm_5[1][1]/(cm_5[1][1] + cm_5[1][0])
sensitivity_2 = cm_2[1][1]/(cm_2[1][1] + cm_2[1][0])
sensitivity_05 = cm_05[1][1]/(cm_05[1][1] + cm_05[1][0])
sensitivity_4 = cm_4[1][1]/(cm_4[1][1] + cm_4[1][0])

#the ability of the model to correctly identify shots that did not result in a goal
specificity_5 = cm_5[0][0]/(cm_5[0][1]+  cm_5[0][0])
specificity_2 = cm_2[0][0]/(cm_2[0][1]+  cm_2[0][0])
specificity_05 = cm_05[0][0]/(cm_05[0][1]+  cm_05[0][0])
specificity_4 = cm_4[0][0]/(cm_4[0][1]+  cm_4[0][0])

print("\n=============== xG-model performance  ======================")

print("Accuracy:", metrics.accuracy_score(y_testSet, y_pred))
print("Precision:", metrics.precision_score(y_testSet, y_pred))
print("Recall:", metrics.recall_score(y_testSet, y_pred))

print('sensitivity = ' + str(sensitivity_4))                                                   # change
print('specificity = '+ str(specificity_4) )                                                   # change

print("R-sq. score:", metrics.r2_score(y_testSet, y_pred, sample_weight=None, multioutput='uniform_average'))

# OR
"""

cm_display = ConfusionMatrixDisplay(cm_dis_3).plot(cmap='OrRd')
cm_display.im_.colorbar.remove()
plt.title('Confusion Matrix for Threshold = 0.3')
"""

#%%
# - Plot ROC-curve - PL
"---------------------------------------------------------------------------"

from sklearn.metrics import roc_curve

fig, axes = plt.subplots(figsize=(11, 7))
y_score = log_model_shots.decision_function(x_testSet)                                    # change model
fpr, tpr, _  = roc_curve(y_testSet, y_score, pos_label=log_model_shots.classes_[1])       # change model
plt.plot(fpr,tpr, label='ROC for xG-model shots')

plt.scatter(1 - specificity_5, sensitivity_5, c='orange', s=100, label='Threshold = 0.5')
plt.scatter(1 - specificity_2, sensitivity_2, c='red', s=100, label='Threshold = 0.2')
plt.scatter(1 - specificity_05, sensitivity_05, c='green', s=100, label='Threshold = 0.05')
plt.scatter(1 - specificity_4, sensitivity_4, c='purple', s=100, label='Threshold = 0.4')
y_45 = np.linspace(0,1,100) 
plt.plot(y_45,y_45,linestyle='dashed', c='cyan', label='random guess')
plt.legend(prop={"family": "Times New Roman", "size": 12})
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.xlabel('False Positive Rate (1 - Specificity)', fontweight='bold', fontsize=16, fontproperties=serif_regular.prop)
plt.ylabel('True Positive Rate (Sensitivity)', fontweight='bold', fontsize=16, fontproperties=serif_regular.prop)
plt.title('ROC Curve', fontweight='bold', fontsize=24, fontproperties=serif_regular.prop)


#%%
#############################################################################
# - Evaluate models by plotting
"---------------------------------------------------------------------------"

coef_angle = df_log_model_shots_coef.iloc[0].values[0]

coef_distance = df_log_model_shots_coef.iloc[2].values[0]

coef_distance_sq = df_log_model_shots_coef.iloc[1].values[0]

B0 = df_log_model_shots_coef.iloc[3].values[0]

#Return xG value for more general model
def calculate_xG(sh):    

   xG = 1/(1 + np.exp(-(coef_distance*sh['distance'] + coef_distance_sq*sh['D2'] 
                        + coef_angle*sh['angle'] + B0)))
   return xG   


#Create a 2D map of xG
pgoal_2d = np.zeros((65, 65))

for x in range(65):
    for y in range(65):
        sh = dict()
        a = np.arctan(7.32 *x /(x**2 + abs(y-65/2)**2 - (7.32/2)**2))
        if a<0:
            a = np.pi + a
        sh['angle'] = a
        sh['distance'] = np.sqrt(x**2 + abs(y-65/2)**2)
        sh['D2'] = x**2 + abs(y-65/2)**2
        sh['X'] = x
        sh['AX'] = x*a
        sh['X2'] = x**2
        #sh['A2'] = a**2
        sh['C'] = abs(y-65/2)
        sh['C2'] = (y-65/2)**2
        
        pgoal_2d[x, y] = calculate_xG(sh)

(fig3, ax3) = FCPython.createGoalMouth()
pos = ax3.imshow(pgoal_2d, extent=[-1, 65, 65, -1], aspect='auto',cmap=plt.cm.Reds,vmin=0, vmax=0.3)
fig3.colorbar(pos, ax=ax3)
ax3.set_title('xG-model goal probabilities', fontsize=24, fontproperties=serif_regular.prop)
plt.xlim((0,66))
plt.ylim((-3,35))
plt.gca().set_aspect('equal', adjustable='box')
plt.show()



