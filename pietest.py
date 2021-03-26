import requests
import re
import os
import time
import collections
import os.path
import ndjson
import random
from Utilities import *

#FixPoints()
#SomePieChart("Participants", "Total participants in each arena category")
#SomePieChart("Events", "Total events in each arena category")
#SomePieChart("Games", "Total games played in each arena category")
#SomePieChart("Moves", "Total moves made in each arena category")
#SomePieChart("TotalPoints", "Total points scored in each arena category")

SomeBoxPlot(lambda ArenaData: ArenaData["Players"], "participants", "Participants per hourly arena")
SomeBoxPlot(lambda ArenaData: ArenaData["TotalRating"] / ArenaData["Players"], "rating", "Average rating per hourly arena")
SomeBoxPlot(lambda ArenaData: ArenaData["Moves"] / ArenaData["Games"] / 2., "moves", "Moves per player per game in hourly arenas")
SomeBoxPlot(lambda ArenaData: ArenaData["TopScore"], "topscore", "Top scores in hourly arenas")
SomeBoxPlot(lambda ArenaData: 100. * ArenaData["Berserks"] / ArenaData["Games"] / 2., "berserk", "Berserk rates in hourly arenas")
SomeBoxPlot(lambda ArenaData: 100. * (ArenaData["Games"] - ArenaData["WhiteWins"] - ArenaData["BlackWins"]) / ArenaData["Games"], "draw", "Draw rates in hourly arenas")
SomeBoxPlot(lambda ArenaData: (ArenaData["WhiteWins"] + 0.5 * (ArenaData["Games"] - ArenaData["WhiteWins"] - ArenaData["BlackWins"])) / ArenaData["Games"], "white", "White's score in hourly arenas")