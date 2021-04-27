import requests
import re
import os
import time
import collections
import os.path
import ndjson
import shutil
from Utilities import *

DrawPlots = False

Cat = dict()
for V in AllVariants:
	Cat[V] = dict()
	for E in AllEvents:

		if DrawPlots:
			shutil.rmtree(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\players\\")			
			Cat[V][E] = ArenaCategory(V, E)
			Cat[V][E].LoadRankings()
			Cat[V][E].UpdateRankings()
			Cat[V][E].UpdatePlots()
			Cat[V][E].UpdateWebsite()
			del Cat[V][E]
		else:
			Cat[V][E] = ArenaCategory(V, E)
			Cat[V][E].LoadRankings()
			Cat[V][E].UpdateRankings()
			Cat[V][E].UpdateWebsite()
			del Cat[V][E]
			