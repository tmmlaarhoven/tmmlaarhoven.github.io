import requests
import re
import os
import time
import collections
import os.path
import ndjson
from Utilities import *

# Above is proper way to only import public things from class
Cat = dict()
for V in AllVs:
	Cat[V] = dict()
	for E in AllEs:
		Cat[V][E] = ArenaCategory(V, E)
		ev1 = Cat[V][E].LoadDataList()
		ev2 = Cat[V][E].LoadRankingInfo()
		if ev2 == ev1:
			Cat[V][E].PrintMessage("Yay!")	
		Cat[V][E].LoadRankingList()		# Load the detailed list of events included in rankings
		Cat[V][E].LoadRankings()		# Load the rankings in memory
		Cat[V][E].LoadPlayerList()		# Load the cumulative player scores in memory
		Cat[V][E].FindMissingList()		# Generate a list of missing IDs
		Cat[V][E].CopyMissingList()		# For mixed later, can use this
		Cat[V][E].FetchMissingData()	# Fetch missing tournament info via API


#Cat[V][E].UpdateRankings()			# Actually update rankings
#Cat[V][E].ScanPlayers()			# Scan for inactive players -- NEEDS TO HAPPEN GLOBALLY
#Cat[V][E].GetTopPlayers(200)		# Get the top 200 players in each of the rankings, for doing the global ScanPlayers() later
#Cat[V][E].UpdatePlayers()			# Update cumulative user scores
#Cat[V][E].UpdatePlots()			# Update various plots
#Cat[V][E].UpdateWebsite(list)		# From the outside, pass a read-only list of user IDs which should be grayed out in the rankings 

