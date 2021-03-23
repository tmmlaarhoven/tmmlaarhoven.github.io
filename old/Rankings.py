import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json
import math
import datetime

APIToken = ""
with open("E:\\lichess\\APIToken.txt", "r") as TokenFile:
	for Line in TokenFile:
		APIToken = Line.strip()

PathData = "E:\\lichess\\tournaments\\data\\"
PathRank = "E:\\lichess\\tournaments\\rankings\\"
PathWeb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

Variants = {
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

Events = {
	"1300": "&lt;1300",
	"1500": "&lt;1500",
	"1600": "&lt;1600",
	"1700": "&lt;1700",
	"2000": "&lt;2000",
	"hourly": "Hourly",
	"daily": "Daily",
	"weekly": "Weekly",
	"monthly": "Monthly",
	"yearly": "Yearly",
	"eastern": "Eastern",
	"elite": "Elite",
	"shield": "Shield",
	"titled": "Titled",
	"marathon": "Marathon"
}

def Prefix(V, E):
	return V + "_" + E + "_"

def Folder(V, E):
	return V + "\\" + E + "\\"
	
def PrintMessage(V, E, Message):
	print("{:<11}".format(V) + " - {:<8}".format(E) + " - " + Message)

# Update ranking information for a player based on new ranking information
# - UserRank: Information about user in this ranking (custom)
# - UserResult: The result of the user in some event (API-fetched)
# - ArenaData: Auxiliary information about the event (custom)
def UpdatePlayer(UserRank, UserResult, ArenaData):
	UserRank["Ranking"] = 0
	UserRank["Score"] = UserRank.get("Score", 0) + UserResult["score"]
	UserRank["Events"] = UserRank.get("Events", 0) + 1
	if not "First" in UserRank:
		UserRank["First"] = ArenaData["Start"]
		UserRank["FirstID"] = ArenaData["ID"]
	UserRank["Last"] = ArenaData["Start"]
	UserRank["LastID"] = ArenaData["ID"]
	if UserRank.get("TopScore", -1) <= UserResult["score"]:
		UserRank["TopScore"] = UserResult["score"]
		UserRank["TopScoreID"] = ArenaData["ID"]
	if UserRank.get("MaxRank", 1000000) >= UserResult["rank"]:
		UserRank["MaxRank"] = UserResult["rank"]
		UserRank["MaxRankID"] = ArenaData["ID"]
	UserRank["Username"] = UserResult["username"]
	if not "Trophies" in UserRank:
		UserRank["Trophies"] = [0, 0, 0]
	UserRank["Trophies"][0] = UserRank["Trophies"][0] + (1 if UserResult["rank"] == 1 else 0)
	UserRank["Trophies"][1] = UserRank["Trophies"][1] + (1 if UserResult["rank"] == 2 else 0)
	UserRank["Trophies"][2] = UserRank["Trophies"][2] + (1 if UserResult["rank"] == 3 else 0)
	if "title" in UserResult:
		UserRank["Title"] = UserResult["title"]
	UserRank["Zeros"] = UserRank.get("Zeros", 0) + (1 if UserResult["score"] == 0 else 0)

# Update global ranking information based on new tournament ranking
def UpdateStats(RankInfo, ArenaData):
	RankInfo["Events"] = RankInfo.get("Events", 0) + 1
	RankInfo["Participants"] = RankInfo.get("Participants", 0) + ArenaData["Players"]
	RankInfo["Games"] = RankInfo.get("Games", 0) + ArenaData["Games"]
	RankInfo["Moves"] = RankInfo.get("Moves", 0) + ArenaData["Moves"]
	RankInfo["WhiteWins"] = RankInfo.get("WhiteWins", 0) + ArenaData["WhiteWins"]
	RankInfo["BlackWins"] = RankInfo.get("BlackWins", 0) + ArenaData["BlackWins"]
	RankInfo["Berserks"] = RankInfo.get("Berserks", 0) + ArenaData["Berserks"]
	RankInfo["TotalPoints"] = RankInfo.get("TotalPoints", 0) + ArenaData["TotalPoints"]
	RankInfo["TotalRating"] = RankInfo.get("TotalRating", 0) + ArenaData["TotalRating"]
	if not "FirstID" in RankInfo:
		RankInfo["FirstStart"] = ArenaData["Start"]
		RankInfo["FirstID"] = ArenaData["ID"]
	RankInfo["LastStart"] = ArenaData["Start"]
	RankInfo["LastID"] = ArenaData["ID"]
	if ArenaData["Players"] > RankInfo.get("MaxUsers", 0):
		RankInfo["MaxUsers"] = ArenaData["Players"]
		RankInfo["MaxUsersID"] = ArenaData["ID"]
	if ArenaData["TopScore"] > RankInfo.get("TopScore", 0):
		RankInfo["TopScore"] = ArenaData["TopScore"]
		RankInfo["TopScoreID"] = ArenaData["ID"]
		RankInfo["TopUser"] = ArenaData["#1"]

# Store rankings in files in different orders, and only partial lists for some...
def StoreRankings(RankInfo, ArenaList, Ranking, V, E, NewList, DoPlayers = False):

	ListUsernamesAll = dict()
	ListUsernamesPlots = dict()

	# 4: Print results back to json
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking.json", "w") as RankInfoFile:
		RankInfoFile.write(json.dumps(RankInfo))
		
	# 4: Re-sort rankings for proper ordering -- ONLY FULL RANKING, REST IS PARTIAL		item = (Ranking[key], Ranking[value])
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: item[1]["Score"], reverse = True)}
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking_points.ndjson", "w") as RankFile:
		for Index, UserID in enumerate(Ranking):
			Ranking[UserID]["Ranking"] = Index + 1
			RankFile.write(json.dumps(Ranking[UserID]) + "\n")
			if Index < 10:
				ListUsernamesPlots[UserID.lower()] = UserID.lower()
			if Index < 100:
				ListUsernamesAll[UserID.lower()] = UserID.lower()

	# 4: Re-sort rankings for medal-based ordering
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: item[1]["Score"], reverse = True)}
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: 100000000*item[1]["Trophies"][0] + 10000*item[1]["Trophies"][1] + item[1]["Trophies"][2], reverse = True)}
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking_trophies.ndjson", "w") as RankFile:
		for Index, UserID in enumerate(Ranking):
			Ranking[UserID]["Ranking"] = Index + 1
			RankFile.write(json.dumps(Ranking[UserID]) + "\n")
			if Index < 10:
				ListUsernamesPlots[UserID.lower()] = UserID.lower()
			if Index < 100:
				ListUsernamesAll[UserID.lower()] = UserID.lower()
			if Index == 999:
				break

	# 4: Re-sort rankings for activeness ordering
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: item[1]["Score"], reverse = True)}
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: item[1]["Events"] - item[1].get("Zeros", 0), reverse = True)}
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking_events.ndjson", "w") as RankFile:
		for Index, UserID in enumerate(Ranking):
			Ranking[UserID]["Ranking"] = Index + 1
			RankFile.write(json.dumps(Ranking[UserID]) + "\n")
			if Index < 10:
				ListUsernamesPlots[UserID.lower()] = UserID.lower()
			if Index < 100:
				ListUsernamesAll[UserID.lower()] = UserID.lower()
			if Index == 999:
				break
			
	# 4: Re-sort rankings for maximum-based ordering
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: item[1]["Score"], reverse = True)}
	Ranking = {k: v for k, v in sorted(Ranking.items(), key = lambda item: item[1]["TopScore"], reverse = True)}
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking_maximum.ndjson", "w") as RankFile:
		for Index, UserID in enumerate(Ranking):
			Ranking[UserID]["Ranking"] = Index + 1
			RankFile.write(json.dumps(Ranking[UserID]) + "\n")
			if Index < 10:
				ListUsernamesPlots[UserID.lower()] = UserID.lower()
			if Index < 100:
				ListUsernamesAll[UserID.lower()] = UserID.lower()
			if Index == 999:
				break


	if DoPlayers:
		UpdatePlayers(V, E, ListUsernamesAll, ListUsernamesPlots, RankInfo, ArenaList, Ranking, NewList)
		
		

# Given variant V and event E, update rankings for this combination
def UpdateRankings(V, E):

	NewList = []
	PrintMessage(V, E, "Running...")
	
	if (V == "all" or E == "all") and (len(TargetIDs) == 0):
		PrintMessage(V, E, "Already up to date.")
		#return None

	# 1: Skip if no detailed tournament info file found (some might not yet be downloaded)
	if (V != "all") and (E != "all") and (not os.path.exists(PathData + Folder(V, E) + V + "_" + E + ".ndjson")):
		PrintMessage(V, E, "No rankings.")
		return
	
	# 2: Create directory if it does not exist
	if not os.path.exists(PathRank + Folder(V, E)):
		PrintMessage(V, E, "Creating directory " + PathRank + Folder(V, E) + ".")
		os.makedirs(PathRank + Folder(V, E))
	
	# 3: Load previous ranking info json in RankInfo, and ranking arena list ndjson in ArenaList
	# RankInfo = {"Events": 200, "Participants": 50240, "Players": 12104, "Games": 1239052, "Moves": 2130935, ...}
	RankInfo = dict()
	if os.path.exists(PathRank + Folder(V, E) + Prefix(V, E) + "ranking.json"): 
		with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking.json", "r") as RankInfoFile:
			RankInfo = json.load(RankInfoFile)
	
	# 4: Load previous list of arenas included in the rankings in ArenaList
	# ArenaList = {"sdk340sd": {"ID": "sdk340sd", ...}, ...}
	ArenaList = dict()
	if os.path.exists(PathRank + Folder(V, E) + Prefix(V, E) + "ranking.ndjson"):	
		with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking.ndjson", "r") as RankListFile:
			for Line in RankListFile:
				ArenaData = json.loads(Line)			
				ArenaList[ArenaData["ID"]] = ArenaData
	
	# 5: Load actual previous ranking ndjson in Ranking 
	# Ranking = {"johnny": {"Ranking": 1, "Score": 5312, "Events": 123, "Username": "johnny", ...}, ..., "thijscom": {}, ...}
	Ranking = dict()
	if os.path.exists(PathRank + Folder(V, E) + Prefix(V, E) + "ranking_points.ndjson"):	
		with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking_points.ndjson", "r") as RankFile:
			UserRank = dict()
			for Line in RankFile:
				UserRank = json.loads(Line)
				Ranking[UserRank["Username"].lower()] = UserRank
	
	# 6: Checks for internal consistency of existing rankings
	if len(ArenaList) > 0:
		assert(len(Ranking) > 0), "Inconsistent ranking files. No users in rankings."
		assert("Events" in RankInfo), "Inconsistent ranking files. No entry Events in RankInfo."
		assert("FirstID" in RankInfo), "Inconsistent ranking files. No entry FirstID in RankInfo."
		assert("LastID" in RankInfo), "Inconsistent ranking files. No entry LastID in RankInfo."
		assert(RankInfo["Events"] == len(ArenaList)), f"Inconsistent ranking files. Unequal number of events. {RankInfo['Events']} != {len(ArenaList)}"
		#assert(RankInfo["FirstID"] in ArenaList), "Inconsistent ranking files. Unequal first IDs."
		#assert(RankInfo["LastID"] in ArenaList), "Inconsistent ranking files. Unequal last IDs."
	
	
	
	# 7: Scroll through more up to date tournament info file until new tournaments are found, then update from corresponding results file
	if V != "all" and E != "all":
		with open(PathData + Folder(V, E) + V + "_" + E + ".ndjson", "r") as RankListFile:
			
			# Do sanity check that last tournament in previous ranking is indeed the Nth in the tournament file (only for pure rankings)
			if ("Events" in RankInfo) and ("LastID" in RankInfo) and (V != "all") and (E != "all"):
				for i in range(RankInfo["Events"] - 1):
					next(RankListFile)
				PrintMessage(V, E, "Skipping " + str(RankInfo["Events"]) + " events...")
				ArenaInfo = json.loads(RankListFile.readline())
				assert(ArenaInfo["ID"] == RankInfo["LastID"]), "Inconsistent ranking files. Last ID does not match data file."
				
			# Process remaining lines by updating rankings
			NewProcessed = 0
			for Line in RankListFile:
				
				# Load tournament info
				ArenaData = json.loads(Line)
				#if (V == "all") or (E == "all"):
				#	if ArenaData["ID"] in ArenaList:
				#		continue
				#	else:
				#		PrintMessage(V, E, "New event: " + ArenaData["ID"] + ".")
				#		NewList.append(ArenaData)
				#else:
				PrintMessage(V, E, "New event: " + ArenaData["ID"] + ".")
				NewList.append(ArenaData)
				assert(not ArenaData["ID"] in ArenaList), "Inconsistent rankings. New tournament ID already included."
				
				# Update global statistics
				UpdateStats(RankInfo, ArenaData)
				ArenaList[ArenaData["ID"]] = ArenaData
				
				# Load tournament results
				with open(PathData + Folder(V, E) + Prefix(V, E) + ArenaData["ID"] + ".ndjson", "r") as ResultsFile:
					for Line in ResultsFile:
						UserResult = json.loads(Line)
						# UserResult: {"rank": 1, "score": 36, "rating": 2267, "username": "kasparovsabe", "title": "FM", "performance": 2454}
						UserID = UserResult["username"].lower()
						if not UserID in Ranking:
							# New player
							Ranking[UserID] = dict()
							RankInfo["Players"] = RankInfo.get("Players", 0) + 1
						
						# Update player information
						UpdatePlayer(Ranking[UserID], UserResult, ArenaData)
						Ranking[UserID]["Username"] = UserResult["username"]
				
				# Update newly processed events, and do intermediate data dumps
				NewProcessed += 1
				if NewProcessed % 1000 == 0:
					PrintMessage(V, E, "Intermediate dump after " + str(RankInfo["Events"]) + " events.")
					StoreRankings(RankInfo, ArenaList, Ranking, V, E, [], False)
	
	# For mixed rankings, use list with tournament info/IDs to fetch relevant data
	else:
		NewProcessed = 0
		for ArenaData in TargetIDs:
			if (V == "all") or (E == "all"):
				if ArenaData["ID"] in ArenaList:
					continue
				else:
					PrintMessage(V, E, "New event: " + ArenaData["ID"] + ".")
			else:
				PrintMessage(V, E, "New event: " + ArenaData["ID"] + ".")
				assert(not ArenaData["ID"] in ArenaList), "Inconsistent rankings. New tournament ID already included."
			
			# Update global statistics
			UpdateStats(RankInfo, ArenaData)
			ArenaList[ArenaData["ID"]] = ArenaData
			
			# Load tournament results
			Vx = ArenaData["Variant"]
			Ex = ArenaData["Event"]
			with open(PathData + Folder(Vx, Ex) + Prefix(Vx, Ex) + ArenaData["ID"] + ".ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					# UserResult: {"rank": 1, "score": 36, "rating": 2267, "username": "kasparovsabe", "title": "FM", "performance": 2454}
					UserID = UserResult["username"].lower()
					if not UserID in Ranking:
						# New player
						Ranking[UserID] = dict()
						RankInfo["Players"] = RankInfo.get("Players", 0) + 1
					
					# Update player information
					UpdatePlayer(Ranking[UserID], UserResult, ArenaData)
					Ranking[UserID]["Username"] = UserResult["username"]
			
			# Update newly processed events, and do intermediate data dumps
			NewProcessed += 1
			if NewProcessed % 1000 == 0:
				PrintMessage(V, E, "Intermediate dump after " + str(RankInfo["Events"]) + " events.")
				StoreRankings(RankInfo, ArenaList, Ranking, V, E, [], False)

	# 9: If we did do something, update files
	PrintMessage(V, E, "Final dump after " + str(RankInfo["Events"]) + " events.")	
	PrintMessage(V, E, "Final dump after " + str(len(ArenaList)) + " events.")	
	
	
	ArenaList = {k: v for k, v in sorted(ArenaList.items(), key = lambda item: item[1]["Start"], reverse = False)}	
	for Index, (ID, Arena) in enumerate(ArenaList.items()):
		Arena["Number"] = Index + 1
	
	StoreRankings(RankInfo, ArenaList, Ranking, V, E, NewList, True)

	# 8: Wrap up -- Check if anything happened. If not, continue
	if NewProcessed == 0:
		PrintMessage(V, E, "No new events found, so nothing to do.")	
		return
		
	
		
	# Sort all events by date (should be unnecessary) and store them in a file
	ArenaList = {k: v for k, v in sorted(ArenaList.items(), key = lambda item: item[1]["Start"], reverse = False)}
	with open(PathRank + Folder(V, E) + Prefix(V, E) + "ranking.ndjson", "w") as RankListFile:
		for Index, (ID, Arena) in enumerate(ArenaList.items()):
			Arena["Number"] = Index + 1
			RankListFile.write(json.dumps(Arena) + "\n")	

	if V != "all" and E != "all":
		return
	else:
		return
	

# Function to update the player ranking file for variant V, event EOFError
# **bullet_hourly_opperwezen.json**
# {Variant: bullet, Event: hourly, Username: opperwezen, Events: 1813, LastID: ksdlk402, CumTrophies: [17,3,1], CumPoints: 1209, CumEvents: 87, CumTopScore: 23}
# **bullet_hourly_opperwezen.ndjson**
# {Number: 93, ID: 93kdf023, Start: 2014-02-15, CumTrophies: [1,0,0], CumPoints: 23, CumEvents: 1, CumTopScore: 23}
# {Number: 105, ID: s09sdkjg, Start: 2014-02-17, CumTrophies: [2,0,0], CumPoints: 54, CumEvents: 2, CumTopScore: 31}
# ...
# {Number: 1791, ID: er0lsdk9, Start: 2018-10-03, CumTrophies: [17,3,1], CumPoints: 1209, CumEvents: 87, CumTopScore: 23}
def UpdatePlayers(V, E, ListUsernamesAll, ListUsernamesPlots, RankInfo, ArenaList, Ranking, NewList = []):
	
	# Two methods: either we need to start from scratch and go through all events or files already exist, and we only update based on new events, either via TargetIDs or by just loading ranking
	#if not os.file.exists(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + ListUsernames[0] + ".json") or not os.file.exists(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + Username + ".ndjson"):

	if not os.path.exists(PathRank + Folder(V, E) + "players\\"):
		os.makedirs(PathRank + Folder(V, E) + "players\\")
	

	

	# FOLLOWING CODE ONLY FOR WHEN STARTING FRESH OR WHEN SOME USERNAME HAS NO FILE
	
	if not os.path.exists(PathRank + Folder(V, E) + "players\\" + V + "_" + E + ".txt"):
	
		# Initialize empty JSON and NDJSON files
		UserJSON = dict()
		UserNDJSON = dict()
		for Username in ListUsernamesAll:
			UserID = Username.lower()
			UserJSON[UserID] = dict()
			UserJSON[UserID]["Variant"] = V
			UserJSON[UserID]["Event"] = E
			UserJSON[UserID]["Username"] = UserID
			UserJSON[UserID]["FirstID"] = "-"
			UserJSON[UserID]["LastID"] = "-"
			UserJSON[UserID]["CumTrophies"] = [0, 0, 0]
			UserJSON[UserID]["CumPoints"] = 0
			UserJSON[UserID]["CumEvents"] = 0
			UserJSON[UserID]["CumTopScore"] = 0
			UserNDJSON[UserID] = []
		
		# Go through all events in the ranking, and update JSON and NDJSON for this user
		ArenaList = {k: v for k, v in sorted(ArenaList.items(), key = lambda item: item[1]["Start"], reverse = False)}
		for Index, ID in enumerate(ArenaList):
			#UserJSON[UserID]["LastID"] = ID
			Vp = ArenaList[ID]["Variant"]
			Ep = ArenaList[ID]["Event"]
			with open(PathData + Folder(Vp, Ep) + Prefix(Vp, Ep) + ID + ".ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					if UserResult["username"].lower() in map(lambda x: x.lower(), ListUsernamesAll) and UserResult["score"] > 0:
						
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
						UserNDJSON[UserID].append({"Number": Index + 1, "ID": ID, "Start": ArenaList[ID]["Start"], "CumTrophies": UserJSON[UserID]["CumTrophies"].copy(), "CumPoints": UserJSON[UserID]["CumPoints"], "CumEvents": UserJSON[UserID]["CumEvents"], "CumTopScore": UserJSON[UserID]["CumTopScore"]})
						
			if Index % 1000 == 0 and Index > 0:
				PrintMessage(V, E, "Player rankings intermediate dump after " + str(Index) + " events.")

				for Username in ListUsernamesAll:
					UserID = Username.lower() 
					with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".json", "w") as JSONFile:
						json.dump(UserJSON[UserID], JSONFile)
					with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".ndjson", "w") as NDJSONFile:
						for Index in range(len(UserNDJSON[UserID])):
							NDJSONFile.write(json.dumps(UserNDJSON[UserID][Index]) + "\n")
		
		PrintMessage(V, E, "Player rankings final dump after " + str(len(ArenaList)) + " events.")
		for Username in ListUsernamesAll:
			UserID = Username.lower() 
			with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".json", "w") as JSONFile:
				json.dump(UserJSON[UserID], JSONFile)
			with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".ndjson", "w") as NDJSONFile:
				for Index in range(len(UserNDJSON[UserID])):
					NDJSONFile.write(json.dumps(UserNDJSON[UserID][Index]) + "\n")
					
		# Print list of usernames to file
		#UsernamesSorted = []
		UsernamesSorted = list(sorted(ListUsernamesAll.keys()))
		with open(PathRank + Folder(V, E) + "players\\" + V + "_" + E + ".txt", "w") as UsernameFile:
			for Username in UsernamesSorted:
				UsernameFile.write(Username.lower() + "\n")
		
		
	
	
	
	# OTHERWISE, ONLY UPDATE RANKINGS
	
	else:
	
		# file PathRank + Folder(V, E) + Prefix(V, E) + "ranking.ndjson" has not yet been updated and can be queried
		
		if len(NewList) == 0:
			PrintMessage(V, E, "No new events, nothing to do.")
			return
		
		
		# Initialize empty JSON and NDJSON files
		UserJSON = dict()
		UserNDJSON = dict()
		ListUsernamesStored = []
		
		# Load list of usernames from file
		with open(PathRank + Folder(V, E) + "players\\" + V + "_" + E + ".txt", "r") as PlayerFile:
			for Line in PlayerFile:
				ListUsernamesStored.append(Line.strip())
				
		for Username in ListUsernamesStored:
			UserID = Username.lower()			
			with open(PathRank + Folder(V, E) + "players\\" + V + "_" + E + "_" + UserID + ".json", "r") as UserInfo:
				UserJSON[UserID] = json.load(UserInfo)
			if "Events" in UserJSON:
				UserJSON.pop("Events")
			UserNDJSON[UserID] = []
			with open(PathRank + Folder(V, E) + "players\\" + V + "_" + E + "_" + UserID + ".ndjson", "r") as UserScores:
				for Line in UserScores:
					UserNDJSON[UserID].append(json.loads(Line))
			
			
		# Go through all events in the ranking, and update JSON and NDJSON for this user
		ArenaList = {k: v for k, v in sorted(ArenaList.items(), key = lambda item: item[1]["Start"], reverse = False)}
		for Index, ID in enumerate(ArenaList):
			if ID not in NewList:
				continue
			Vp = ArenaList[ID]["Variant"]
			Ep = ArenaList[ID]["Event"]
			with open(PathData + Folder(Vp, Ep) + Prefix(Vp, Ep) + ID + ".ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					if UserResult["username"].lower() in map(lambda x: x.lower(), ListUsernamesStored) and UserResult["score"] > 0:
						
						# Update JSON stats
						UserID = UserResult["username"].lower()
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
						UserNDJSON[UserID].append({"Number": Index + 1, "ID": ID, "Start": ArenaList[ID]["Start"], "CumTrophies": UserJSON[UserID]["CumTrophies"].copy(), "CumPoints": UserJSON[UserID]["CumPoints"], "CumEvents": UserJSON[UserID]["CumEvents"], "CumTopScore": UserJSON[UserID]["CumTopScore"]})
						
			if Index % 1000 == 0 and Index > 0:
				PrintMessage(V, E, "Player rankings (update) intermediate dump after " + str(Index) + " events.")

				for Username in ListUsernamesStored:
					UserID = Username.lower() 
					with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".json", "w") as JSONFile:
						json.dump(UserJSON[UserID], JSONFile)
					with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".ndjson", "w") as NDJSONFile:
						for Index in range(len(UserNDJSON[UserID])):
							NDJSONFile.write(json.dumps(UserNDJSON[UserID][Index]) + "\n")
		
		PrintMessage(V, E, "Player rankings (update) final dump after " + str(len(ArenaList)) + " events.")
		for Username in ListUsernamesStored:
			UserID = Username.lower() 
			#print(UserID)
			with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".json", "w") as JSONFile:
				json.dump(UserJSON[UserID], JSONFile)
			with open(PathRank + Folder(V, E) + "players\\" + Prefix(V, E) + UserID + ".ndjson", "w") as NDJSONFile:
				for Index in range(len(UserNDJSON[UserID])):
					NDJSONFile.write(json.dumps(UserNDJSON[UserID][Index]) + "\n")
					
		# Print list of usernames to file
		#UsernamesSorted = []
		UsernamesSorted = list(sorted(ListUsernamesStored))
		with open(PathRank + Folder(V, E) + "players\\" + V + "_" + E + ".txt", "w") as UsernameFile:
			for Username in UsernamesSorted:
				UsernameFile.write(Username.lower() + "\n")
	
	
	
	#else:
		# Update player cumulative rankings

#curyear = datetime.datetime.now().year


#######################################################################################
# Standard rankings: For each variant V and event E make rankings
#######################################################################################	

# Standard rankings: Events/Variants totals
# Approach: Load previous ranking file with arena IDs, and see which are not yet included.
# Possibility that some events last longer than others, and start earlier than other events which were already included.
# Example: Marathon starts at 1am, and hourly bullets from 2am, 3am, ... are already included before the marathon finished.
# Solution: For the last week, check IDs of events to see if they are already included in the rankings.

# TODO: More targeted update. For each pure variant and event, check for new events. Then for mixed rankings, load rankings, and only update with previously identified new events

if not os.path.exists(PathRank):
	os.makedirs(PathRank)

NewArenas = dict()
for V in Variants:
	NewArenas[V] = dict()
	for E in Events:
		#NewArenas[V][E] = []
		NewArenas[V][E] = UpdateRankings(V, E)

#for V in Variants:
#	TargetEvents = [Arena for E in Events for Arena in NewArenas[V][E]]
#	UpdateRankings(V, "all", TargetEvents)

#for E in Events:
#	TargetEvents = [Arena for V in Variants for Arena in NewArenas[V][E]]
#	UpdateRankings("all", E, TargetEvents)
	
#TargetEvents = [Arena for V in Variants for E in Events for Arena in NewArenas[V][E]]
#UpdateRankings("all", "all", TargetEvents)





print("ALL DONE!")

