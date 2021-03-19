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
	"3check": 		{"Name": "Three-check", 	"Color": [204, 121, 167], 	"WebOrder": 11,		"Icon": "."},
	"antichess": 	{"Name": "Antichess",		"Color": [223, 83, 83],		"WebOrder": 12,		"Icon": "@"},
	"atomic": 		{"Name": "Atomic",			"Color": [102, 85, 140],	"WebOrder": 13,		"Icon": ">"},
	"blitz": 		{"Name": "Blitz",			"Color": [0, 114, 178],		"WebOrder": 5,		"Icon": ")"},
	"bullet": 		{"Name": "Bullet",			"Color": [86, 180, 233],	"WebOrder": 3,		"Icon": "T"},
	"chess960": 	{"Name": "Chess960",		"Color": [230, 159, 0],		"WebOrder": 9,		"Icon": "'"},
	"classical": 	{"Name": "Classical",		"Color": [69, 159, 59],		"WebOrder": 7,		"Icon": "+"},
	"crazyhouse": 	{"Name": "Crazyhouse",		"Color": [86, 180, 233],	"WebOrder": 8,		"Icon": "&#xe00b;"},
	"horde": 		{"Name": "Horde",			"Color": [153, 230, 153],	"WebOrder": 14,		"Icon": "_"},
	"hyperbullet": 	{"Name": "HyperBullet",		"Color": [86, 180, 233],	"WebOrder": 2,		"Icon": "T"},
	"koth": 		{"Name": "King of the Hill","Color": [213, 94, 0],		"WebOrder": 10,		"Icon": "("},
	"racingkings": 	{"Name": "Racing Kings",	"Color": [255, 174, 170],	"WebOrder": 15,		"Icon": "&#xe00a;"},
	"rapid": 		{"Name": "Rapid",			"Color": [0, 158, 115],		"WebOrder": 6,		"Icon": "#"},
	"superblitz": 	{"Name": "SuperBlitz",		"Color": [0, 114, 178],		"WebOrder": 4,		"Icon": ")"},
	"ultrabullet": 	{"Name": "UltraBullet",		"Color": [0, 158, 115],		"WebOrder": 1,		"Icon": "{"}
}
AllVariants = dict(PureVariants)
AllVariants["all"] = {"Name": "All",			"Color": [200, 200, 200],	"WebOrder": 0,		"Icon": "O"}

PureEvents = {
	"hourly": 		{"Name": "Hourly"},
	"2000": 		{"Name": "&lt;2000"},
	"1700": 		{"Name": "&lt;1700"},
	"1600": 		{"Name": "&lt;1600"},
	"1500": 		{"Name": "&lt;1500"},
	"1300": 		{"Name": "&lt;1300"},
	"daily": 		{"Name": "Daily"},
	"weekly": 		{"Name": "Weekly"},
	"monthly": 		{"Name": "Monthly"},
	"yearly": 		{"Name": "Yearly"},
	"eastern": 		{"Name": "Eastern"},
	"elite": 		{"Name": "Elite"},
	"shield": 		{"Name": "Shield"},
	"titled": 		{"Name": "Titled"},
	"marathon": 	{"Name": "Marathon"}
}
AllEvents = dict(PureEvents)
AllEvents["all"] = 	{"Name": "All"}
	
#######################################################################################################################################################################################
#######################################################################################################################################################################################
#######################################################################################################################################################################################

'''
ArenaCategory object: controls local data and update functions for a combination of event and variant.
Internally has functions for e.g. loading rankings, updating the rankings, the cumulative player rankings, plots, website.
'''
class ArenaCategory:
	
	# Initializing the category. Input: variant and event.
	def __init__(self, Variant: str, Event: str):
	
		# Check for correct input
		assert(Variant in AllVariants), f"Incorrect variant description."
		assert(Event in AllEvents), f"Incorrect event description."
		
		# Set variant, event
		self._V = Variant
		self._E = Event
		self.PrintMessage("Starting...")
		self._Prefix = f"{self._V}_{self._E}"
		self._Mixed = (False if (self._V in PureVariants and self._E in PureEvents) else True)
		self._Pure = not self._Mixed
		if self._V == "all":
			self._Vs = list(PureVariants.keys())
		else:
			self._Vs = [self._V]
		if self._E == "all":
			self._Es = list(PureEvents.keys())
		else:
			self._Es = [self._E]
		
		# Files stored locally in the data directory
		self._PathData = f"E:\\lichess\\tournaments\\data\\"
		if self._Pure:
			self._FileDataList = f"{self._PathData}{self._Prefix}.txt"
			self._FileDataDetailedList = f"{self._PathData}{self._Prefix}.ndjson"
		
		# Files stored locally in the rankings directory
		self._PathRanking = f"E:\\lichess\\tournaments\\rankings\\{self._V}\\{self._E}\\"
		self._FileRankingInfo = f"{self._PathRanking}{self._Prefix}_ranking.json"	
		self._FileRankingList = f"{self._PathRanking}{self._Prefix}_ranking.ndjson"	
		self._FileRankingFull = f"{self._PathRanking}{self._Prefix}_ranking_full.ndjson"
		#self._FileRankingFullOld = f"{self._PathRanking}{self._Prefix}_ranking_points.ndjson"
		self._FileRankingPoints = f"{self._PathRanking}{self._Prefix}_players_points.ndjson"
		self._FileRankingTrophies = f"{self._PathRanking}{self._Prefix}_players_trophies.ndjson"	
		self._FileRankingEvents = f"{self._PathRanking}{self._Prefix}_players_events.ndjson"	
		self._FileRankingAverage = f"{self._PathRanking}{self._Prefix}_players_average.ndjson"	
		self._FileRankingMaximum = f"{self._PathRanking}{self._Prefix}_players_maximum.ndjson"
		
		# Files stored locally in the rankings directory
		self._FileArenaNewest = f"{self._PathRanking}{self._Prefix}_arenas_newest.ndjson"	
		self._FileArenaPlayers = f"{self._PathRanking}{self._Prefix}_arenas_players.ndjson"	
		self._FileArenaMaximum = f"{self._PathRanking}{self._Prefix}_arenas_maximum.ndjson"
		self._FileArenaRating = f"{self._PathRanking}{self._Prefix}_arenas_rating.ndjson"	
		
		# Storing rankings based on different orderings
		self._ListFiles = [self._FileRankingPoints, self._FileRankingTrophies, self._FileRankingEvents, self._FileRankingMaximum]
		self._ListSorts = [self._SortPoints, self._SortTrophies, self._SortEvents, self._SortMaximum]
		
		# Files stored locally about player cumulative scores over time (for plots)
		self._PathPlayers = f"{self._PathRanking}players\\"
		self._FilePlayerList = f"{self._PathPlayers}{self._Prefix}.txt"
		
		# ALl files stored locally and externally in the website directory
		self._PathWeb = f"E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\{self._V}\\{self._E}\\"
		self._PathFigures = f"E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\{self._V}\\{self._E}\\figures\\"
		
		# Initialize data maintenance parameters
		self._DataList = OrderedDict()			# All arena IDs:		{"jf03alf3": {"Number": 1, "ID": "jf03alf3", "Players": 23, "Variant": "bullet", "Event": "hourly", ...}, "dkweo3kX", ...}
		self._NewList = OrderedDict()			# IDs not in ranking:	["jf03alf3": {...}, ...]
		self._RankingInfo = dict()				# Global ranking info:	{"Events": 200, "Participants": 50240, "Players": 12104, "Games": 1239052, "Moves": 2130935, ...}
		self._RankingList = OrderedDict()		# Arenas in ranking:	{"jf03alf3": {"Number": 1, "ID": "jf03alf3", "Players": 23, "Variant": "bullet", "Event": "hourly", ...}, ...}
		self._Ranking = OrderedDict()			# Player rankings:		{"thijscom": {"Username": "thijscom", "Ranking": 1, "Points": 354, "Events": 12, ...}, ...}
		self._PlayerList = OrderedDict()		# Players potentially for plots, and for whom we keep track of cumulative rankings:	["thijscom", "DrNykterstein", "dugong161", ...]
		self._PlayerListTop = OrderedDict()		# Players actually used for plots:	["DrNykterstein", "penguingim1", ...]
		self._PlayerStatus = OrderedDict()			# Latest player status:	{"thijscom": {..., "CumTrophies": [13, 11, 15], "CumEvents": 210, "CumTopScore": ...}, ...}
		self._UpToDate = False
		
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
	def _SortPoints(self, item):
		return item["Score"]
	def _SortTrophies(self, item):
		return 100000000 * item["Trophies"][0] + 10000 * item["Trophies"][1] + item["Trophies"][2]
	def _SortEvents(self, item):
		return item["Events"] - item.get("Zeros", 0)
	def _SortAverage(self, item):
		return item["Score"] / max(item["Events"], 1)
	def _SortMaximum(self, item):
		return item["TopScore"]
	def _SortNewest(self, item):
		return item["Start"]
	def _SortPlayers(self, item):
		return item["Players"]
	def _SortTopScore(self, item):
		return item["TopScore"]
	def _SortRating(self, item):
		return item["TotalRating"] / item["Players"]
		
	# Printing a message to the command line, when running in verbose mode.
	def PrintMessage(self, Message: str):
		print(f"{self._V:<11} - {self._E:<8} - {Message}")

	#######################################################################################################################################################################################

	'''
	Functionalities implemented:
	
	1. LoadRankings(self)						 (P	/ M)	
	 a. _LoadDataList(self)						# P	/ M	#	Load list of IDs for which data has been fetched -- assumption is that FetchData.py finished and updated the data files
	 b. _LoadRankingInfo(self)					# P	/ M	#	Loads information about rankings to date
	 c. _LoadRankingList(self)					# P	/ M	#	Loads list of IDs previously included in rankings
	 d. _LoadRankingData(self)					# P	/ M	#	Loads actual detailed rankings in big dictionary
	 e. _LoadPlayerList(self)					# P	/ M	#	Loads list of top players to update cumulative rankings for plots
	 f. _FixPlayers(self)						# P / M #	If no list of players exists, fix this and make up to date lists
	 g. _LoadPlayerStatus(self)					# P / M #	Loads latest player statuses for cumulative updates
	 h. _LoadMissingList(self)					# P	/ M	#	Generates list of missing IDs and detailed info for later
	
	2. UpdateRankings(self)						 (P	/ M)
	 a. _UpdateRankingPlayer(self, ...)			# P	/ M	#	For a given player and tournament result, update their ranking
	 b. _UpdateRankingStats(self, ArenaData)	# P	/ M	#	Update the ranking info based on the stats of one new tournament
	 c. _StoreRankings(self)					# P	/ M	#	Store all the rankings to files
	
	3. UpdatePlots(self)						 (	/  )	
	 a. _UpdateArenaPlots(self)					# 	/ 	#	
	 b. _UpdateUserPlots(self)					# 	/ 	#	
		
	4. UpdateWebsite(self)						# 	/ 	#	
	 a. _UpdateLists(self)						# 	/ 	#

	'''

	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# 1. Load all data in memory
	def LoadRankings(self):
		self.PrintMessage("1. Loading...")
		
		
		
		if os.path.exists(f"{self._PathRanking}{self._Prefix}_ranking_events.ndjson"):
			os.remove(f"{self._PathRanking}{self._Prefix}_ranking_events.ndjson")
			
		if os.path.exists(f"{self._PathRanking}{self._Prefix}_ranking_maximum.ndjson"):
			os.remove(f"{self._PathRanking}{self._Prefix}_ranking_maximum.ndjson")
			
		if os.path.exists(f"{self._PathRanking}{self._Prefix}_ranking_trophies.ndjson"):
			os.remove(f"{self._PathRanking}{self._Prefix}_ranking_trophies.ndjson")
			
			
			
		self._LoadDataList()			# Up to date data that has been fetched
		self._LoadRankingInfo()			# Current global information about rankings
		if len(self._DataList) == self._RankingInfo["Events"]:
			self._UpToDate = True
			self.PrintMessage("Nothing to do.")
		else:
			self._UpToDate = False
			self.PrintMessage(f"Out of {len(self._DataList)} events, only {self._RankingInfo['Events']} included in rankings so far.")
			self._LoadRankingList()		# Detailed list of events currently in rankings
			self._LoadRankingData()		# Detailed state of rankings
			self._LoadPlayerList()		# Top players for cumulative scores
			self._LoadPlayerStatus()	# For those top players, load most recent info
			self._LoadMissingList()		# Make a list of detailed arena info for updates
		# self._FIXUSERFILES()		# TEMPORARY FIX	
	
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
		
	# 1a. Load all IDs till now from a file (both IDs included in the ranking and those not yet in the ranking).
	def _LoadDataList(self):
		for V, E in product(self._Vs, self._Es):
			if os.path.exists(f"{self._PathData}{V}\\{E}\\{V}_{E}.txt") and os.path.exists(f"{self._PathData}{V}\\{E}\\{V}_{E}.ndjson"):
				with open(f"{self._PathData}{V}\\{E}\\{V}_{E}.ndjson", "r") as FileDataDetailedList:
					for Line in FileDataDetailedList:
						ArenaData = json.loads(Line)
						self._DataList[ArenaData["ID"]] = ArenaData
		self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda Arena: Arena[1]["Start"]))

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	# 1b. Load ranking information from JSON file.
	def _LoadRankingInfo(self):
		if os.path.exists(self._FileRankingInfo): 
			with open(self._FileRankingInfo, "r") as FileRankingInfo:
				self._RankingInfo = json.load(FileRankingInfo)
			if self._RankingInfo["Events"] == 0:
				os.remove(self._FileRankingInfo)
		else:
			
			self._RankingInfo = {"Events": 0, "Participants": 0, "Games": 0, "Moves": 0, "WhiteWins": 0, "BlackWins": 0, "Berserks": 0, "TotalPoints": 0, "TotalRating": 0, "FirstStart": "2030-01-01T00:00:00.000Z", "FirstID": "XXXXXXXX", "LastStart": "2010-01-01T00:00:00.000Z", "LastID": "YYYYYYYY", "MaxUsers": 0, "MaxUsersID": "ZZZZZZZZ", "TopScore": 0, "TopScoreID": "WWWWWWWW", "TopUser": "-", "Players": 0, "Points": 0}
			#with open(self._FileRankingInfo, "w") as FileRankingInfo:
			#	FileRankingInfo.write(json.dumps(self._RankingInfo))

		assert(self._RankingInfo["Events"] <= len(self._DataList)), f"Ranking information shows more events than the more up to date list of IDs!" 		

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1c. Load ranking list of arenas from file (subset of all IDs, namely those that have been processed).
	def _LoadRankingList(self):
		if os.path.exists(self._FileRankingList):	
			with open(self._FileRankingList, "r") as FileRankingList:
				for Line in FileRankingList:
					ArenaData = json.loads(Line)
					self._RankingList[ArenaData["ID"]] = ArenaData
			self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda Arena: Arena[1]["Start"]))
			self.PrintMessage(f"Loaded {len(self._RankingList)} detailed arena statistics from file.")
		else:
			self.PrintMessage(f"No file with detailed arena statistics found.")

		assert(self._RankingInfo["Events"] == len(self._RankingList)), f"Ranking information shows a different number of events than the detailed ranking list."	

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1d. If we need to update rankings, then we need to load the rankings data.
	def _LoadRankingData(self):
		if os.path.exists(self._FileRankingFull):	
			with open(self._FileRankingFull, "r") as FileRankingData:
				for Line in FileRankingData:
					UserRank = json.loads(Line)
					self._Ranking[UserRank["Username"].lower()] = UserRank
		else:
			self.PrintMessage(f"No file with detailed ranking data found.")
			assert(len(self._RankingList) == 0), f"How come no detailed ranking file exists?"

		# Checks for internal consistency of existing rankings
		if len(self._RankingList) > 0:
			assert(len(self._Ranking) > 0), "Inconsistent ranking files. No users in rankings."
			assert("Events" in self._RankingInfo), "Inconsistent ranking files. No entry Events in RankInfo."
			assert("FirstID" in self._RankingInfo), "Inconsistent ranking files. No entry FirstID in RankInfo."
			assert("LastID" in self._RankingInfo), "Inconsistent ranking files. No entry LastID in RankInfo."
			assert(self._RankingInfo["Events"] == len(self._RankingList)), "Inconsistent ranking files. Unequal number of events."
			assert(self._RankingInfo["FirstID"] in self._RankingList), "Inconsistent ranking files. Unequal first IDs."
			assert(self._RankingInfo["LastID"] in self._RankingList), "Inconsistent ranking files. Unequal last IDs."
		
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1e. Load players for cumulative rankings from file.
	def _LoadPlayerList(self):
		if not os.path.exists(self._FilePlayerList):
			self.PrintMessage(f"No list of players yet. Making one based on rankings...")
			if len(self._RankingList) > 0:
				self._FixPlayers()
		else:
			with open(self._FilePlayerList, "r") as FilePlayerList:
				for Line in FilePlayerList:
					UserID = Line.strip().lower()
					self._PlayerList[UserID] = 1
			self._PlayerList = OrderedDict(sorted(self._PlayerList.items(), key = lambda item: item[0]))
			self.PrintMessage(f"Loaded {len(self._PlayerList)} users from file.")

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1f. In case no player files exist yet, generate them now from past tournaments.
	def _FixPlayers(self):
		# First build list of relevant players to maintain, say top 100
		self.PrintMessage(f"Building list of relevant players...")
		for FilenameTopPlayers in self._ListFiles:
			with open(FilenameTopPlayers, "r") as FileTopPlayers:
				for Index, Line in enumerate(FileTopPlayers):
					UserRanking = json.loads(Line.strip())
					UserID = UserRanking["Username"].lower()
					self._PlayerList[UserID] = 1
					if Index > 100:
						break
		self.PrintMessage(f"Loaded {len(self._PlayerList)} users into a list.")
		self._PlayerList = OrderedDict(sorted(self._PlayerList.items(), key = lambda item: item[0]))
		
		# Initialize empty JSON and NDJSON files
		UserJSON = dict()
		UserNDJSON = dict()
		for Username in self._PlayerList:
			UserID = Username.lower()
			UserJSON[UserID] = dict()
			UserJSON[UserID]["Variant"] = self._V
			UserJSON[UserID]["Event"] = self._E
			UserJSON[UserID]["Username"] = UserID
			UserJSON[UserID]["FirstID"] = "-"
			UserJSON[UserID]["LastID"] = "-"
			UserJSON[UserID]["CumTrophies"] = [0, 0, 0]
			UserJSON[UserID]["CumPoints"] = 0
			UserJSON[UserID]["CumEvents"] = 0
			UserJSON[UserID]["CumTopScore"] = 0
			UserNDJSON[UserID] = []
		
		# Then fetch data from arenas already in rankings and update
		self.PrintMessage(f"Updating the users based on past events.")
		for Index, ID in enumerate(self._RankingList):
			V = self._RankingList[ID]["Variant"]
			E = self._RankingList[ID]["Event"]
			with open(f"{self._PathData}{V}\\{E}\\{V}_{E}_{ID}.ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					if UserResult["score"] == 0:
						break
					if UserResult["username"].lower() in self._PlayerList and UserResult["score"] > 0:
						
						# Update JSON stats
						UserID = UserResult["username"].lower()
						if UserJSON[UserID]["FirstID"] == "-":
							UserJSON[UserID]["FirstID"] = ID
						UserJSON[UserID]["LastID"] = ID
						if UserResult["rank"] == 1:
							UserJSON[UserID]["CumTrophies"][0] = UserJSON[UserID]["CumTrophies"][0] + 1
						elif UserResult["rank"] == 2:
							UserJSON[UserID]["CumTrophies"][1] = UserJSON[UserID]["CumTrophies"][1] + 1
						elif UserResult["rank"] == 3:
							UserJSON[UserID]["CumTrophies"][2] = UserJSON[UserID]["CumTrophies"][2] + 1
						UserJSON[UserID]["CumPoints"] = UserJSON[UserID]["CumPoints"] + UserResult["score"]
						UserJSON[UserID]["CumEvents"] = UserJSON[UserID]["CumEvents"] + 1
						UserJSON[UserID]["CumTopScore"] = max(UserJSON[UserID]["CumTopScore"], UserResult["score"])
						
						# Update NSJSON stats
						newdict = dict()
						newdict["ID"] = ID
						newdict["Start"] = self._RankingList[ID]["Start"]
						newdict["CumTrophies"] = UserJSON[UserID]["CumTrophies"].copy()
						newdict["CumPoints"] = UserJSON[UserID]["CumPoints"]
						newdict["CumEvents"] = UserJSON[UserID]["CumEvents"]
						newdict["CumTopScore"] = UserJSON[UserID]["CumTopScore"]
						UserNDJSON[UserID].append(newdict)
			
			# Intermediate progress update
			if Index % 1000 == 0 and Index > 0:
				self.PrintMessage(f"Finished processing {Index + 1} events. (Nothing saved...)")
		
		# Final dump
		self.PrintMessage(f"Storing cumulative player scores after {len(self._RankingList)} past events.")
		for UserID in self._PlayerList:
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json", "w") as JSONFile:
				json.dump(UserJSON[UserID], JSONFile)
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson", "w") as NDJSONFile:
				for Index in range(len(UserNDJSON[UserID])):
					NDJSONFile.write(json.dumps(UserNDJSON[UserID][Index]) + "\n")
					
		# Print list of usernames to file
		self._PlayerList = OrderedDict(sorted(self._PlayerList.items(), key = lambda item: item[0]))
		with open(f"{self._PathPlayers}{self._V}_{self._E}.txt", "w") as UsernameFile:
			for Username in self._PlayerList:
				UsernameFile.write(Username.lower() + "\n")
					
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1g. In case no player files exist yet, generate them now from past tournaments.
	def _LoadPlayerStatus(self):	
		assert(len(self._PlayerList) > 100), "How is this possible?"
		for UserID in self._PlayerList:
			assert(os.path.exists(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json")), "What?"
			assert(os.path.exists(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson")), "What??"
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json", "r") as JSONFile:
				self._PlayerStatus[UserID] = json.load(JSONFile)	

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1h. Find list of missing events
	def _LoadMissingList(self):
		for ID in self._DataList:
			if ID not in self._RankingList:
				self._NewList[ID] = self._DataList[ID].copy()
		self._NewList = OrderedDict(sorted(self._NewList.items(), key = lambda Arena: Arena[1]["Start"]))
	
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# 2. Updating the rankings
	def UpdateRankings(self):
	
		self.PrintMessage("2. Updating...")
		if self._UpToDate:
			self.PrintMessage("Nothing to do! Already up to date.")
			return
		
		# Checks for internal consistency of existing rankings
		if len(self._RankingList) > 0:
			assert(len(self._Ranking) > 0), "Inconsistent ranking files. No users in rankings."
			assert("Events" in self._RankingInfo), "Inconsistent ranking files. No entry Events in RankInfo."
			assert("FirstID" in self._RankingInfo), "Inconsistent ranking files. No entry FirstID in RankInfo."
			assert("LastID" in self._RankingInfo), "Inconsistent ranking files. No entry LastID in RankInfo."
			assert(self._RankingInfo["Events"] == len(self._RankingList)), f"Inconsistent ranking files. Unequal number of events. {self._RankingInfo['Events']} != {len(self._RankingList)}"
			assert(self._RankingInfo["FirstID"] in self._RankingList), "Inconsistent ranking files. Unequal first IDs."
			assert(self._RankingInfo["LastID"] in self._RankingList), "Inconsistent ranking files. Unequal last IDs."
	
		# Go through all new events
		for Index, ID in enumerate(self._NewList):
			ArenaData = self._NewList[ID]
			V = ArenaData["Variant"]
			E = ArenaData["Event"]
			self.PrintMessage(f"New event: {ID}.")
			assert(ArenaData["ID"] not in self._RankingList), "Inconsistent rankings. New tournament ID already included."
			
			# Load tournament results
			with open(f"{self._PathData}{V}\\{E}\\{V}_{E}_{ID}.ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					# UserResult: {"rank": 1, "score": 36, "rating": 2267, "username": "kasparovsabe", "title": "FM", "performance": 2454}
					UserID = UserResult["username"].lower()
					if UserID not in self._Ranking:
						# New player
						self._Ranking[UserID] = dict()
						self._RankingInfo["Players"] = self._RankingInfo.get("Players", 0) + 1
					
					# Update player information
					self._UpdateRankingPlayer(UserID, UserResult, ArenaData)
					self._Ranking[UserID]["Username"] = UserResult["username"].lower()
					
					# For special players, add new cumulative score to files
					if UserID in self._PlayerList and UserResult["score"] > 0:
						
						# Update JSON stats
						self._PlayerStatus[UserID]["LastID"] = ID
						if UserResult["rank"] == 1:
							self._PlayerStatus[UserID]["CumTrophies"][0] = self._PlayerStatus[UserID]["CumTrophies"][0] + 1
						elif UserResult["rank"] == 2:
							self._PlayerStatus[UserID]["CumTrophies"][1] = self._PlayerStatus[UserID]["CumTrophies"][1] + 1
						elif UserResult["rank"] == 3:
							self._PlayerStatus[UserID]["CumTrophies"][2] = self._PlayerStatus[UserID]["CumTrophies"][2] + 1
						self._PlayerStatus[UserID]["CumPoints"] = self._PlayerStatus[UserID]["CumPoints"] + UserResult["score"]
						self._PlayerStatus[UserID]["CumEvents"] = self._PlayerStatus[UserID]["CumEvents"] + 1
						self._PlayerStatus[UserID]["CumTopScore"] = max(self._PlayerStatus[UserID]["CumTopScore"], UserResult["score"])

						# Save new entry to user files
						with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson", "a+") as NDJSONFile:
							newdict = dict()
							newdict["ID"] = ID
							newdict["Start"] = ArenaData["Start"]
							newdict["CumTrophies"] = self._PlayerStatus[UserID]["CumTrophies"].copy()
							newdict["CumPoints"] = self._PlayerStatus[UserID]["CumPoints"]
							newdict["CumEvents"] = self._PlayerStatus[UserID]["CumEvents"]
							newdict["CumTopScore"] = self._PlayerStatus[UserID]["CumTopScore"]
							NDJSONFile.write(json.dumps(newdict) + "\n")

			# Update global statistics
			self._UpdateRankingInfo(ArenaData)
				
			# Update newly processed events, and do intermediate data dumps
			if Index % 1000 == 0 and Index > 0:
				self.PrintMessage(f"Intermediate dump after {Index} new events.")
				self._StoreRankings()

		# Wrap up
		self.PrintMessage(f"Final dump after {len(self._NewList)} new events.")	
		self._StoreRankings()
		
		# Store new user JSON status in files
		for UserID in self._PlayerList:
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json", "w") as JSONFile:
				json.dump(self._PlayerStatus[UserID], JSONFile)	
		
		# Sort all events by date (should be unnecessary) and store them in a file
		self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda Arena: Arena[1]["Start"]))
		with open(f"{self._FileRankingList}", "w") as RankListFile:
			for Index, (ID, Arena) in enumerate(self._DataList.items()):
				Arena["Number"] = Index + 1
				RankListFile.write(json.dumps(Arena) + "\n")	
				
		self._StoreArenaRankings()

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	# 2a. Update player ranking in self._Ranking
	def _UpdateRankingPlayer(self, UserID, UserResult, ArenaData):
		self._Ranking[UserID]["Ranking"] = 0
		self._Ranking[UserID]["Score"] = self._Ranking[UserID].get("Score", 0) + UserResult["score"]
		self._Ranking[UserID]["Events"] = self._Ranking[UserID].get("Events", 0) + 1
		if not "First" in self._Ranking[UserID]:
			self._Ranking[UserID]["First"] = ArenaData["Start"]
			self._Ranking[UserID]["FirstID"] = ArenaData["ID"]
		self._Ranking[UserID]["Last"] = ArenaData["Start"]
		self._Ranking[UserID]["LastID"] = ArenaData["ID"]
		if self._Ranking[UserID].get("TopScore", -1) <= UserResult["score"]:
			self._Ranking[UserID]["TopScore"] = UserResult["score"]
			self._Ranking[UserID]["TopScoreID"] = ArenaData["ID"]
		if self._Ranking[UserID].get("MaxRank", 1000000) >= UserResult["rank"]:
			self._Ranking[UserID]["MaxRank"] = UserResult["rank"]
			self._Ranking[UserID]["MaxRankID"] = ArenaData["ID"]
		self._Ranking[UserID]["Username"] = UserResult["username"]
		if not "Trophies" in self._Ranking[UserID]:
			self._Ranking[UserID]["Trophies"] = [0, 0, 0]
		self._Ranking[UserID]["Trophies"][0] = self._Ranking[UserID]["Trophies"][0] + (1 if UserResult["rank"] == 1 else 0)
		self._Ranking[UserID]["Trophies"][1] = self._Ranking[UserID]["Trophies"][1] + (1 if UserResult["rank"] == 2 else 0)
		self._Ranking[UserID]["Trophies"][2] = self._Ranking[UserID]["Trophies"][2] + (1 if UserResult["rank"] == 3 else 0)
		if "title" in UserResult:
			self._Ranking[UserID]["Title"] = UserResult["title"]
		self._Ranking[UserID]["Zeros"] = self._Ranking[UserID].get("Zeros", 0) + (1 if UserResult["score"] == 0 else 0)

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	# 2b. Updating ranking info based on some arena data
	def _UpdateRankingInfo(self, ArenaData):
		self._RankingInfo["Events"] = self._RankingInfo.get("Events", 0) + 1
		self._RankingInfo["Participants"] = self._RankingInfo.get("Participants", 0) + ArenaData["Players"]
		self._RankingInfo["Games"] = self._RankingInfo.get("Games", 0) + ArenaData["Games"]
		self._RankingInfo["Moves"] = self._RankingInfo.get("Moves", 0) + ArenaData["Moves"]
		self._RankingInfo["WhiteWins"] = self._RankingInfo.get("WhiteWins", 0) + ArenaData["WhiteWins"]
		self._RankingInfo["BlackWins"] = self._RankingInfo.get("BlackWins", 0) + ArenaData["BlackWins"]
		self._RankingInfo["Berserks"] = self._RankingInfo.get("Berserks", 0) + ArenaData["Berserks"]
		self._RankingInfo["TotalPoints"] = self._RankingInfo.get("TotalPoints", 0) + ArenaData["TotalPoints"]
		self._RankingInfo["TotalRating"] = self._RankingInfo.get("TotalRating", 0) + ArenaData["TotalRating"]
		if not "FirstID" in self._RankingInfo:
			self._RankingInfo["FirstStart"] = ArenaData["Start"]
			self._RankingInfo["FirstID"] = ArenaData["ID"]
		self._RankingInfo["LastStart"] = ArenaData["Start"]
		self._RankingInfo["LastID"] = ArenaData["ID"]
		if self._RankingInfo.get("MaxUsers", 0) < ArenaData["Players"]:
			self._RankingInfo["MaxUsers"] = ArenaData["Players"]
			self._RankingInfo["MaxUsersID"] = ArenaData["ID"]
		if self._RankingInfo.get("TopScore", 0) < ArenaData["TopScore"]:
			self._RankingInfo["TopScore"] = ArenaData["TopScore"]
			self._RankingInfo["TopScoreID"] = ArenaData["ID"]
			self._RankingInfo["TopUser"] = ArenaData["#1"]
	
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 2c. Sort and store rankings to files
	def _StoreRankings(self):
	
		# Different orders for rankings, and sort functions
		ListFiles = [self._FileRankingFull, self._FileRankingPoints, self._FileRankingTrophies, self._FileRankingEvents, self._FileRankingAverage, self._FileRankingMaximum]
		ListSorts = [self._SortPoints, self._SortPoints, self._SortTrophies, self._SortEvents, self._SortAverage, self._SortMaximum]
		
		# Store in different orders to different files
		for i in range(len(ListFiles)):
			self._Ranking = OrderedDict(sorted(self._Ranking.items(), key = lambda item: ListSorts[0](item[1]), reverse = True))
			self._Ranking = OrderedDict(sorted(self._Ranking.items(), key = lambda item: ListSorts[i](item[1]), reverse = True))
			with open(ListFiles[i], "w") as RankFile:
				for Index, UserID in enumerate(self._Ranking):
					self._Ranking[UserID]["Ranking"] = Index + 1
					RankFile.write(json.dumps(self._Ranking[UserID]) + "\n")					
					if Index == 999 and i != 0:
						break

		# Print information to json
		with open(self._FileRankingInfo, "w") as RankInfoFile:
			RankInfoFile.write(json.dumps(self._RankingInfo))
		
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 2d. Sort and store lists of arenas to files		
	def _StoreArenaRankings(self):
	
		# Different orders for rankings, and sort functions
		ListFiles = [self._FileArenaNewest, self._FileArenaPlayers, self._FileArenaMaximum, self._FileArenaRating]
		ListSorts = [self._SortNewest, self._SortPlayers, self._SortTopScore, self._SortRating]
	
		# Store in different orders to different files
		for i in range(len(ListFiles)):
			self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda item: ListSorts[0](item[1]), reverse = True))
			self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda item: ListSorts[i](item[1]), reverse = True))
			with open(ListFiles[i], "w") as ArenaFile:
				for Index, ArenaID in enumerate(self._DataList):
					self._DataList[ArenaID]["Number"] = Index + 1
					ArenaFile.write(json.dumps(self._DataList[ArenaID]) + "\n")					
					if Index == 999:
						break

		# Resort data list in proper order
		self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda Arena: Arena[1]["Start"], reverse = False))
		
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	
	def _FIXUSERFILES(self):
		for UserID in self._PlayerList:
			NDJSONList = []
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson", "r") as NDJSONFile:
				for Line in NDJSONFile:
					newdict = dict()
					olddict = json.loads(Line.strip())
					if "LastID" in olddict:
						newdict["ID"] = olddict["LastID"]
						newdict["Start"] = self._DataList[newdict["ID"]]["Start"]
					else:
						newdict["ID"] = olddict["ID"]
						newdict["Start"] = olddict["Start"]
					newdict["CumTrophies"] = olddict["CumTrophies"]	
					newdict["CumPoints"] = olddict["CumPoints"]	
					newdict["CumEvents"] = olddict["CumEvents"]	
					newdict["CumTopScore"] = olddict["CumTopScore"]	
					NDJSONList.append(newdict)
			assert(self._PlayerStatus[UserID]["CumEvents"] == len(NDJSONList)), "SOMETHING WRONG!"
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson", "w") as NDJSONFile:
				for i in range(len(NDJSONList)):
					NDJSONFile.write(json.dumps(NDJSONList[i]) + "\n")
	

	def _UpdateArenaPlots(self, Type):
		return
	
	def _UpdateUserPlots(self, Type):
		return
	
	def UpdatePlots(self):
		return
		
	def UpdateWebsite(self):
		return
		








		