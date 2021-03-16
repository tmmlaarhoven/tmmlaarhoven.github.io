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
		APIToken = Line

PathData = "E:\\lichess\\tournaments\\data\\"
PathRank = "E:\\lichess\\tournaments\\rankings\\"
PathWeb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

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

def Prefix(E, V):
	return E + "_" + V + "_"

def Folder(E, V):
	return E + "\\" + V + "\\"
	
#=========================================================================
# INPUT CHOICES
#=========================================================================

for E in Events:
	if not os.path.exists(PathData + E):
		os.makedirs(PathData + E)

	#=========================================================================
	# 1: Load tournament IDs from files
	#=========================================================================

	# Existing files may already contain all/some tournament IDs
	ArenaIDs = dict()
	for V in Variants:
		ArenaIDs[V] = []
		if os.path.exists(PathData + Folder(E, V) + E + "_" + V + ".txt"):		
			with open(PathData + Folder(E, V) + E + "_" + V + ".txt", "r") as TourFile:
				for Line in TourFile:
					ArenaIDs[V].append(Line[0:8])
					
			ArenaIDs[V].sort(key = lambda x: x.upper())
			#with open(tourlistfile, "w") as outfile:
			#	for tid in ArenaIDs[V]:
			#		outfile.write(tid + "\n")

	print(E + " - Loaded tournament IDs from files.")

	#=========================================================================
	# 2: Scrape potentially new tournament IDs from internet
	#=========================================================================	

	# Scrape webpages for tournament ids
	if not E == "titled" and not E == "marathon":

		totaltids = 0
		emptypagesinarow = 0
		print(E + " - Fetching new tournaments...")
		for page in range(1, 100000):
			
			# Special URL for elite tournaments
			if E == "elite":
				r = requests.get("https://lichess.org/tournament/history/weekend?page=" + str(page), headers = {"Authorization": "Bearer " + APIToken})		# pages start at 1
			elif E[3] == "0": # rating-restricted events
				r = requests.get("https://lichess.org/tournament/history/hourly?page=" + str(page), headers = {"Authorization": "Bearer " + APIToken})	# pages start at 1
			else:
				r = requests.get("https://lichess.org/tournament/history/" + E + "?page=" + str(page), headers = {"Authorization": "Bearer " + APIToken})	# pages start at 1
				
			# In the unlikely/impossible Events of rate limit, just indicate this and stop until the user notices
			if r.status_code == 429:
				print("RATE LIMIT!")
				time.sleep(1000000)
			
			# If no tournaments at all, quit
			if len(re.findall('/tournament/[0-9a-zA-Z]{8}">', r.text)) == 0:
				break
			
			# Partition the tournaments over the right files
			newonpage = 0
			totaltids += len(re.findall('/tournament/[0-9a-zA-Z]{8}">', r.text))
			for V in Variants:
				
				# Check for URLs on webpage of the appropriate form and title
				if E == "shield":
					tids = re.findall('/tournament/[0-9a-zA-Z]{8}"><span class="name">' + Variants[V] + ' ' + Events[E] + ' Arena', r.text)	# Shield formatting
				else:
					tids = re.findall('/tournament/[0-9a-zA-Z]{8}"><span class="name">' + Events[E] + ' ' + Variants[V] + ' Arena', r.text)	# Monthly, Weekly, Yearly, etc.
				
				# Add newly found tournament IDs to file
				for tid in tids:
					if not tid[12:20] in ArenaIDs[V]:
						ArenaIDs[V].append(tid[12:20])		# The tournament code starts on position 12 in that reg. exp.
						newonpage += 1
			
			# Count collisions to stop fetching when we have been here before
			if newonpage == 0:
				emptypagesinarow += 1
				if emptypagesinarow > (10 if E == "hourly" else 5):
					break
			else:
				emptypagesinarow = 0
			
			# Pause to avoid rate limit
			print(E + " - Page " + str(page) + " - " + str(newonpage) + " new events found.")
			if page % 2 == 0:
				#print("Finished page " + str(page) + " -- Pausing!")
				time.sleep(0.5)

	print(E + " - Scraped potentially new tournament IDs from internet.")

	#=========================================================================
	# Intermezzo: In case of quitting early, store tournament ids in file now
	#=========================================================================	

	# Store tournament IDs alphabetically for now
	for V in Variants:
		
		# Skip tournament variants for which no tournaments exist
		if len(ArenaIDs[V]) == 0:
			continue
		
		# Create directory if it does not exist
		if not os.path.exists(PathData + E + "\\" + V + "\\"):
			print(E + " - " + V + " - Creating directory " + PathData + E + "\\" + V + "\\")
			os.makedirs(PathData + E + "\\" + V + "\\")

		# If tournaments exist, store them in a file  
		ArenaIDs[V].sort(key=lambda v: v.upper())
		with open(PathData + E + "\\" + V + "\\" + E + "_" + V + ".txt", "w") as outfile:
			for tid in ArenaIDs[V]:
				outfile.write(tid + "\n")

	#=========================================================================
	# 3: Download tournament information and results files
	#=========================================================================

	# Use a dictionary with {id: date}, both in string formats
	touridinfo = dict()
		
	# Process each chess Variants one at a time
	for V in Variants:
	
		print(Prefix(E, V) + " - Running...")
		
		# Check if the list of tournament files exists and is not empty
		if len(ArenaIDs[V]) == 0:
			print(Prefix(E, V) + " - No events found.")
			continue
			
		# Create directory if it does not exist
		if not os.path.exists(PathData + Folder(E, V)):
			print(Prefix(E, V) + " - Creating directory " + PathData + Folder(E, V) + "...")
			os.makedirs(PathData + Folder(E, V))

		# Do rate limit-aware fetching of missing tournament IDs		
		APIaccess = 0
		for tid in ArenaIDs[V]:
			
			# Download results file
			if not os.path.exists(PathData + Folder(E, V) + Prefix(E, V) + tid + ".ndjson"):
				print(Prefix(E, V) + " - Downloading https://lichess.org/api/tournament/" + tid + "/results...")
				r = requests.get("https://lichess.org/api/tournament/" + tid + "/results", headers = {"Authorization": "Bearer " + APIToken})
				if r.status_code == 429:
					print("RATE LIMIT!")
					time.sleep(100000)
				with open(PathData + Folder(E, V) + Prefix(E, V) + tid + ".ndjson", "wb") as localfile:
					localfile.write(r.content)
				APIaccess += 1
				
			# Download tournament info file
			if not os.path.exists(PathData + Folder(E, V) + Prefix(E, V) + tid + ".json"):
				print(Prefix(E, V) + " - Downloading https://lichess.org/api/tournament/" + tid + "...")
				r = requests.get("https://lichess.org/api/tournament/" + tid, headers = {"Authorization": "Bearer " + APIToken})
				if r.status_code == 429:
					print("RATE LIMIT!")
					time.sleep(100000)
				with open(PathData + Folder(E, V) + Prefix(E, V) + tid + ".json", "wb") as localfile:
					localfile.write(r.content)
				APIaccess += 1
			
			# Check for many API accesses without pausing
			if APIaccess > 2:
				time.sleep(1)
				APIaccess = 0
			
		# Remove future events
		if E == "titled" or E == "marathon":
			for tid in ArenaIDs[V]:			
				with open(PathData + Folder(E, V) + "\\" + Prefix(E, V) + tid + ".json", "r") as tf:
					dictio = json.load(tf)
				if ("secondsToStart" in dictio) or not dictio.get("isFinished", False):
					ArenaIDs[V].remove(tid)
					os.remove(PathData + Folder(E, V) + "\\" + Prefix(E, V) + tid + ".ndjson")
					os.remove(PathData + Folder(E, V) + "\\" + Prefix(E, V) + tid + ".json")
					print(Prefix(E, V) + " - Removing future Events " + tid + ".")
		
		print(Prefix(E, V) + " - Finished downloading tournament information.")
		
		#=========================================================================
		# 4a: Fetch existing tournament data from ndjson
		#=========================================================================

		if os.path.exists(PathData + E + "\\" + V + "\\" + E + "_" + V + ".ndjson"):
			with open(PathData + E + "\\" + V + "\\" + E + "_" + V + ".ndjson", "r") as tfile:
				for Line in tfile:
					dictio = json.loads(Line)
					touridinfo[dictio["id"]] = dictio
		
		print(Prefix(E, V) + " - Loaded tournament info for " + str(len(touridinfo)) + " events in memory.")
		
		#=========================================================================
		# 4: Fetch tournament dates from json for chronological ordering
		#=========================================================================
		
		for tid in ArenaIDs[V]:
			# -- There was a bug due to lichess API unreachable and a corrupt file being stored...
			#if V == "crazyhouse" and E == "hourly":
			#	print(E + " - " + V + " - TID: " + tid)
			if tid in touridinfo:
				continue
			with open(PathData + Folder(E, V) + Prefix(E, V) + tid + ".json") as datfile:
				data = json.load(datfile)
				touridinfo[tid] = dict()
				touridinfo[tid]["number"] = 0
				touridinfo[tid]["mode"] = V
				touridinfo[tid]["events"] = E
				touridinfo[tid]["id"] = tid
				touridinfo[tid]["start"] = data["startsAt"]
				touridinfo[tid]["players"] = int(data["nbPlayers"])
				touridinfo[tid]["games"] = int(data["stats"]["games"])
				touridinfo[tid]["moves"] = int(data["stats"]["moves"])
				touridinfo[tid]["wwins"] = int(data["stats"]["whiteWins"])
				touridinfo[tid]["bwins"] = int(data["stats"]["blackWins"])
				touridinfo[tid]["berserks"] = int(data["stats"]["berserks"])
				touridinfo[tid]["totrating"] = touridinfo[tid]["players"] * int(data["stats"]["averageRating"])
				if len(data["podium"]) > 0:
					touridinfo[tid]["#1"] = data["podium"][0]["name"]
				else:
					touridinfo[tid]["#1"] = "???"
				if len(data["podium"]) > 1:
					touridinfo[tid]["#2"] = data["podium"][1]["name"]
				else:
					touridinfo[tid]["#2"] = "???"
				if len(data["podium"]) > 2:
					touridinfo[tid]["#3"] = data["podium"][2]["name"]
				else:
					touridinfo[tid]["#3"] = "???"
					print("Weird: " + tid)
				touridinfo[tid]["topscore"] = data["podium"][0]["score"]
		
		print(Prefix(E, V) + " - Retrieved tournament dates from json-files for chronological ordering.")
		
		#=========================================================================
		# 5: Store tournament IDs back in separate files, sorted by date
		#=========================================================================
		
		# Delete empty files as these tournament series apparently do not exist
		if len(ArenaIDs[V]) == 0:
			continue
		
		# For non-empty files, now store tournaments chronologically (with dates, csv)
		ArenaIDs[V].sort(key = lambda v: touridinfo[v]["start"])
		with open(PathData + Folder(E, V) + Prefix(E, V) + ".ndjson", "w") as outfile:
			tnum = 0
			for tid in ArenaIDs[V]:
				tnum += 1
				touridinfo[tid]["number"] = tnum
				outfile.write(json.dumps(touridinfo[tid]) + "\n")
		
		print(Prefix(E, V) + " - Stored tournament IDs with json data, chronologically.")
		
print("ALL DONE!")