# NFL Game Predictor

The goal of this project is to build a model where users can input a "Home Team" and "Away Team" to predict which team would win in a head-to-head matchup. The model will also predict the upcoming slate of games for the week. Accordingly, we will also fetch new data on a weekly basis while the model is live.  

I have scraped the relevant data from www.pro-football-reference.com into one dataset. The Python code for the web scraping can be found in the "Scraping_NFL_Game_Data.ipynb" file.

The first series of exploratory data analysis on this dataset can be found in the "01_eda.ipynb" file. This file prepares the data for modeling by handling missing values and converting categorical data into numerical data.

When splitting the dataset, the training dataset should include game data for each team from seasons 2021 to 1994. The test dataset should contain the results from the current 2022 season. 

