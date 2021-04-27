import requests
import re
import os
import time
import collections
import os.path
import ndjson
from Utilities import *

Cat = dict()
for V in AllVariants:
	Cat[V] = dict()
	for E in AllEvents:
		Cat[V][E] = ArenaCategory(V, E)
		Cat[V][E].LoadRankings()
		Cat[V][E].UpdateRankings()
		Cat[V][E].UpdatePlots()
		Cat[V][E].UpdateWebsite()
		del Cat[V][E]