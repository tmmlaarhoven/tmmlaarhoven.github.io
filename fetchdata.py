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
	"marathon": "Marathon",
	"liga": "Liga"
}

def Prefix(V, E):
	return f"{V}_{E}_"

def Folder(V, E):
	return f"{V}\\{E}\\"
	
def PrintMessage(V, E, Message):
	print(f"{V:<11} - {E:<8} - {Message}")
	
#=========================================================================
# Process each event type separately
#=========================================================================

ArenaIDs = dict()
for V in Variants:
	ArenaIDs[V] = dict()
	for E in Events:
		ArenaIDs[V][E] = []

for E in Events:
	#if not os.path.exists(PathData + E):
	#	os.makedirs(PathData + E)

	#=========================================================================
	# 1. Load tournament IDs from files
	#=========================================================================

	# Existing files may already contain all/some tournament IDs
	for V in Variants:
		if os.path.exists(f"{PathData}{Folder(V, E)}{V}_{E}.txt"):		
			with open(f"{PathData}{Folder(V, E)}{V}_{E}.txt", "r") as IDFile:
				for Line in IDFile:
					ArenaIDs[V][E].append(Line[0:8])				
			ArenaIDs[V][E].sort(key = lambda ID: ID.upper())
		PrintMessage(V, E, f"Loaded {len(ArenaIDs[V][E])} tournament IDs from file.")

	#=========================================================================
	# 2. Scrape potentially new tournament IDs from internet
	#=========================================================================	

	# Scrape webpages for tournament ids
	#if (E == "liga"):
	
	#	pass
	
		# TotalIDs = 0
		# EmptyPages = 0
		# PrintMessage("all", E, "Fetching new tournaments...")
		
		# for Page in range(1, 100000):
			
			# r = requests.get(f"https://lichess.org/@/jeffforever/tournaments/created?page={Page}", headers = {"Authorization": f"Bearer {APIToken}"})		# pages start at 1
				
			# # In the unlikely/impossible Events of rate limit, just indicate this and stop until the user notices
			# if r.status_code == 429:
				# print("RATE LIMIT!")
				# time.sleep(1000000)
			
			# # If no tournaments at all, quit
			# if len(re.findall("/tournament/[0-9a-zA-Z]{8}\">", r.text)) == 0:
				# break
			
			# # Partition the tournaments over the right files
			# NewOnPage = 0
			# TotalIDs += len(re.findall("/tournament/[0-9a-zA-Z]{8}\">", r.text))
			# IDs = re.findall(f"/tournament/[0-9a-zA-Z]{{8}}\"><span class=\"name\">", r.text)
				
			# # Add newly found tournament IDs to file
			# for ID in IDs:		# ID: '/tournament/d09wfkjs">...', need entries 12-19
			
				# RealID = ID[12:20]
				# PosInText = r.text.find(RealID)
				# TimeControlPos = r.text.find("+", PosInText) - 1
				# TimeControl = r.text[TimeControlPos:TimeControlPos+3]
				# if TimeControl == "3+0":
					# V == "superblitz"
				# else:
					# V == "blitz"
					
				# if not RealID in ArenaIDs[V][E]:
					# ArenaIDs[V][E].append(RealID)
					# NewOnPage += 1
			
			# # Count collisions to stop fetching when we do not find new entries
			# PrintMessage("all", E, f"Page {Page} - {NewOnPage} new events found.")
			# if NewOnPage == 0:
				# EmptyPages += 1
				# if EmptyPages >= 5:
					# break
			# else:
				# EmptyPages = 0
			
			# # Pause to avoid rate limit
			# if Page % 2 == 0:
				# time.sleep(1)
	
	
		# pass
	
	if (not E == "titled") and (not E == "marathon") and not (E == "liga"):

		TotalIDs = 0
		EmptyPages = 0
		PrintMessage("all", E, "Fetching new tournaments...")
		
		for Page in range(1, 100000):
			
			if E == "elite":	# Special URL for elite tournaments
				r = requests.get(f"https://lichess.org/tournament/history/weekend?page={Page}", headers = {"Authorization": f"Bearer {APIToken}"})		# pages start at 1
			elif E[3] == "0": 	# Rating-restricted hourly events
				r = requests.get(f"https://lichess.org/tournament/history/hourly?page={Page}", headers = {"Authorization": f"Bearer {APIToken}"})	# pages start at 1
			else:				# All other events
				r = requests.get(f"https://lichess.org/tournament/history/{E}?page={Page}", headers = {"Authorization": f"Bearer {APIToken}"})	# pages start at 1
				
			# In the unlikely/impossible Events of rate limit, just indicate this and stop until the user notices
			if r.status_code == 429:
				print("RATE LIMIT!")
				time.sleep(1000000)
			
			# If no tournaments at all, quit
			if len(re.findall("/tournament/[0-9a-zA-Z]{8}\">", r.text)) == 0:
				break
			
			# Partition the tournaments over the right files
			NewOnPage = 0
			TotalIDs += len(re.findall("/tournament/[0-9a-zA-Z]{8}\">", r.text))
			for V in Variants:
				
				if E == "shield":		# Format on webpage for shield events
					IDs = re.findall(f"/tournament/[0-9a-zA-Z]{{8}}\"><span class=\"name\">{Variants[V]} {Events[E]} Arena", r.text)	# Shield formatting
				else:					# Format on webpage for all other events
					IDs = re.findall(f"/tournament/[0-9a-zA-Z]{{8}}\"><span class=\"name\">{Events[E]} {Variants[V]} Arena", r.text)	# Monthly, Weekly, Yearly, etc.
				
				# Add newly found tournament IDs to file
				for ID in IDs:		# ID: '/tournament/d09wfkjs">...', need entries 12-19
					if not ID[12:20] in ArenaIDs[V][E]:
						ArenaIDs[V][E].append(ID[12:20])
						NewOnPage += 1
			
			# Count collisions to stop fetching when we do not find new entries
			PrintMessage("all", E, f"Page {Page} - {NewOnPage} new events found.")
			if NewOnPage == 0:
				EmptyPages += 1
				if EmptyPages >= 5:
					break
			else:
				EmptyPages = 0
			
			# Pause to avoid rate limit
			if Page % 2 == 0:
				time.sleep(1)

	PrintMessage("all", E, "Scraped potentially new tournament IDs from internet.")

	#=========================================================================
	# 3. Intermezzo: In case of quitting early, store tournament ids in file now
	#=========================================================================	

	# Store tournament IDs alphabetically for now
	for V in Variants:
		
		# Skip tournament variants for which no tournaments exist
		if len(ArenaIDs[V][E]) == 0:
			continue
		
		# Create directory if it does not exist
		if not os.path.exists(PathData + Folder(V, E)):
			PrintMessage(V, E, f"Creating directory {PathData}{Folder(V, E)}.")
			os.makedirs(f"{PathData}{Folder(V, E)}")

		# If tournaments exist, store them in a file (alphabetically)
		ArenaIDs[V][E].sort(key = lambda ID: ID.upper())
		with open(f"{PathData}{Folder(V, E)}{V}_{E}.txt", "w") as IDFile:
			for ID in ArenaIDs[V][E]:
				IDFile.write(f"{ID}\n")

	#=========================================================================
	# 4. Download tournament information and results files
	#=========================================================================

	# Use a dictionary with {id: date}, both in string formats
	ArenaData = dict()
		
	# Process each chess Variants one at a time
	for V in Variants:
	
		PrintMessage(V, E, "Running...")
		
		# Check if the list of tournament files exists and is not empty
		if len(ArenaIDs[V][E]) == 0:
			PrintMessage(V, E, "No events found.")
			continue
			
		# Create directory if it does not exist
		if not os.path.exists(PathData + Folder(V, E)):
			PrintMessage(V, E, f"Creating directory {PathData}{Folder(V, E)}...")
			os.makedirs(PathData + Folder(V, E))

		#=========================================================================
		# 4a. Fetch the missing files via the API
		#=========================================================================		
		
		# Do rate limit-aware fetching of missing tournament IDs		
		APIRequests = 0
		for ID in ArenaIDs[V][E]:
			
			# Download results file
			if not os.path.exists(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.ndjson"):
				PrintMessage(V, E, f"Downloading https://lichess.org/api/tournament/{ID}/results...")
				r = requests.get(f"https://lichess.org/api/tournament/{ID}/results", headers = {"Authorization": f"Bearer {APIToken}"})
				if r.status_code == 429:
					print("RATE LIMIT!")
					time.sleep(100000)
				with open(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.ndjson", "wb") as ArenaResultsFile:
					ArenaResultsFile.write(r.content)
				APIRequests += 1
				
			# Download tournament info file
			if not os.path.exists(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json"):
				PrintMessage(V, E, f"Downloading https://lichess.org/api/tournament/{ID}...")
				r = requests.get(f"https://lichess.org/api/tournament/{ID}", headers = {"Authorization": f"Bearer {APIToken}"})
				if r.status_code == 429:
					print("RATE LIMIT!")
					time.sleep(100000)
				with open(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json", "wb") as ArenaInfoFile:
					ArenaInfoFile.write(r.content)
				APIRequests += 1
			
			# Check for many API accesses without pausing
			if APIRequests > 2:
				time.sleep(1)
				APIRequests = 0
			
		# Remove future events
		if E == "titled" or E == "marathon" or E == "liga":
			for ID in ArenaIDs[V][E]:			
				if os.path.exists(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json"):
					with open(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json", "r", encoding = "utf-8") as ArenaInfoFile:
						#print(ID)
						ArenaInfo = json.load(ArenaInfoFile)
					if ("secondsToStart" in ArenaInfo) or not ArenaInfo.get("isFinished", False):
						ArenaIDs[V][E].remove(ID)
						os.remove(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.ndjson")
						os.remove(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json")
						PrintMessage(V, E, f"Removing future/unfinished event {ID}.")
		
		PrintMessage(V, E, "Finished downloading tournament information.")
		
		#=========================================================================
		# 4b. Fetch existing tournament data from ndjson
		#=========================================================================

		if os.path.exists(f"{PathData}{Folder(V, E)}{V}_{E}.ndjson"):
			with open(f"{PathData}{Folder(V, E)}{V}_{E}.ndjson", "r") as DataFile:
				for Line in DataFile:
					ArenaInfo = json.loads(Line)

					# Update total point count, if not available, for previously stored files
					if ("TotalPoints" in ArenaInfo):
						ArenaData[ArenaInfo["ID"]] = ArenaInfo	# New, capitalized format
						continue

					# stuck in old format from API file
					# SHOULD NEVER GET HERE
					PrintMessage(V, E, f'Computing missing total points for tournament {ArenaInfo["kappa"]} with ID {ArenaInfo["id"]}.')
					#print(ArenaInfo["id"])
					with open(f'{PathData}{Folder(V, E)}{Prefix(V, E)}{ArenaInfo["id"]}.json', "r") as ArenaInfoFile:
						ArenaInfo = json.load(ArenaInfoFile) 	# Old, API format
					if not "stats" in ArenaInfo:
						ArenaInfo["stats"] = dict()
					with open(f'{PathData}{Folder(V, E)}{Prefix(V, E)}{ArenaInfo["id"]}.ndjson', "r") as ArenaResultsFile:
						TotalPoints = 0
						for Line in ArenaResultsFile:
							ArenaResults = json.loads(Line)
							TotalPoints += ArenaResults.get("score", 0)
					ArenaInfo["stats"]["points"] = TotalPoints
					with open(f'{PathData}{Folder(V, E)}{Prefix(V, E)}{ArenaInfo["id"]}.json', "w") as ArenaInfoFile:
						ArenaInfoFile.write(json.dumps(ArenaInfo))	
					#print(Prefix(V, E) + " - Computed missing total points for tournament " + ArenaInfo["id"] + ".")
		
		PrintMessage(V, E, f"Loaded tournament info for {len(ArenaData)} events in memory.")
		
		#=========================================================================
		# 4c. Fetch tournament dates from json for chronological ordering
		#=========================================================================
		
		for ID in ArenaIDs[V][E]:
			# -- There was a bug due to lichess API unreachable and a corrupt file being stored...
			#if V == "crazyhouse" and E == "hourly":
			#	print(E + " - " + V + " - TID: " + ID)
			if ID in ArenaData:
				continue
			with open(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json", "r", encoding = "utf-8") as ArenaInfoFile:
				ArenaInfo = json.load(ArenaInfoFile)
			
			if not ("points" in ArenaInfo.get("stats", {})):
				if not "stats" in ArenaInfo:
					ArenaInfo["stats"] = dict()
				with open(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.ndjson", "r") as ArenaResultsFile:
					TotalPoints = 0
					for Line in ArenaResultsFile:
						ArenaResults = json.loads(Line)
						TotalPoints += ArenaResults.get("score", 0)
				ArenaInfo["stats"]["points"] = TotalPoints
				with open(f"{PathData}{Folder(V, E)}{Prefix(V, E)}{ID}.json", "w") as ArenaInfoFile:
					ArenaInfoFile.write(json.dumps(ArenaInfo))	
				PrintMessage(V, E, f'Computed missing total points for tournament {ArenaInfo["id"]}.')
			
			ArenaData[ID] = dict()
			ArenaData[ID]["Number"] = 0
			ArenaData[ID]["Variant"] = V
			ArenaData[ID]["Event"] = E
			ArenaData[ID]["ID"] = ID
			ArenaData[ID]["Start"] = ArenaInfo["startsAt"]
			ArenaData[ID]["Players"] = int(ArenaInfo["nbPlayers"])
			ArenaData[ID]["Games"] = int(ArenaInfo.get("stats", {}).get("games", 0))
			ArenaData[ID]["Moves"] = int(ArenaInfo.get("stats", {}).get("moves", 0))
			ArenaData[ID]["WhiteWins"] = int(ArenaInfo.get("stats", {}).get("whiteWins", 0))
			ArenaData[ID]["BlackWins"] = int(ArenaInfo.get("stats", {}).get("blackWins", 0))
			ArenaData[ID]["Berserks"] = int(ArenaInfo.get("stats", {}).get("berserks", 0))
			ArenaData[ID]["TotalPoints"] = int(ArenaInfo.get("stats", {}).get("points", 0))
			ArenaData[ID]["TotalRating"] = ArenaData[ID]["Players"] * int(ArenaInfo.get("stats", {}).get("averageRating", 0))
			ArenaData[ID]["#1"] = ("???" if len(ArenaInfo.get("podium", [])) == 0 else ArenaInfo["podium"][0]["name"])
			ArenaData[ID]["#2"] = ("???" if len(ArenaInfo.get("podium", [])) <= 1 else ArenaInfo["podium"][1]["name"])
			ArenaData[ID]["#3"] = ("???" if len(ArenaInfo.get("podium", [])) <= 2 else ArenaInfo["podium"][2]["name"])
			ArenaData[ID]["TopScore"] = (0 if len(ArenaInfo.get("podium", [])) == 0 else ArenaInfo["podium"][0]["score"])
		
		PrintMessage(V, E, "Retrieved tournament dates from json-files for chronological ordering.")
		
		#=========================================================================
		# 4d. Store tournament IDs back in separate files, sorted by date
		#=========================================================================
		
		# Delete empty files as these tournament series apparently do not exist
		if len(ArenaIDs[V][E]) == 0:
			continue
		
		# For non-empty files, now store tournaments chronologically (with dates, csv)
		ArenaIDs[V][E].sort(key = lambda ID: ArenaData[ID]["Start"])
		with open(f"{PathData}{Folder(V, E)}{V}_{E}.ndjson", "w") as DataFile:
			Number = 0
			for ID in ArenaIDs[V][E]:
				Number += 1
				ArenaData[ID]["Number"] = Number
				DataFile.write(json.dumps(ArenaData[ID]) + "\n")
		
		PrintMessage(V, E, "Stored tournament IDs with json data, chronologically.")
		
	PrintMessage("all", E, f"Finished processing {E} events.\n")
		
print("ALL DONE!")