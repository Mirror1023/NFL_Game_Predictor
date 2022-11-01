# NFL Game Predictor

The goal of this project is to build a model where users can input a "Home Team" and "Away Team" to predict which team would win in a head-to-head matchup. The model will also predict the upcoming slate of games for the week. Accordingly, we will also fetch new data on a weekly basis while the model is live.  

I have scraped the relevant data from www.pro-football-reference.com into one dataset. The Python code for the web scraping can be found in the "Scraping_NFL_Game_Data.ipynb" file.

https://cdn.discordapp.com/attachments/1034140324685164576/1036718637970628729/Screen_Shot_2022-10-31_at_2.58.42_PM.png

The first series of exploratory data analysis on this dataset can be found in the "01_eda.ipynb" file. This file prepares the data for modeling by handling missing values and converting categorical data into numerical data.

We found many missing values so consider the following:
- Every season, each team has one "Bye Week" during the middle of the season. Since there are 32 teams in the league, that's 32 completely empty rows for every season.
- They also have a "Playoffs" row just to designate the start of the postseason tournament. Typically, this row would only be present for 12 teams each season, but since last season, 14 teams now make the playoffs. So that's about 44 empty rows for each season when we include bye week and 46 empty rows for 2021 and beyond.
- The "OT" column is either blank or has OT as it's value for when the game went to overtime. Overtime is not a common occurrence. 
- The column to the left of "Opp" is whether the team was the home team or the away team. It was left blank if the team was playing a home game. It had a value of @ for an away game.
- For column "TO", instead of listing the value as 0, the website left the value blank.


When splitting the dataset, the training dataset should include game data for each team from seasons 2021 to 1994. The test dataset should contain the results from the current 2022 season. 

