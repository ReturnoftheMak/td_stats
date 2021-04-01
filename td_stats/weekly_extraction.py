# %% Package Imports

import pandas as pd
from splinter import Browser
from get_all_matches import save_html, get_new_matches, get_soup_from_html
from match_extraction import get_match_data
from statistics import match_info_formatting, batting_formatting, bowling_formatting


# %% Parameters

base_url = r'https://thamesditton.play-cricket.com'
season_id = 2021
browser = Browser('chrome', headless=True)
html_path = r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\html_2021.json'
directory = r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data'


# %% Run process
def update_stats():

    html_dict = get_new_matches(season_id, base_url, browser)

    save_html(html_dict, html_path)

    soup_dict = get_soup_from_html(html_dict)
    df_bat, df_bowl, df_match_info = get_match_data(html_dict)

    df_bat.to_csv(directory + r'\batting_' + str(season_id) + '.csv')
    df_bowl.to_csv(directory + r'\bowling_' + str(season_id) + '.csv')
    df_match_info.to_csv(directory + r'\match_info_' + str(season_id) + '.csv')

    df_bat_combined = pd.concat([df_bat, pd.read_csv(directory + r'\consolidated_files\2020_and_prior\batting_all.csv')])
    df_bowl_combined = pd.concat([df_bowl, pd.read_csv(directory + r'\consolidated_files\2020_and_prior\bowling_all.csv')])
    df_match_info_combined = pd.concat([df_match_info, pd.read_csv(directory + r'\consolidated_files\2020_and_prior\match_info_all.csv')])

    df_bat_combined.to_csv(directory + r'\consolidated_files\batting_all.csv')
    df_bowl_combined.to_csv(directory + r'\consolidated_files\bowling_all.csv')
    df_match_info_combined.to_csv(directory + r'\consolidated_files\match_info_all.csv')

    df_bat_combined = batting_formatting(df_bat_combined)
    df_bowl_combined = bowling_formatting(df_bowl_combined)
    df_match_info_combined = match_info_formatting(df_match_info_combined)

    df_bat_combined.to_csv(directory + r'\processed_data\batting.csv')
    df_bowl_combined.to_csv(directory + r'\processed_data\bowling.csv')
    df_match_info_combined.to_csv(directory + r'\processed_data\match_info.csv')

    pass

if __name__ == '__main__':
    update_stats()
