# %% Package Imports

import pandas as pd


# %% Get the dfs loaded

df_bat_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\td_stats\data\batting_all.csv')
df_bowl_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\td_stats\data\bowling_all.csv')
df_match_info_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\td_stats\data\match_info_all.csv')


# %% Formatting the date column

def match_info_formatting(df_match_info):
    """
    """

    df_match_info['date'] = pd.to_datetime(df_match_info['date'], infer_datetime_format=True)

    # New cols for TD Toss win/lose/unknown, TD bat/bowl first


#%% Try out a grouping of runs by year

def runs_per_year(df_bat, df_match_info, player_name):
    """
    """

    df_bat_p = df_bat[df_bat['player_name'] == player_name]
    df_bat_p = df_bat_p.merge(df_match_info, how='left', on='match_id')

    df_bat_p['date'] = pd.to_datetime(df_bat_p['date'], infer_datetime_format=True)

    runs_by_year = df_bat_p.groupby(df_bat_p['date'].dt.year)['runs_scored'].sum()

    return runs_by_year


# %%
