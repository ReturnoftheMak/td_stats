
# %% Package Imports

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


# %% Extract match information

# Need to run exceptions on all of these

def extract_match_information(match_url, soup):
    """Get match information from top banner
    """

    # League details
    league = soup.findAll('div', class_='col-sm-12 col-md-6 col-lg-6 text-center text-lg-left leaguedetail-left')
    try:
        league_name = league[0].text.strip()
    except:
        league_name = ''
    try:
        league_link = league[0].find_all('a')
    except:
        league_link = []
    if len(league_link) > 0:
        league_link = league[0].find_all('a')[0]['href'].split('/')[-1]
    else:
        league_link = ''

    # Ground and Date
    date_ground = soup.findAll('div', class_='col-sm-12 col-md-6 col-lg-6 text-lg-right leaguedetail-right')
    if len(date_ground) > 0:
        date = date_ground[0].text.split("\n")[1].strip()
    else:
        date = ''
    ground_name = soup.find('span', class_='location')
    if ground_name is not None:
        ground_name = soup.find('span', class_='location').text.strip()

    ground_url = soup.find('span', class_='location')
    if ground_url is not None:
        ground_url = soup.find('span', class_='location').find('a')
        if ground_url is not None:
            ground_url = soup.find('span', class_='location').find('a')['href']

    # Reformat for multi-day dates
    date_list = date.split(' ')
    date = ' '.join(date_list[:3])

    # Winner and margin
    winner = soup.findAll('p', class_='match-ttl')
    if len(winner) > 0:
        winner = winner[0].text
    else:
        winner = None

    margin = soup.findAll('div', class_='info mdont')
    if len(margin) > 0:
        margin = margin[0].text
    else:
        margin = None

    # Team info
    club_names = soup.findAll('p', class_='team-name')
    if len(club_names) > 0:
        try:
            home_club = club_names[0].text
        except:
            home_club = ''
        try:
            away_club = club_names[1].text
        except:
            away_club = ''
    else:
        home_club = ''
        away_club = ''

    team_names = soup.findAll('span', class_='team-info-1')
    if len(team_names) > 0:
        try:
            home_team = team_names[0].text.strip()
        except:
            home_team = ''
        try:
            away_team = team_names[1].text.strip()
        except:
            away_team = ''
    else:
        home_team = ''
        away_team = ''

    toss = soup.findAll('p', class_='team-info-3')
    if len(toss) > 0:
        try:
            home_toss = toss[0].text
        except:
            home_toss = ''
        try:
            away_toss = toss[1].text
        except:
            away_toss = ''
    else:
        home_toss = ''
        away_toss = ''

    match_id = match_url.split('/')[-1]

    match_info_dict = {'league_name':league_name,
                       'league_link':league_link,
                       'date':date,
                       'ground_name':ground_name,
                       'ground_url':ground_url,
                       'winner':winner,
                       'margin':margin,
                       'home_club':home_club,
                       'away_club':away_club,
                       'home_team':home_team,
                       'away_team':away_team,
                       'home_toss':home_toss,
                       'away_toss':away_toss,
                       'match_id':match_id}

    df = pd.DataFrame(match_info_dict, index=[0])

    return df


# %% Extract batting innings

# We only need the match url to get both innings, but should also get the
# match id to add on, to link to other tables

def extract_batting_innings(match_url, soup):
    """From
    """

    tables = soup.findAll('table', class_='table standm table-hover')
    innings_list = [table for table in tables]

    innings_names = soup.findAll('ul', class_='nav nav-tabs nav-justified subnav-2')
    if len(innings_names) > 0:
        innings_names = innings_names[0].findAll('li')
    else:
        innings_names = []

    inns_no = 0
    df_list = []
    for innings in innings_list:
        inns_no += 1
        row_dicts = [get_row_to_dict_bat(row, match_url, i) for i, row in enumerate(innings.find_all('tr')[1:])]
        df = pd.DataFrame(row_dicts)
        # Add some other innings information
        df['innings_no'] = inns_no
        if len(innings_names) > 0:
            df['innings_name'] = innings_names[inns_no-1].text.strip()

        df_list.append(df)

    if len(df_list) > 0:
        df_combined = pd.concat(df_list, ignore_index=True)
    else:
        df_combined = pd.DataFrame(columns=['player_name', 'player_id',
                                            'fielding_dismissal', 'dismissal_fielder_name',
                                            'dismissal_fielder_link', 'dismissal_method',
                                            'bowler_name', 'bowler_link',
                                            'runs_scored', 'balls_faced',
                                            'fours_scored', 'sixes_scored',
                                            'strike_rate', 'match_id',
                                            'batting_number', 'captain',
                                            'wicketkeeper', 'innings_name',
                                            'innings_no'])

    return df_combined


# %% Batting innings rows

def get_row_to_dict_bat(row, match_url, i):
    """For a row in the batting innings table, return a dictionary of contents
    """

    cells = row.findAll('td')

    player_name = cells[0].find('div', class_='bts').text

    player_id = cells[0].find('div', class_='bts')
    if player_id is not None:
        player_id = cells[0].find('div', class_='bts').find('a')
        if player_id is not None:
            player_id = cells[0].find('div', class_='bts').find('a')['href'].split("?")[0].split('/')[-1]

    dismissal_fielder_name = cells[1].find('a')
    if dismissal_fielder_name is not None:
        dismissal_fielder_name = cells[1].find('a').text

    dismissal_fielder_link = cells[1].find('a')
    if dismissal_fielder_link is not None:
        dismissal_fielder_link = cells[1].find('a')['href'].split("?")[0].split('/')[-1]

    dismissal_method = cells[2].find('span')
    if dismissal_method is not None:
        dismissal_method = cells[2].find('span').text

    fielding_dismissal = cells[1].find('span')
    if fielding_dismissal is not None:
        fielding_dismissal = cells[1].find('span').text
        if cells[1].find('span').text == 'not out':
            fielding_dismissal = ''
            dismissal_method = 'not out'

    bowler_name = cells[2].find('a')
    if bowler_name is not None:
        bowler_name = cells[2].find('a').text

    bowler_link = cells[2].find('a')
    if bowler_link is not None:
        bowler_link = cells[2].find('a')['href'].split("?")[0].split('/')[-1]

    try:
        runs_scored = int(cells[3].text)
    except:
        runs_scored = np.nan
    
    try:
        balls_faced = int(cells[4].text)
    except:
        balls_faced = np.nan
    
    try:
        fours_scored = int(cells[5].text)
    except:
        fours_scored = np.nan
    
    try:
        sixes_scored = int(cells[6].text)
    except:
        sixes_scored = np.nan

    try:
        strike_rate = float(cells[7].text)
    except:
        strike_rate = np.nan
    
    cap = cells[0].find('img', class_='kcim')
    if cap is not None:
        if cells[0].find('img', class_='kcim')['alt'] == 'Captain':
            captain = True
        else:
            captain = False
    else:
        captain = False

    keep = cells[0].find('img', class_='kcim')
    if keep is not None:
        if cells[0].find('img', class_='kcim')['alt'] == 'Keeper':
            wicketkeeper = True
        else:
            wicketkeeper = False
    else:
        wicketkeeper = False
    
    match_id = match_url.split('/')[-1]
    batting_number = i+1

    row_dict = {'player_name':player_name,
                'player_id':player_id,
                'fielding_dismissal':fielding_dismissal,
                'dismissal_fielder_name':dismissal_fielder_name,
                'dismissal_fielder_link':dismissal_fielder_link,
                'dismissal_method':dismissal_method,
                'bowler_name':bowler_name,
                'bowler_link':bowler_link,
                'runs_scored':runs_scored,
                'balls_faced':balls_faced,
                'fours_scored':fours_scored,
                'sixes_scored':sixes_scored,
                'strike_rate':strike_rate,
                'match_id':match_id,
                'batting_number':batting_number,
                'captain':captain,
                'wicketkeeper':wicketkeeper}

    # print(player_name)
        
    return row_dict


# %% Extract bowling innings

# We only need the match url to get both innings, but should also get the
# innings id to add on, to link to other tables

def extract_bowling_innings(match_url, soup):
    """From
    """

    tables = soup.findAll('table', class_='table bowler-detail table-hover')
    innings_list = [table for table in tables]

    innings_names = soup.findAll('ul', class_='nav nav-tabs nav-justified subnav-2')
    if len(innings_names) > 0:
        innings_names = innings_names[0].findAll('li')
    else:
        innings_names = []

    inns_no = 0
    df_list = []
    for innings in innings_list:
        inns_no += 1
        row_dicts = [get_row_to_dict_bowl(row, match_url, i) for i, row in enumerate(innings.find_all('tr')[1:])]
        df = pd.DataFrame(row_dicts)
        # Add some other innings information
        df['innings_no'] = inns_no
        if len(innings_names) > 0:
            df['innings_name'] = innings_names[inns_no-1].text.strip()

        df_list.append(df)

    if len(df_list) > 0:
        df_combined = pd.concat(df_list, ignore_index=True)
    else:
        df_combined = pd.DataFrame(columns=['player_name', 'player_id',
                                            'overs_bowled', 'maidens_bowled',
                                            'runs_conceded', 'wickets_taken',
                                            'wides_bowled', 'noballs_bowled',
                                            'economy_rate', 'match_id'])

    return df_combined


# %% Bowling innings rows

def get_row_to_dict_bowl(row, match_url, i):
    """For a row in the batting innings table, return a dictionary of contents
    """

    cells = row.findAll('td')

    player_name = cells[0].text

    player_id = cells[0].find('a')
    if player_id is not None:
        player_id = cells[0].find('a')['href'].split("?")[0].split('/')[-1]

    try:
        overs_bowled = float(cells[1].text)
    except:
        overs_bowled = np.nan

    try:
        maidens_bowled = int(cells[2].text)
    except:
        maidens_bowled = np.nan

    try:
        runs_conceded = int(cells[3].text)
    except:
        runs_conceded = np.nan

    try:
        wickets_taken = int(cells[4].text)
    except:
        wickets_taken = np.nan

    try:
        wides_bowled = int(cells[5].text)
    except:
        wides_bowled = np.nan

    try:
        noballs_bowled = int(cells[6].text)
    except:
        noballs_bowled = np.nan

    try:
        economy_rate = float(cells[7].text)
    except:
        economy_rate = np.nan

    match_id = match_url.split('/')[-1]
    bowling_number = i+1

    row_dict = {'player_name':player_name,
                'player_id':player_id,
                'overs_bowled':overs_bowled,
                'maidens_bowled':maidens_bowled,
                'runs_conceded':runs_conceded,
                'wickets_taken':wickets_taken,
                'wides_bowled':wides_bowled,
                'noballs_bowled':noballs_bowled,
                'economy_rate':economy_rate,
                'match_id': match_id,
                'bowling_number':bowling_number}

    # print(player_name)

    return row_dict


# %% Work on this later

def extras_total_extraction(match_url, soup):
    """
    """

    extras_total = soup.findAll('div', class_='alert alert-info alert-info-1 rounded d-inline-block')

    if len(extras_total) == 4:
        batting_extras_1st = extras_total[0]
        bowling_extras_1st = extras_total[1]
        batting_extras_2nd = extras_total[2]
        bowling_extras_2nd = extras_total[3]
        extras = [batting_extras_1st, bowling_extras_1st,
                  batting_extras_2nd, bowling_extras_2nd]
    elif len(extras_total) == 8:
        batting_extras_1st = extras_total[0]
        bowling_extras_1st = extras_total[1]
        batting_extras_2nd = extras_total[2]
        bowling_extras_2nd = extras_total[3]
        batting_extras_3rd = extras_total[4]
        bowling_extras_3rd = extras_total[5]
        batting_extras_4th = extras_total[6]
        bowling_extras_4th = extras_total[7]
        extras = [batting_extras_1st, bowling_extras_1st,
                  batting_extras_2nd, bowling_extras_2nd,
                  batting_extras_3rd, bowling_extras_3rd,
                  batting_extras_4th, bowling_extras_4th]
    else:
        pass
    # Again need the logic for incomplete number of innings

    # Get the number of extras


# %% Match Urls to larger DataFrame

def get_match_data(soup_dict):
    """
    """

    df_list_batting = []
    df_list_bowling = []
    df_list_match_info = []

    for match_url, soup in soup_dict.items():
        # print(match_url)
        df_bat = extract_batting_innings(match_url, soup)
        df_list_batting.append(df_bat)
        df_bowl = extract_bowling_innings(match_url, soup)
        df_list_bowling.append(df_bowl)
        df_match_info = extract_match_information(match_url, soup)
        df_list_match_info.append(df_match_info)

    df_bat_combined = pd.concat(df_list_batting)
    df_bowl_combined = pd.concat(df_list_bowling)
    df_match_info_combined = pd.concat(df_list_match_info)

    return df_bat_combined, df_bowl_combined, df_match_info_combined


# %%

df_bat_combined.to_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\batting_all.csv')
df_bowl_combined.to_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\bowling_all.csv')
df_match_info_combined.to_csv(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\match_info_all.csv')

# %%
