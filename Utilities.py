import requests
import re
import os
import time
import os.path
import ndjson
import json
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from typing import List, Union
from matplotlib.ticker import PercentFormatter
from itertools import product

PureVariants = {
	"3check": "Three-check",
	"antichess": "Antichess",
	"atomic": "Atomic",
	"blitz": "Blitz",
	"bullet": "Bullet",
	"chess960": "Chess960",
	"classical": "Classical",
	"crazyhouse": "Crazyhouse",
	"horde": "Horde",
	"hyperbullet": "HyperBullet",
	"koth": "King of the Hill",
	"racingkings": "Racing Kings",
	"rapid": "Rapid",
	"superblitz": "SuperBlitz",
	"ultrabullet": "UltraBullet"
}
AllVariants = dict(PureVariants)
AllVariants["all"] = "All"

PureEvents = {
	"hourly": "Hourly",
	"2000": "&lt;2000",
	"1700": "&lt;1700",
	"1600": "&lt;1600",
	"1500": "&lt;1500",
	"1300": "&lt;1300",
	"daily": "Daily",
	"weekly": "Weekly",
	"monthly": "Monthly",
	"yearly": "Yearly",
	"eastern": "Eastern",
	"elite": "Elite",
	"shield": "Shield",
	"titled": "Titled",
	"marathon": "Marathon",
	"special": "Special"
}
AllEvents = dict(PureEvents)
AllEvents["all"] = "All"
	
#######################################################################################################################################################################################
#######################################################################################################################################################################################
#######################################################################################################################################################################################

'''
ArenaCategory object: controls local data and update functions for a combination of event and variant.
Internally has functions for e.g. fetching data via the API, updating rankings, player rankings, plots, website.
'''
class ArenaCategory:

	#######################################################################################################################################################################################
	
	'''
	Initializing the category. Input: variant and event.
	'''
	def __init__(self, Variant: str, Event: str):
	
		# Check for correct input
		assert(Variant in AllVariants), f"Incorrect variant description."
		assert(Event in AllEvents), f"Incorrect event description."
		
		# Set variant, event
		self._V = Variant
		self._E = Event
		self._Prefix = f"{self._V}_{self._E}"
		self._Mixed = (False if (self._V in PureVariants and self._E in PureEvents) else True)
		self._Pure = not self._Mixed
		if self._Mixed:
			if self._V == "all":
				self._Vs = list(PureVariants.keys())
			else:
				self._Vs = [self._V]
			if self._E == "all":
				self._Es = list(PureEvents.keys())
			else:
				self._Es = [self._E]
			# For mixed, categories to check are (self._Vs) x (self._Es) c (PureVariants) x (PureEvents)
			
		# Files stored locally in the data directory
		self._PathData = f"E:\\lichess\\tournaments\\data\\{self._V}\\{self._E}\\"
		self._FileDataList = f"{self._PathData}{self._Prefix}.txt"
		
		# Files stored locally in the rankings directory
		self._PathRanking = f"E:\\lichess\\tournaments\\rankings\\{self._V}\\{self._E}\\"
		self._FileRankingInfo = f"{self._PathRanking}{self._Prefix}_ranking.json"	
		self._FileRankingList = f"{self._PathRanking}{self._Prefix}_ranking.ndjson"	
		self._FileRankingPoints = f"{self._PathRanking}{self._Prefix}_ranking_points.ndjson"
		self._FileRankingTrophies = f"{self._PathRanking}{self._Prefix}_ranking_trophies.ndjson"	
		self._FileRankingEvents = f"{self._PathRanking}{self._Prefix}_ranking_events.ndjson"	
		self._FileRankingMaximum = f"{self._PathRanking}{self._Prefix}_ranking_maximum.ndjson"

		# Files stored locally about player cumulative scores over time (for plots)
		self._PathPlayers = f"{self._PathRanking}players\\"
		self._FilePlayerList = f"{self._PathPlayers}{self._Prefix}.txt"				# TODO
		
		# ALl files stored locally and externally in the website directory
		self._PathWeb = f"E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\{self._V}\\{self._E}\\"
		self._PathFigures = f"E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\{self._V}\\{self._E}\\figures\\"
		
		# Initialize data maintenance parameters
		self._DataList = []					# All arena IDs:		["jf03alf3", "dkweo3kX", ...]
		self._MissingList = OrderedDict()		# IDs not in ranking:	{"dkweo3kX": {"ID": "dkweo3kX", "Variant": "bullet", "Event": "hourly"}, ...}
		self._RankingInfo = dict()				# Global ranking info:	{"Events": 200, "Participants": 50240, "Players": 12104, "Games": 1239052, "Moves": 2130935, ...}
		self._RankingList = OrderedDict()		# Arenas in ranking:	{"jf03alf3": {"Number": 1, "ID": "jf03alf3", "Players": 23, "Variant": "bullet", "Event": "hourly", ...}, ...}
		self._Ranking = OrderedDict()			# Player rankings:		{"thijscom": {"Username": "thijscom", "Ranking": 1, "Points": 354, "Events": 12, ...}, ...}
		self._PlayerList = []					# Players potentially for plots, and for whom we keep track of cumulative rankings:	["thijscom", "DrNykterstein", "dugong161", ...]
		self._PlayerListTop = []				# Players actualy for plots:	["DrNykterstein", "penguingim1", ...]
		
		# Internal flags to see whether the data is up to date
		self._DataUpToDate = False				# Is the local data repository up to date?
		self._RankingUpToDate = False			# Are the rankings up to date?
		self._PlayersUpToDate = False			# Are the local cumulative player rankings up to date?
		
		# Initialize some directories if they do not exist yet
		for Path in {self._PathData, self._PathRanking, self._PathPlayers, self._PathWeb, self._PathFigures}:
			if not os.path.exists(Path):
				self.PrintMessage(f"Creating directory {Path}.")
				os.makedirs(Path)
				
		# Load API token for Lichess API queries
		with open(f"E:\\lichess\\APIToken.txt", "r") as TokenFile:
			for Line in TokenFile:
				self._APIToken = Line.strip()
				assert(len(self._APIToken) == 16), f"API token not of length 16."
	
	
	#######################################################################################################################################################################################

	# Functions for sorting rankings
	def _SortPoints(item):
		return item[1]["Score"]
	def _SortTrophies(item):
		return 100000000 * item[1]["Trophies"][0] + 10000 * item[1]["Trophies"][1] + item[1]["Trophies"][2]
	def _SortMaximum(item):
		return item[1]["TopScore"]
	def _SortEvents(item):
		return item[1]["Events"] - item[1].get("Zeros", 0)
		
	# Printing a message to the command line, when running in verbose mode.
	def PrintMessage(self, Message: str):
		print(f"{self._V:<11} - {self._E:<8} - {Message}")

	#######################################################################################################################################################################################

	'''
	Functionalities implemented:				 (P / M)
	
	1. LoadRankings(self)						#   /   #
	 a. _LoadDataList(self)						# P	/ M	# Load list of IDs for which data has been fetched -- assumption is that FetchData.py finished and updated the data files
	 b. _LoadRankingInfo(self)					# 	/ 	# Loads information about rankings to date
	 c. _LoadRankingList(self)					# 	/ 	# Loads list of IDs previously included in rankings
	 d. _LoadRankingData(self)					# 	/ 	# Loads actual detailed rankings in big dictionary
	 e. _LoadPlayerList(self)					# 	/ 	# Loads list of top players to update cumulative rankings for plots
	
	2. UpdateRankings(self)						# 	/ 	# 
	 a. _UpdateRankingInfo(self)				# 	/ 	#
	 b. _UpdatePlayerRanking(self)				# 	/ 	#
	 c. _StoreRankings(self)					# 	/ 	#
	 d. _UpdatePlayers(self)					# 	/ 	#
	
	3. UpdatePlots(self)						# 	/ 	#
	 a. _UpdateArenaPlots(self)					# 	/ 	#
	 b. _UpdateUserPlots(self)					# 	/ 	#
	
	4. UpdateWebsite(self)						# 	/ 	#
	
	'''

	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# 1. Load all data in memory
	def LoadRankings(self):
		self._LoadDataList()
		self._LoadRankingInfo()
		if len(self._DataList) == self._RankingInfo["Events"]:
			self._PrintMessage("Nothing to do.")
		else:
			self._LoadRankingList()
			self._LoadRankingData()
			self._LoadPlayerList()
		
	#######################################################################################################################################################################################		
		
	# 1a. Load all IDs till now from a file (both IDs included in the ranking and those not yet in the ranking).
	def _LoadDataList(self):
		if self._Pure:
			# Pure
			if os.path.exists(self._FileDataList):		
				with open(self._FileDataList, "r") as FileDataList:
					for Line in FileDataList:
						self._DataList.append(Line[0:8])				
				self._DataList.sort(key = lambda ID: ID.lower())
				self.PrintMessage(f"Loaded {len(self._DataList)} plain tournament IDs from file.")
			else:
				self.PrintMessage(f"No file with arena IDs found.")
		else:
			# Mixed
			for V, E in product(self._Vs, self._Es):
				if os.path.exists(f"{self._PathData}{self._V}_{self._E}.txt"):		
					with open(f"{self._PathData}{self._V}_{self._E}.txt", "r") as FileDataList:
						for Line in FileDataList:
							self._DataList.append(Line[0:8])

	#######################################################################################################################################################################################

	# 1b. Load ranking information from file.
	def _LoadRankingInfo(self):
		
		# Load data from file
		if os.path.exists(self._FileRankingInfo): 
			with open(self._FileRankingInfo, "r") as FileRankingInfo:
				self._RankingInfo = json.load(FileRankingInfo)
		else:
			self._RankingInfo = {"Events": 0, "Participants": 0, "Games": 0, "Moves": 0, "WhiteWins": 0, "BlackWins": 0, "Berserks": 0, "TotalPoints": 0, "TotalRating": 0, "FirstStart": "2030-01-01T00:00:00.000Z", "FirstID": "XXXXXXXX", "LastStart": "2010-01-01T00:00:00.000Z", "LastID": "YYYYYYYY", "MaxUsers": 0, "MaxUsersID": "ZZZZZZZZ", "TopScore": 0, "TopScoreID": "WWWWWWWW", "TopUser": "-", "Players": 0, "Points": 0}
			with open(self._FileRankingInfo, "w") as FileRankingInfo:
				FileRankingInfo.write(json.dumps(self._RankingInfo))

		assert(self._RankingInfo["Events"] <= len(self._DataList)), f"Ranking information shows more events than the list of IDs." 		

	#######################################################################################################################################################################################

	# 1c. Load ranking list of arenas from file (subset of all IDs, namely those that have been processed).
	def _LoadRankingList(self):
		
		# Load data from files
		if os.path.exists(self._FileRankingList):	
			with open(self._FileRankingList, "r") as FileRankingList:
				for Line in FileRankingList:
					ArenaData = json.loads(Line)
					self._RankingList[ArenaData["ID"]] = ArenaData
			self.PrintMessage(f"Loaded {len(self._RankingList)} detailed arena statistics from file.")
		else:
			self.PrintMessage(f"No file with detailed arena statistics found.")
		self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda Arena: Arena[1]["Start"]))

		# Update internal flags about being up to date
		assert(self._RankingInfo["Events"] == len(self._RankingList)), f"Ranking information shows a different number of events than the detailed list."
		if len(self._RankingList) < len(self._DataList):
			self._DataUpToDate = False		
			self._RankingUpToDate = False
			self._PlayersUpToDate = False
		else:
			self._DataUpToDate = True		
			self._RankingUpToDate = True
			self._PlayersUpToDate = True		

		return len(self._RankingList)
	
	#######################################################################################################################################################################################
	
	# 1d. Load players for cumulative rankings from file.
	def _LoadPlayerList(self):
		assert(os.path.exists(self._PathPlayers)), f"No directory for player scores; why are we loading this list?"
		if not os.path.exists(self._FilePlayerList):
			self.PrintMessage(f"No list of players yet. Making one based on files in directory...")
			self._PlayerList = []
			for Filename in os.listdir(self._PathPlayers):
				if Filename.endswith(".json"):
					self._PlayerList.append(Filename[len(self._V)+len(self._E)+2:-5])
			self.PrintMessage(f"Found {len(self._PlayerList)} players. Storing to file...")
			with open(self._FilePlayerList, "w") as FilePlayerList:
				for PlayerID in self._PlayerList:
					FilePlayerList.write(f"{PlayerID.lower()}\n")
			self.PrintMessage(f"Saved {len(self._PlayerList)} user IDs to file.")
		else:
			self._PlayerList = []
			with open(self._FilePlayerList, "r") as FilePlayerList:
				for Line in FilePlayerList:
					self._PlayerList.append(Line.strip())
			self.PrintMessage(f"Loaded {len(self._PlayerList)} users from file.")
		return len(self._PlayerList)
	
	#######################################################################################################################################################################################
	
	# 1e. If we need to update rankings, then we need to load the rankings data.
	def _LoadRankingData(self) -> bool:

		# Load actual rankings
		if os.path.exists(self._FileRankingPoints):	
			with open(self._FileRankingPoints, "r") as RankFile:
				for Line in RankFile:
					UserRank = json.loads(Line)
					self._Ranking[UserRank["Username"].lower()] = UserRank
		else:
			assert(len(self._RankingList) == 0), "How come no detailed ranking file exists?"
		
		# Load ranking information
		if os.path.exists(self._FileRankingInfo): 
			with open(self._FileRankingInfo, "r") as RankInfoFile:
				self._RankingInfo = json.load(RankInfoFile)
		else:
			assert(len(self._RankingList) == 0), "How come no ranking information file exists?"

		# Checks for internal consistency of existing rankings
		if len(self._RankingList) > 0:
			assert(len(self._Ranking) > 0), "Inconsistent ranking files. No users in rankings."
			assert("Events" in self._RankingInfo), "Inconsistent ranking files. No entry Events in RankInfo."
			assert("FirstID" in self._RankingInfo), "Inconsistent ranking files. No entry FirstID in RankInfo."
			assert("LastID" in self._RankingInfo), "Inconsistent ranking files. No entry LastID in RankInfo."
			assert(self._RankingInfo["Events"] == len(self._RankingList)), "Inconsistent ranking files. Unequal number of events."
			assert(self._RankingInfo["FirstID"] in self._RankingList), "Inconsistent ranking files. Unequal first IDs."
			assert(self._RankingInfo["LastID"] in self._RankingList), "Inconsistent ranking files. Unequal last IDs."
		
		return True

	
	''' 
	Sort and store rankings to files
	'''
	def _StoreRankings(self):
	
		# Different orders for rankings, and sort functions
		ListFiles = [self._FileRankingPoints, self._FileRankingTrophies, self._FileRankingEvents, self._FileRankingMaximum]
		ListSorts = [self._SortPoints, self._SortTrophies, self._SortEvents, self._SortMaximum]
		
		# Store in different orders to different files
		for i in range(len(ListFiles)):
			self._Ranking = {k: v for k, v in sorted(self._Ranking.items(), key = lambda item: ListSorts[0](item), reverse = True)}
			self._Ranking = {k: v for k, v in sorted(self._Ranking.items(), key = lambda item: ListSorts[i](item), reverse = True)}
			with open(ListFiles[i], "w") as RankFile:
				for Index, UserID in enumerate(Ranking):
					self._Ranking[UserID]["Ranking"] = Index + 1
					RankFile.write(json.dumps(self._Ranking[UserID]) + "\n")
					# Do not compute top 10 here as it's intermediate lists only...
					if Index < 100:
						if not UserID.lower() in self._PlayerList:
							self._PlayerList.append(UserID.lower())							
					if Index == 999 and i != 0:
						break
	
	
	'''
	Update a player's ranking with a new arena result
	'''
	def _UpdatePlayer(self, UserRanking, UserResult, ArenaInfo):
		return True
		
	
	'''
	Updating ranking information with one arena
	'''
	def _UpdateRankingInfo(self, ArenaInfo):
		return True
	
	
	'''
	Updating cumulative stuff
	'''
	def _UpdatePlayerScores(self):
		return
	
	
	'''
	'''
	def UpdateRankings(self):
		# Update based on new IDs
		# Store back to file
		# Also resort plain list of IDs and store in file, to be sure
		
		return
	
	
	#######################################################################################################################################################################################
		

	def _UpdateArenaPlots(self, Type):
		return
	
	def _UpdateUserPlots(self, Type):
		return
	
	def UpdatePlots(self):
		return True
		
	def UpdateWebsite(self):
		return True
		








		