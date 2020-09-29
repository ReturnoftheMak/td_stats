# %% Package Imports

import pandas as pd


# %% Get the dfs loaded

df_bat_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\batting_all.csv')
df_bowl_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\bowling_all.csv')
df_match_info_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\match_info_all.csv')


# %% Formatting the date column

def match_info_formatting(df_match_info):
    """
    """

    # Convert to timestamp
    df_match_info['date'] = pd.to_datetime(df_match_info['date'], infer_datetime_format=True)

    # New cols for TD Toss win/lose/unknown, TD bat/bowl first

    # Home or Away
    df_match_info['td_home_club_bool'] = df_match_info['home_club'].map({'Thames Ditton CC':True})
    df_match_info['td_home_club_bool'].fillna(value=False, inplace=True)

    df_match_info['td_team'] = df_match_info['home_team'].where(df_match_info['td_home_club_bool'] == True, df_match_info['away_team'])

    df_match_info['td_win'] =  df_match_info['winner'].map({'Thames Ditton CC':True})
    df_match_info['td_win'].fillna(value=False, inplace=True)

    return df_match_info


#%% Try out a grouping of runs by year

def runs_per_year(df_bat, df_match_info, player_name):
    """
    """

    df_bat_p = df_bat[df_bat['player_name'] == player_name]
    df_bat_p = df_bat_p.merge(df_match_info, how='left', on='match_id')

    df_bat_p['date'] = pd.to_datetime(df_bat_p['date'], infer_datetime_format=True)
    df_bat_p['year'] = df_bat_p['date'].dt.year

    runs_by_year = df_bat_p.groupby([df_bat_p['year'], df_bat_p['td_team']], as_index=False)[['td_team', 'runs_scored']].sum()

    return df_bat_p, runs_by_year


# %%
