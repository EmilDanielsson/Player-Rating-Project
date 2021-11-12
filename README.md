# Player_Rating_Project
==============================

Instruction of how to run the files, and what needs to be downloaded beforehand, for the Player_Rating_Project. Project has been carried out at Uppsala university for the course "Advanced Course on Topics in Scientific Computing I", HT2021 period 1.

Python Packages needed
------------
- `pandas`
- `numpy`
- `json`
- `matplotlib`
- `seaborn`
- `mplsoccer`
- `sklearn`
- `statsmodels`
- `tabulate`

Downloads
------------
Make sure to have Python3 downloaded, along with needed packages listed above.

Get the Wyscout data from: https://figshare.com/collections/Soccer_match_event_dataset/4415000/2 
The following data sets from Wyscout are needed: "events.json", "matches.json", "players.json" and "teams.json".

Place the downloaded Wyscout data in a folder named: `Wyscout`, placed two levels above the Python code.

Also download Excel-sheet `Gameweek_38.xlsx` from XXXXXXXX and place at one level above the Python code.

Getting Started
------------



Project Organization
------------

    ├── README.md                           <- The top-level README for running this project.
    ├── Wyscout                             <- Wyscout data folder.
    │   ├── players.json      
    │   ├── teams.json      
    │   ├── events            
    │   │   ├── events_England.json
    │   │   ├── events_France.json
    │   │   ├── events_Germany.json
    │   │   ├── events_Italy.json
    │   │   └── events_Spain.json
    │   └── matches            
    │       ├── matches_England.json
    │       ├── matches_France.json
    │       ├── matches_Germany.json
    │       ├── matches_Italy.json
    │       └── matches_Spain.json
    │
    └──Player_rating_Project                <- Main folder for this project.
        │
        │
        │
        │
        │
        │
        │
        └── Python_Code                     <- Source code for this project.
            |
            |── create_events_df_eu.py
            |── create_KPI_dataframe_EDIT.py
            |── create_KPI_dataframe.py
            |── FCPython.py
            |── fitting_functions.py
            |── GW_38_Ratings_evaluation.py
            |── GW_38_Ratings.py
            |── KPI_functions.py
            |── minutes_played.py
            |── percentile_functions.py
            |── the_match_ranking.py
            |── validation_vs_WhoScored.py
            └── xG_model_evaluation.py
            
            
            │
            ├── data           <- Scripts to download or generate data
            │   └── make_dataset.py
            │
            ├── features       <- Scripts to turn raw data into features for modeling
            │   └── build_features.py
            │
            ├── models         <- Scripts to train models and then use trained models to make
            │   │                 predictions
            │   ├── predict_model.py
            │   └── train_model.py
            │
            └── visualization  <- Scripts to create exploratory and results oriented visualizations
                └── visualize.py
    


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
