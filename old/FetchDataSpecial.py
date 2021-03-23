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

Events = {
	"special": "Special"
}

def Prefix(V, E):
	return V + "_" + E + "_"

def Folder(V, E):
	return V + "\\" + E + "\\"
	
def PrintMessage(V, E, Message):
	print("{:<11}".format(V) + " - {:<8}".format(E) + " - " + Message)

#=========================================================================
# INPUT CHOICES
#=========================================================================

if not os.path.exists(PathData + "special"):
	os.makedirs(PathData + "special")

#=========================================================================
# 1: Load tournament IDs from files
#=========================================================================

# Existing files may already contain all/some tournament IDs
ArenaIDs = []
if os.path.exists(PathData + "special\\special.txt"):		
	with open(PathData + "special\\special.txt", "r") as IDFile:
		for Line in IDFile:
			ArenaIDs.append(Line[0:8])
				
		ArenaIDs.sort(key = lambda ID: ID.upper())

PrintMessage("all", "special", "Loaded tournament IDs from files.")

#=========================================================================
# 2: Scrape potentially new tournament IDs from internet
#=========================================================================	

# Scrape webpages for tournament ids
TotalIDs = 0
EmptyPages = 0
PrintMessage("all", "special", "Fetching new tournaments...")
for Page in range(1, 100000):
	
	# Special URL for elite tournaments
	r = requests.get("https://lichess.org/tournament/history?page=" + str(Page), headers = {"Authorization": "Bearer " + APIToken})
		
	# In the unlikely/impossible Events of rate limit, just indicate this and stop until the user notices
	if r.status_code == 429:
		print("RATE LIMIT!")
		time.sleep(1000000)
	
	# If no tournaments at all, quit
	if len(re.findall('/tournament/[0-9a-zA-Z]{8}">', r.text)) == 0:
		break
	
	# Partition the tournaments over the right files
	NewOnPage = 0
	TotalIDs += len(re.findall('/tournament/[0-9a-zA-Z]{8}">', r.text))
	IDs = re.findall('/tournament/[0-9a-zA-Z]{8}"><span class="name">', r.text)	# Shield formatting
	
	# Add newly found tournament IDs to file
	for ID in IDs:
		if not ID[12:20] in ArenaIDs:
			ArenaIDs.append(ID[12:20])		# The tournament code starts on position 12 in that reg. exp.
			NewOnPage += 1
	
	# Count collisions to stop fetching when we have been here before
	if NewOnPage == 0:
		EmptyPages += 1
		if EmptyPages > 10:
			break
	else:
		EmptyPages = 0
	
	# Pause to avoid rate limit
	PrintMessage("special - Page " + str(Page) + " - " + str(NewOnPage) + " new events found.")
	if Page % 2 == 0:
		#print("Finished Page " + str(Page) + " -- Pausing!")
		time.sleep(1)

print("special - Scraped potentially new tournament IDs from internet.")

#=========================================================================
# Intermezzo: In case of quitting early, store tournament ids in file now
#=========================================================================

# If tournaments exist, store them in a file
ArenaIDs.sort(key = lambda ID: v.upper())
with open(PathData + "special\\special.txt", "w") as IDFile:
	for ID in ArenaIDs:
		IDFile.write(ID + "\n")

#=========================================================================
# 3: Download tournament information and results files
#=========================================================================

# Do rate limit-aware fetching of missing tournament IDs		
APIRequests = 0
for ID in ArenaIDs:
	
	# Download results file
	if not os.path.exists(PathData + "special\\special_" + ID + ".ndjson"):
		print("special - Downloading https://lichess.org/api/tournament/" + ID + "/results...")
		r = requests.get("https://lichess.org/api/tournament/" + ID + "/results", headers = {"Authorization": "Bearer " + APIToken})
		if r.status_code == 429:
			print("RATE LIMIT!")
			time.sleep(100000)
		with open(PathData + "special\\special_" + ID + ".ndjson", "wb") as ResultsFile:
			ResultsFile.write(r.content)
		APIRequests += 1
		
	# Download tournament info file
	if not os.path.exists(PathData + "special\\special_" + ID + ".json"):
		print("special - Downloading https://lichess.org/api/tournament/" + ID + "...", headers = {"Authorization": "Bearer " + APIToken})
		r = requests.get("https://lichess.org/api/tournament/" + ID)
		if r.status_code == 429:
			print("RATE LIMIT!")
			time.sleep(100000)
		with open(PathData + "special\\special_" + ID + ".json", "wb") as ArenaFile:
			ArenaFile.write(r.content)
		APIRequests += 1
	
	# Check for many API accesses without pausing
	if APIRequests > 2:
		time.sleep(1)
		APIRequests = 0

print("special - Finished downloading tournament information.")

#=========================================================================
# 4aa: Compute total points, if not stored in json file
#=========================================================================		

for ID in ArenaIDs:
	with open(PathData + "special\\special_" + ID + ".json", "r") as ArenaFile:
		ArenaInfo = json.load(ArenaFile)
	if not "stats" in ArenaInfo:
		ArenaInfo["stats"] = dict()
	if "points" in ArenaInfo["stats"]:
		continue
	with open(PathData + "special\\special_" + ID + ".ndjson", "r") as ResultsFile:
		TotalPoints = 0
		for Line in ResultsInfo:
			ArenaResults = json.loads(Line)
			TotalPoints += ArenaResults.get("score", 0)
	ArenaInfo["stats"]["points"] = TotalPoints
	with open(PathData + "special\\special_" + ID + ".json", "w") as ArenaFile:
		DataFile.write(json.dumps(ArenaInfo))
				
#=========================================================================
# 4: Fetch tournament dates from json for chronological ordering
#=========================================================================
				
ArenaData = dict()
for ID in ArenaIDs:
	with open(PathData + "special\\special_" + ID + ".json", "r") as ArenaFile:
		ArenaInfo = json.load(ArenaFile)
	ArenaData[ID] = dict()
	ArenaData[ID]["Number"] = 0
	ArenaData[ID]["ID"] = ID
	ArenaData[ID]["Name"] = ArenaInfo["fullName"]
	ArenaData[ID]["Start"] = ArenaInfo["startsAt"]
	ArenaData[ID]["Players"] = int(ArenaInfo["nbPlayers"])
	ArenaData[ID]["Games"] = int(ArenaInfo["stats"]["games"])
	ArenaData[ID]["Moves"] = int(ArenaInfo["stats"]["moves"])
	ArenaData[ID]["WhiteWins"] = int(ArenaInfo["stats"]["whiteWins"])
	ArenaData[ID]["BlackWins"] = int(ArenaInfo["stats"]["blackWins"])
	ArenaData[ID]["Berserks"] = int(ArenaInfo["stats"]["berserks"])
	ArenaData[ID]["TotalPoints"] = int(ArenaInfo["stats"]["points"])
	ArenaData[ID]["TotalRating"] = ArenaData[ID]["Players"] * int(ArenaInfo["stats"]["averageRating"])
	ArenaData[ID]["#1"] = ("???" if len(ArenaInfo["podium"]) == 0 else ArenaInfo["podium"][0]["name"])
	ArenaData[ID]["#2"] = ("???" if len(ArenaInfo["podium"]) <= 1 else ArenaInfo["podium"][1]["name"])
	ArenaData[ID]["#3"] = ("???" if len(ArenaInfo["podium"]) <= 2 else ArenaInfo["podium"][2]["name"])
	ArenaData[ID]["TopScore"] = (0 if len(ArenaInfo["podium"]) == 0 else ArenaInfo["podium"][0]["score"])

print("special - Retrieved tournament dates from json-files for chronological ordering.")

#=========================================================================
# 5: Store tournament IDs back in separate files, sorted by date
#=========================================================================

# For non-empty files, now store tournaments chronologically (with dates, csv)
ArenaIDs.sort(key = lambda ID: ArenaData[ID]["Start"])
with open(PathData + "special\\special.ndjson", "w") as DataFile:
	Number = 0
	for ID in ArenaIDs:
		Number += 1
		ArenaData[ID]["Number"] = Number
		DataFile.write(json.dumps(ArenaData[ID]) + "\n")

print("special - Stored tournament IDs with json data, chronologically.")
		
print("ALL DONE!")