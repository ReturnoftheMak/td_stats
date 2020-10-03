# %% Package Imports

import pandas as pd


# %% Get the dfs loaded

df_bat_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\consolidated_files\batting_all.csv')
df_bowl_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\consolidated_files\bowling_all.csv')
df_match_info_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\consolidated_files\match_info_all.csv')


# %% Formatting the date column

def match_info_formatting(df_match_info=df_match_info_combined):
    """
    """

    # Convert to timestamp
    df_match_info['date'] = pd.to_datetime(df_match_info['date'], infer_datetime_format=True)

    # New cols for TD Toss win/lose/unknown, TD bat/bowl first

    # Home or Away
    df_match_info['td_home_club'] = df_match_info['home_club'].map({'Thames Ditton CC':True})
    df_match_info['td_home_club'] = df_match_info['td_home_club'].fillna(value=False)

    # TD team playing in the match
    df_match_info['td_team'] = df_match_info['home_team'].where(df_match_info['td_home_club'] == True, df_match_info['away_team'])

    # TD winners of the match
    df_match_info['td_match_win'] =  df_match_info['winner'].map({'THAMES DITTON CC':True})
    df_match_info['td_match_win'] = df_match_info['td_match_win'].fillna(value=False)

    # TD win the toss - add in unknown logic here, so not boolean
    def win_toss(row):
        if row['td_home_club'] == True:
            if 'won' in str(row['home_toss']).lower():
                td_toss_win = 'won'
            elif 'won' in str(row['away_toss']).lower():
                td_toss_win = 'loss'
            else:
                td_toss_win = 'unknown'
        else:
            if 'won' in str(row['away_toss']).lower():
                td_toss_win = 'won'
            elif 'won' in str(row['home_toss']).lower():
                td_toss_win = 'loss'
            else:
                td_toss_win = 'unknown'
        
        return td_toss_win

    df_match_info['td_toss_win'] = df_match_info.apply(lambda row : win_toss(row), axis=1)

    df_match_info = df_match_info.drop(labels=['Unnamed: 0','Unnamed: 0.1','Unnamed: 0.1.1','Unnamed: 0.1.1.1'], axis=1)

    return df_match_info


# %% Formatting for bowling

# Figure out how to aggregate the overs properly

def bowling_formatting():
    """
    """
    pass


# %% Formatting for batting

def batting_formatting(df_bat):
    """
    """

    # Batsman has an innings
    df_bat['innings_played'] = df_bat['fielding_dismissal'].map({'did not bat':False})
    df_bat['innings_played'].fillna(True, inplace=True)
    # Bat is dismissed
    df_bat['is_dismissed'] = df_bat['innings_played'].where(df_bat['dismissal_method'] != 'not out')
    df_bat['is_dismissed'].fillna(0, inplace=True)
    df_bat['is_dismissed'] = df_bat['is_dismissed'].map({1:True, 0:False})

    df_bat = df_bat.drop(labels=['Unnamed: 0','Unnamed: 0.1'], axis=1)

    return df_bat


#%% Try out a grouping of runs by year

def runs_per_year(df_bat=df_bat_combined, df_match_info=df_match_info_combined, player_name=''):
    """
    """

    df_bat_p = df_bat[df_bat['player_name'] == player_name]
    df_bat_p = df_bat_p.merge(df_match_info, how='left', on='match_id')

    df_bat_p['date'] = pd.to_datetime(df_bat_p['date'], infer_datetime_format=True)
    df_bat_p['year'] = df_bat_p['date'].dt.year

    runs_by_year = df_bat_p.groupby([df_bat_p['year']], as_index=False)[['runs_scored']].sum()

    return df_bat_p, runs_by_year


# %% Matches played

def number_of_matches_played(df_bat=df_bat_combined, player_name=''):
    """
    """

    df_bat_p = df_bat[df_bat['player_name'] == player_name]

    games_played = len(df_bat_p.match_id.unique())

    return games_played






