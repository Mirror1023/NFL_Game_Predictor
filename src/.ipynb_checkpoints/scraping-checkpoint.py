# common imports
import requests
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

class Fetch:
    
    def __init__(self):
        return None

    def scrape(self):
        """
        This function fetches game data from www.pro-football-reference.com for each team and each season from 1993-2022.
        The function also manipulates the dataset's missing values to prepare the raw version of the dataset.
        This function will create a .csv file into the working directory.
        """

        # creating a list of years in descending order and an empty list to add dataframes to.
        years = list(range(2022, 1993, -1))
        all_games = []

        # stating the website we will fetch data from, starting with the current 2022 season.
        url = "https://www.pro-football-reference.com/years/2022/"

        # the outer/first for loop creates a list of links that the inner/second for loop will iterate through.
        # we also change the year of the url at the end of the first for loop so new links can be generated from previous seasons.
        # the second for loop reads in the data and appends it to the empty list all_games.
        # the second loop also creates two new columns (Season and Team) to track which team and year each record belongs to.
        # we also perform some initial data cleansing such as dropping a column level and capitalizing team name abbreviations.
        for year in years:
            data = requests.get(url)
            soup = BeautifulSoup(data.text, features="lxml")
            first = soup.select('div.content_grid')[0]
            links = first.find_all('a')
            links = [l.get("href") for l in links]
            team_urls = [f"https://www.pro-football-reference.com/{l}" for l in links]
            url = url.replace(str(year), str(int(year)-1))

            for team_url in team_urls:
                team_name = team_url.split("/")[-2]
                firstdata = requests.get(team_url)
                sched = pd.read_html(firstdata.text, header = None, match = "Schedule & Game Results")
                df = sched[0]
                df.columns = df.columns.droplevel()

                df["Season"] = year
                df["Team"] = team_name.upper()
                all_games.append(df)
                #time.sleep(1) # added to not stress the website with requests, but this line causes the entire loop to hang

        # combining all dataframes into one dataframe
        gamesdf = pd.concat(all_games)

        # transforming all column names to lowercase so exploratory analysis will be easier to perform.
        gamesdf.columns = [c.lower() for c in gamesdf.columns]

        # resetting the index without keeping the old one
        gamesdf = gamesdf.reset_index(drop=True)

        # dropping a column with no value. this column is just a link that provides more details for that particular game - aka boxscore. 
        df = gamesdf.drop(gamesdf.columns[[4]], axis=1) 

        # renaming most column names for more clarity
        df.columns.values[3] = "time"
        df.columns.values[4] = "result"
        df.columns.values[6] = "record"
        df.columns.values[7] = "home_team"
        df.columns.values[9] = "points_scored"
        df.columns.values[10] = "points_allowed"
        df.columns.values[11] = "1st_downs"
        df.columns.values[13] = "passyd"
        df.columns.values[14] = "rushyd"
        df.columns.values[16] = "1st_downs_allowed"
        df.columns.values[17] = "totyd_allowed"
        df.columns.values[18] = "passyd_allowed"
        df.columns.values[19] = "rushyd_allowed"
        df.columns.values[20] = "to_forced"
        df.columns.values[21] = "off_exp_pts"
        df.columns.values[22] = "def_exp_pts"
        df.columns.values[23] = "sts_exp_pts"

        # some team abbreviations are not listed as expected, creating a dictionary to rectify this.
        team_abbr_dict = {"RAM":"LAR", "KAN":"KC", "SFO":"SF", "TAM":"TB", "CRD":"ARZ",
                  "NWE":"NE", "GNB":"GB", "HTX":"HOU", "OTI":"TEN", "RAI":"LV",
                  "NOR":"NO", "SDG":"LAC", "CLT":"IND", "RAV":"BAL"}

        # using the manually created dictionary to replace team abbreviations.
        df = df.replace({"team": team_abbr_dict}) 

        # building a list to view all the column names in the dataframe.
        cols = df.columns.tolist()

        # reordering the column list by placing the season and team columns first.
        cols = cols[-2:] + cols[:-2]

        # applying the new column order to the dataframe and viewing it.
        df = df[cols]

        # dropping bye week rows, playoff rows, games not played yet, etc.
        df = df[df['result'].notna()]

        # using pandas to convert the dataframe into a csv file.
        return df.to_csv("Data/scraped_data.csv", index=False)
    