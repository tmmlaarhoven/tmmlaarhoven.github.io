import requests
import re
import os
import time
import collections
import os.path
import ndjson
from Utilities import *

# # Resorting due to earlier bug
# for V in AllVariants:
	# for E in AllEvents:
		# LIST = OrderedDict()
		# with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_arenas.ndjson", "r") as rf:
			# for Line in rf:
				# ArenaData = json.loads(Line)
				# LIST[ArenaData["ID"]] = ArenaData
		# LIST = OrderedDict(sorted(LIST.items(), key = lambda item: item[1]["Start"]))
		# with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_arenas.ndjson", "w") as rf:
			# for Index, ID in enumerate(LIST):
				# LIST[ID]["Number"] = Index + 1
				# rf.write(json.dumps(LIST[ID]) + "\n")



# Above is proper way to only import public things from class
Cat = dict()
for V in AllVariants:
	Cat[V] = dict()
	for E in AllEvents:
		Cat[V][E] = ArenaCategory(V, E)
		Cat[V][E].LoadRankings()
		Cat[V][E].UpdateRankings()
		#Cat[V][E].UpdatePlots()
		Cat[V][E].UpdateWebsite()
		del Cat[V][E]

#Cat[V][E].UpdateRankings()			# Actually update rankings
#Cat[V][E].ScanPlayers()			# Scan for inactive players -- NEEDS TO HAPPEN GLOBALLY
#Cat[V][E].GetTopPlayers(200)		# Get the top 200 players in each of the rankings, for doing the global ScanPlayers() later
#Cat[V][E].UpdatePlayers()			# Update cumulative user scores
#Cat[V][E].UpdatePlots()			# Update various plots
#Cat[V][E].UpdateWebsite(list)		# From the outside, pass a read-only list of user IDs which should be grayed out in the rankings 

