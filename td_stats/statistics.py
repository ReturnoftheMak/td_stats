# %% Package Imports

import pandas as pd
import numpy as np


# %% Get the dfs loaded

df_bat_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\consolidated_files\batting_all.csv')
df_bowl_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\consolidated_files\bowling_all.csv')
df_match_info_combined = pd.read_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\consolidated_files\match_info_all.csv')


# %% Formatting the match info

def match_info_formatting(df_match_info=df_match_info_combined, df_bat=df_bat_combined):
    """Create additional columns and format some of the data within existing
    """

    # Convert to timestamp
    df_match_info['date'] = pd.to_datetime(df_match_info['date'], infer_datetime_format=True)

    # New cols for TD Toss win/lose/unknown, TD bat/bowl first

    # Home or Away
    df_match_info['td_home_club'] = df_match_info['home_club'].map({'Thames Ditton CC':True})
    df_match_info['td_home_club'] = df_match_info['td_home_club'].fillna(value=False)

    # Fill in the club info from team if blank
    df_match_info['home_club'].replace('\xa0', None, inplace=True)
    df_match_info['home_club'].fillna(df_match_info['home_team'])
    df_match_info['away_club'].replace('\xa0', None, inplace=True)
    df_match_info['away_club'].fillna(df_match_info['away_team'])

    # TD batting first - may need to use the batting info to supplement unknown
    inns = df_bat[df_bat['innings_name'] == 'Thames Ditton CC'][['match_id', 'innings_no']]
    inns = inns.groupby('match_id').min()
    inns['innings_no'] = inns['innings_no'].map({1:'batted_first', 2:'bowled_first'})
    inns.columns = ['bat_bowl']
    df_match_info = df_match_info.merge(inns, how='left', left_on='match_id', right_index=True)

    def bat_first(row):
        if row['td_home_club'] == True:
            if 'bat' in str(row['home_toss']).lower():
                td_bat_first = 'batted_first'
            elif 'field' in str(row['home_toss']).lower():
                td_bat_first = 'bowled_first'
            elif 'bat' in str(row['away_toss']).lower():
                td_bat_first = 'bowled_first'
            elif 'field' in str(row['away_toss']).lower():
                td_bat_first = 'batted_first'
            else:
                td_bat_first = row['bat_bowl']
        else:
            if 'bat' in str(row['away_toss']).lower():
                td_bat_first = 'batted_first'
            elif 'field' in str(row['away_toss']).lower():
                td_bat_first = 'bowled_first'
            elif 'bat' in str(row['home_toss']).lower():
                td_bat_first = 'bowled_first'
            elif 'field' in str(row['home_toss']).lower():
                td_bat_first = 'batted_first'
            else:
                td_bat_first = row['bat_bowl']
        
        return td_bat_first
    
    df_match_info['td_bat_first'] = df_match_info.apply(lambda row : bat_first(row), axis=1)

    # TD team playing in the match
    df_match_info['td_team'] = df_match_info['home_team'].where(df_match_info['td_home_club'] == True, df_match_info['away_team'])

    # TD winners of the match - need to differentiate nr to draws
    # Need to be able to infer a winner
    def td_match_result(row):
        if str(row['margin']).strip() == 'MATCH DRAWN':
            result = 'draw'
        elif row['winner'] == 'THAMES DITTON CC':
            result = 'win'
        elif type(row['winner']) is str and row['winner'] != 'THAMES DITTON CC':
            result = 'loss'
        elif type(row['winner']) is float and type(row['margin']) is str:
            if 'RUNS' in row['margin'] and row['td_bat_first'] == 'batted_first':
                result = 'win'
            elif 'WICKET' in row['margin'] and row['td_bat_first'] == 'batted_first':
                result = 'loss'
            elif 'RUNS' in row['margin'] and row['td_bat_first'] == 'bowled_first':
                result = 'loss'
            elif 'WICKET' in row['margin'] and row['td_bat_first'] == 'bowled_first':
                result = 'win'
            else:
                result = 'check_1'
        elif type(row['winner']) is float and type(row['margin']) is float:
            result = 'no result'
        else:
            result = 'check_2'
        return result

    df_match_info['td_match_win'] =  df_match_info.apply(lambda row : td_match_result(row), axis=1)

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

    df_match_info = df_match_info.drop(labels=['Unnamed: 0','Unnamed: 0.1','Unnamed: 0.1.1','Unnamed: 0.1.1.1', 'bat_bowl'], axis=1)

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
    def null_inns(runs):
        if np.isnan(runs) == True:
            return False
        else:
            return np.nan

    df_bat['innings_played'] = df_bat['runs_scored'].apply(lambda x : null_inns(x))
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


# %% Analysis of the captains

# Most tosses won/lost in a row by captains
# Do teams win more when winning the toss?

def captain_win_loss_by_toss(df_match_info, df_bat, captain=''):
    """Return some basic stats around the toss
    """

    cap = df_bat[(df_bat['captain'] == True) & (df_bat['innings_name'].str.contains('Thames Ditton CC'))][['player_name', 'match_id']]
    cap.columns = ['captain_name', 'match_id']
    df_mi = df_match_info.merge(cap, how='left', on='match_id')
    df_mi = df_mi[df_mi['captain_name'] == captain]

    # Wins and losses by toss outcome
    df_mi = df_mi[df_mi['td_match_win'].isin(['win', 'loss', 'draw'])]
    df_mi['count'] = 1
    cap_result = df_mi.pivot_table(index='td_toss_win', columns='td_match_win', values='count', aggfunc='sum', fill_value=0)
    cap_result['total'] = cap_result.sum(axis=1) 
    cap_result_perc = cap_result.div(cap_result.iloc[:,-1], axis=0)

    return cap_result, cap_result_perc


# %% Helper function for cumulative sums by partition

def count_consecutive_items_n_cols(df, col_name_list, output_col):
        """
        """
        cum_sum_list = [(df[col_name] != df[col_name].shift(1)).cumsum().tolist() for col_name in col_name_list]
        df[output_col] = df.groupby(["_".join(map(str, x)) for x in zip(*cum_sum_list)]).cumcount() + 1
        return df


# %% Get streaks for tosses

def longest_toss_streaks(df_match_info, df_bat):
    """
    """

    cap = df_bat[(df_bat['captain'] == True) & (df_bat['innings_name'].str.contains('Thames Ditton CC'))][['player_name', 'match_id']]
    cap.columns = ['captain_name', 'match_id']
    df_mi = df_match_info.merge(cap, how='inner', on='match_id')

    # sort by captain and then date
    df_mi = df_mi[df_mi['td_toss_win'] != 'unknown']
    toss_streak = df_mi[['captain_name', 'date', 'td_team', 'td_toss_win']]
    toss_streak.sort_values(['captain_name', 'date'], ascending=[True, True], inplace=True)
    toss_streak['Count'] = toss_streak['td_toss_win'].map({'won':1, 'loss':0})

    # try this one next
    toss_streak = count_consecutive_items_n_cols(toss_streak, ['captain_name', 'td_toss_win'], 'counts')

    return toss_streak


# %% Use the same logic in the streaks to figure out who is quickest
#    to certain milestones

# filter for anyone who has got to 1000 runs in total
# then use the cumulative sum to work out in which match the player reached 1000
# filter for games in which cumsum is > 1000 and then get minimum per player to get matches
# then use a game count with another cumulative to find the games/innings taken to get there
# Sort ascending and return list

def innings_to_milestone_runs(df_bat, df_match_info, runs_milestone=1000):
    """
    """

    inns_to_runs = df_bat[(df_bat['innings_played'] == True) & (df_bat['innings_name'].str.contains('Thames Ditton CC'))]
    inns_to_runs = inns_to_runs.merge(df_match_info[['match_id', 'date']], how='left', on='match_id')

    inns_to_runs.sort_values(['player_name', 'date'], ascending=[True, True], inplace=True)

    inns_to_runs = count_consecutive_items_n_cols(inns_to_runs, ['player_name'], 'cumulative_inns')
    inns_to_runs['cumulative_runs'] = inns_to_runs.groupby(['player_name'])['runs_scored'].apply(lambda x: x.cumsum())

    milestone = inns_to_runs[inns_to_runs['cumulative_runs'] >= runs_milestone]
    milestone = milestone.groupby(['player_name'])['cumulative_inns'].min().reset_index()
    milestone.sort_values('cumulative_inns', ascending=True, inplace=True)

    return milestone

# Doesn't quite work with the innings thing?? Seems to have missed some
# Find if there are any runs scored when the innings is false 

# Now we've got all innings containing TD rather than exactly TD

# Still Mike has 5 more innings than the data suggests, Jonners +2
# Abandoned games it looks like - fixed, innings now match
