from typing import List

import pandas as pd

from src.paths import DATA_DIR

def load_scrapped_data_from_disk(file_name: str) -> pd.DataFrame:
    """
    Loads CSV file that the scrapper previously generated and saved locally
    to disk

    Args:
        file_name (str): name of the CSV file (not the path, just the name)

    Returns:
        pd.DataFrame: 
    """
    return pd.read_csv(DATA_DIR / file_name)


def fix_opponent_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Some teams have changed their name and/or location, which created another
    opponent. Manually replacing team names.

    Args:
        data (pd.DataFrame): original data

    Returns:
        pd.DataFrame: fixed data
    """
    df.loc[df["opp"] == "Washington Redskins", "opp"] = "Washington Commanders"
    df.loc[df["opp"] == "Washington Football Team", "opp"] = "Washington Commanders"
    df.loc[df["opp"] == "Oakland Raiders", "opp"] = "Las Vegas Raiders"
    df.loc[df["opp"] == "Los Angeles Raiders", "opp"] = "Las Vegas Raiders"
    df.loc[df["opp"] == "Houston Oilers", "opp"] = "Tennessee Titans"
    df.loc[df["opp"] == "Tennessee Oilers", "opp"] = "Tennessee Titans"
    df.loc[df["opp"] == "San Diego Chargers", "opp"] = "Los Angeles Chargers"
    df.loc[df["opp"] == "St. Louis Rams", "opp"] = "Los Angeles Rams"

    # verifying that there are only 32 teams in the df.opp column now.
    assert len(df.opp.unique()) == 32, "There should be 32 teams in the `opp` column"
    
    return df


def map_team_abbreviations_to_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Maps the `team` column abbreviaton to the full name of the team
        Example: "ARZ" -> "Arizona Cardinals"

    Args:
        df (pd.DataFrame): original dataframe with team abbreviations

    Returns:
        pd.DataFrame: transformed data frame with full `team` names
    """

    MAP_ABBREVIATIONS_TO_NAMES  = {
        "ARZ": "Arizona Cardinals",
        "ATL": "Atlanta Falcons",
        "BAL": "Baltimore Ravens",
        "BUF": "Buffalo Bills",
        "CAR": "Carolina Panthers",
        "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals",
        "CLE": "Cleveland Browns",
        "DAL": "Dallas Cowboys",
        "DEN": "Denver Broncos",
        "DET": "Detroit Lions",
        "GB": "Green Bay Packers",
        "HOU": "Houston Texans",
        "IND": "Indianapolis Colts",
        "JAX": "Jacksonville Jaguars",
        "KC": "Kansas City Chiefs",
        "LV": "Las Vegas Raiders",
        "LAC": "Los Angeles Chargers",
        "LAR": "Los Angeles Rams",
        "MIA": "Miami Dolphins",
        "MIN": "Minnesota Vikings",
        "NE": "New England Patriots",
        "NO": "New Orleans Saints",
        "NYG": "New York Giants",
        "NYJ": "New York Jets",
        "PHI": "Philadelphia Eagles",
        "PIT": "Pittsburgh Steelers",
        "SF": "San Francisco 49ers",
        "SEA": "Seattle Seahawks",
        "TB": "Tampa Bay Buccaneers",
        "TEN": "Tennessee Titans",
        "WAS": "Washington Commanders"
    }
    df.replace({"team": MAP_ABBREVIATIONS_TO_NAMES}, inplace=True)
    return df


def add_home_or_away_column(data: pd.DataFrame) -> pd.DataFrame:
    """Adds a new column `home_or_away` to the dataframe with values 'HOME' or
    'AWAY'.

    Args:
        data (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    data['home_or_away'] = ['AWAY' if x == '@' else 'HOME' for x in data['@']]
    return data


def add_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    """_summary_

    Args:
        data (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # year
    df['year'] = df['season']

    # month and day
    df[['month', 'day']] = df['date'].str.split(' ', expand=True)
    # Convert the 'day' column to integer type
    df['day'] = df['day'].astype(int)

    # Conert the `month` from string to integer
    MONTH_MAP = {
        "January":1, "February":2, "March":3, "April":4, "May":5, "June":6,
        "July":7, "August":8, "September":9, "October":10, "November":11,
        "December":12}
    df = df.replace({"month": MONTH_MAP})

    # Extract the hour from the 'time' column
    df['hour'] = df['time'].str[0].astype(int)
    # Add 12 to the 'hour' column for times in the PM
    df['hour'] += df['time'].str.contains('PM').astype(int) * 12

    # combine year, month, day and hour to build the complete date_time
    df['date_time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])

    # df.drop(columns=['year', 'month', 'hour', 'day'], inplace=True)

    return df


def sort_data_by_team_and_datetime(data: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the data by team and datetime
    """
    return data.sort_values(by=['team', 'date_time'], ascending=[True, True], ignore_index=True)#.reset_index(drop=True)


def add_win_rates_last_n_matches(
    data: pd.DataFrame,
    n_matches: List[int] = [1, 3, 5]
) -> pd.DataFrame:
    """Adds 

    Args:
        data (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)

    # add a column with the win/loss result as an integer: win = 1, loss = 0
    data['win'] = data['result'].apply(lambda x: 1 if x == 'W' else 0) 
    
    for n in n_matches:
        data[f'win_rate_last_{n}_matches'] = (
            data
            .groupby('team')['win']
            .shift(1) # so we only use past matches, aka avoid future-data leakage
            .rolling(n, min_periods=0).mean()
            .reset_index(drop=True)
        )

    return data