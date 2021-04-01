
#%% Package Imports

import json
from bs4 import BeautifulSoup
from splinter import Browser


# %% Test URLs

base_url = r'https://thamesditton.play-cricket.com'

start_url = r'https://thamesditton.play-cricket.com/Matches?tab=Result&selected_season_id='

browser = Browser('chrome', headless=True)
browser.visit(base_url)

# %% HTML Retrieval using splinter and bs4

def get_page_soup(url, driver):
    """Returns a BeautifulSoup object for parsing within other functions

    Params:
        url (str): url of website from which html needs to be obtained
        driver (splinter.driver.webdriver.chrome.WebDriver): Splinter webdriver object
    Returns:
        bs4.BeautifulSoup object for parsing
    """

    # Direct webdriver to page, then parse html
    driver.visit(url)
    soup = BeautifulSoup(driver.html, 'html.parser')

    return soup


# %% Get a list of season urls to run through

def get_season_url_list(start_url, driver):
    """Returns a list of starting urls to begin pagination loops from

    Params:
        start_url (str): url from the match list on year view
        driver driver (splinter.driver.webdriver.chrome.WebDriver): Splinter webdriver object

    Returns:
        list of url strings
    """

    soup = get_page_soup(start_url, driver)

    seasons = soup.find('select', id='season_id')
    season_list = seasons.find_all('option')
    season_id_list = [i['value'] for i in season_list]

    season_pages = [r'https://thamesditton.play-cricket.com/Matches?tab=Result&selected_season_id='+ str(id) +r'&view_by=year' for id in season_id_list]

    return season_pages


# %% Now to get all the page urls from each season page

# What are the exceptions here for no pagination?

def get_page_urls(base_url, season_page, driver):
    """For each season starting page, find the other pages.
    """

    soup = get_page_soup(season_page, driver)

    pagination = soup.find('ul', class_='pagination pagination')
    if pagination is not None:
        pages = pagination.find_all('li')
        page_urls = [base_url + page.find('a')['href'] for page in pages[2:-1]]
        page_urls = [season_page] + page_urls
    else:
        page_urls = [season_page]

    return page_urls


# %% Combine all the page_urls for all seasons into a list

def get_all_pages(base_url, start_url, driver):
    """Returns all the pages with matches in
    """

    all_pages = []

    season_pages = get_season_url_list(start_url, driver)

    for season_page in season_pages:
        all_pages += (get_page_urls(base_url, season_page, driver))
    
    return all_pages


# %% Get the match links from each page

def get_match_urls(base_url, page_url, driver):
    """Get all of the innings urls from the matches in a given page url
    """

    soup = get_page_soup(page_url, driver)

    tables = soup.findAll('table')

    if len(tables) > 0:
        match_urls = [base_url+table.find('a')['href'] for table in tables]
    else:
        match_urls = []
    return match_urls


# %% Get all the match urls

def get_all_match_urls(base_url, start_url, driver):
    """Return every match url on the website
    """

    all_match_urls = []

    all_pages = get_all_pages(base_url, start_url, driver)

    for page_url in all_pages:
        all_match_urls += (get_match_urls(base_url, page_url, driver))

    return all_match_urls


# %% Return the innings urls from the match url

# Should work for any number of innings

def innings_url(match_url, driver):
    """From a match url, return the innings urls
    """

    soup = get_page_soup(match_url, driver)

    tab = soup.findAll('ul', id='myTab')[0].find_all('a')

    innings = [x['href'] for x in tab]

    innings_urls = [match_url + inning for inning in innings]

    return innings_urls


# %% Get the html only

def get_html(match_urls, driver):
    """
    """

    html_dict = {}
    for url in match_urls:
        driver.visit(url)
        html_dict[url] = driver.html

    return html_dict

# %% HTML dict saved down to a json

# Save down the html
def save_html(html_dict, filepath):
    with open(filepath, "w") as outfile:
        json.dump(html_dict, outfile)

# Load back in
def load_html(filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)
    return data 

# %% Now we want to create a soup object for each object

def get_soup_from_html(html_dict):
    """
    """
    soup_dict = {}

    for key, value in html_dict.items():
        soup_dict[key] = BeautifulSoup(value, 'html.parser')

    return soup_dict


# %% Get the current season page to start with, then all the match urls
# Can then check if there are any new, pass this to a new_html_dict and update the html json
# I'd prefer to keep anything post 2020 separate

def get_new_matches(current_season_id, base_url, driver):
    """
    """

    season_page = r'https://thamesditton.play-cricket.com/Matches?tab=Result&selected_season_id='+ str(current_season_id) +r'&view_by=year'
    page_urls = get_page_urls(base_url, season_page, driver)
    season_match_urls = []
    for page_url in page_urls:
        season_match_urls += (get_match_urls(base_url, page_url, driver))

    data = load_html(r'C:\Users\Mak\Documents\Python Scripts\thames_ditton_stats\td_stats\data\html_new.json')
    loaded_match_urls = list(data.keys())

    new_match_urls = [match for match in season_match_urls if match not in loaded_match_urls]

    new_html_dict = get_html(new_match_urls,driver)
    data.update(new_html_dict)

    return new_html_dict


# %%