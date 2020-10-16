import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json

event = {
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

mode = {
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
	
#mode = {"bullet": "Bullet"}

#=========================================================================
# INPUT CHOICES
#=========================================================================

#ev = "hourly"
fpath = "E:\\lichess\\tournaments\\"

#=========================================================================

for ev in event:
	if not os.path.exists(fpath + ev):
		os.makedirs(fpath + ev)

	#=========================================================================
	# 1: Load tournament IDs from files
	#=========================================================================

	# Existing files may already contain all/some tournament IDs
	tourids = dict()
	tourlistfiles = dict()
	for mo in mode:
		tourids[mo] = []
		tourlistfiles[mo] = fpath + ev + "\\" + ev + "_" + mo + "_tournaments.txt"
		if os.path.exists(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".txt"):		
			with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".txt", "r") as tourfile:
				for line in tourfile:
					tourids[mo].append(line[0:8])
					
			tourids[mo].sort(key=lambda v: v.upper())
			#with open(tourlistfile, "w") as outfile:
			#	for tid in tourids[mo]:
			#		outfile.write(tid + "\n")

	print(ev + " - Loaded tournament IDs from files.")

	#=========================================================================
	# 2: Scrape potentially new tournament IDs from internet
	#=========================================================================	

	# Scrape webpages for tournament ids
	if not ev == "titled" and not ev == "marathon":

		totaltids = 0
		emptypagesinarow = 0
		print(ev + " - Fetching new tournaments...")
		for page in range(1, 100000):
			
			# Special URL for elite tournaments
			if ev == "elite":
				r = requests.get("https://lichess.org/tournament/history/weekend?page=" + str(page))		# pages start at 1
			else:
				r = requests.get("https://lichess.org/tournament/history/" + ev + "?page=" + str(page))	# pages start at 1
			
			# In the unlikely/impossible event of rate limit, just indicate this and stop until the user notices
			if r.status_code == 429:
				print("RATE LIMIT!")
				time.sleep(1000000)
			
			# If no tournaments at all, quit
			if len(re.findall('/tournament/[0-9a-zA-Z]{8}">', r.text)) == 0:
				break
			
			# Partition the tournaments over the right files
			newonpage = 0
			totaltids += len(re.findall('/tournament/[0-9a-zA-Z]{8}">', r.text))
			for mo in mode:
				
				# Check for URLs on webpage of the appropriate form and title
				if ev == "shield":
					tids = re.findall('/tournament/[0-9a-zA-Z]{8}"><span class="name">' + mode[mo] + ' ' + event[ev] + ' Arena', r.text)	# Shield formatting
				else:
					tids = re.findall('/tournament/[0-9a-zA-Z]{8}"><span class="name">' + event[ev] + ' ' + mode[mo] + ' Arena', r.text)	# Monthly, Weekly, Yearly, etc.
				
				# Add newly found tournament IDs to file
				for tid in tids:
					if not tid[12:20] in tourids[mo]:
						tourids[mo].append(tid[12:20])		# The tournament code starts on position 12 in that reg. exp.
						newonpage += 1
			
			# Count collisions to stop fetching when we have been here before
			if newonpage == 0:
				emptypagesinarow += 1
				if emptypagesinarow > (10 if ev == "hourly" else 5):
					break
			else:
				emptypagesinarow = 0
			
			# Pause to avoid rate limit
			print(ev + " - Page " + str(page) + " - " + str(newonpage) + " new events found.")
			if page % 2 == 0:
				#print("Finished page " + str(page) + " -- Pausing!")
				time.sleep(0.5)

	print(ev + " - Scraped potentially new tournament IDs from internet.")

	#=========================================================================
	# Intermezzo: In case of quitting early, store tournament ids in file now
	#=========================================================================	

	# Store tournament IDs alphabetically for now
	for mo in mode:
		
		# Skip tournament modes for which no tournaments exist
		if len(tourids[mo]) == 0:
			if os.path.exists(tourlistfiles[mo]):
				os.remove(tourlistfiles[mo])
			continue
		
		# Create directory if it does not exist
		if not os.path.exists(fpath + ev + "\\" + mo + "\\"):
			print(ev + " - " + mo + " - Creating directory " + fpath + folder)
			os.makedirs(fpath + ev + "\\" + mo + "\\")

		# If tournaments exist, store them in a file  
		tourids[mo].sort(key=lambda v: v.upper())
		with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".txt", "w") as outfile:
			for tid in tourids[mo]:
				outfile.write(tid + "\n")

	#=========================================================================
	# 3: Download tournament information and results files
	#=========================================================================

	# Use a dictionary with {id: date}, both in string formats
	touridinfo = dict()
		
	# Process each chess variant one at a time
	for mo in mode:
	
		print(ev + " - " + mo + " - Running...")
	
		pref = ev + "_" + mo + "_"
		folder = ev + "\\" + mo
		
		# Check if the list of tournament files exists and is not empty
		if len(tourids[mo]) == 0:
			print(ev + " - " + mo + " - No events found.")
			continue
			
		# Create directory if it does not exist
		if not os.path.exists(fpath + ev + "\\" + mo + "\\"):
			print(ev + " - " + mo + " - Creating directory " + fpath + folder + "...")
			os.makedirs(fpath + ev + "\\" + mo + "\\")

		# Do rate limit-aware fetching of missing tournament IDs		
		APIaccess = 0
		for tid in tourids[mo]:
			
			# Download results file
			if not os.path.exists(fpath + folder + "\\" + pref + tid + ".ndjson"):
				print(ev + " - " + mo + " - Downloading https://lichess.org/api/tournament/" + tid + "/results...")
				r = requests.get("https://lichess.org/api/tournament/" + tid + "/results")
				if r.status_code == 429:
					print("RATE LIMIT!")
					time.sleep(100000)
				with open(fpath + folder + "\\" + pref + tid + ".ndjson", "wb") as localfile:
					localfile.write(r.content)
				APIaccess += 1
				
			# Download tournament info file
			if not os.path.exists(fpath + folder + "\\" + pref + tid + ".json"):
				print(ev + " - " + mo + " - Downloading https://lichess.org/api/tournament/" + tid + "...")
				r = requests.get("https://lichess.org/api/tournament/" + tid)
				if r.status_code == 429:
					print("RATE LIMIT!")
					time.sleep(100000)
				with open(fpath + folder + "\\" + pref + tid + ".json", "wb") as localfile:
					localfile.write(r.content)
				APIaccess += 1
			
			# Check for many API accesses without pausing
			if APIaccess > 2:
				time.sleep(1)
				APIaccess = 0
			
		# Remove future events
		if ev == "titled" or ev == "marathon":
			for tid in tourids[mo]:			
				with open(fpath + folder + "\\" + pref + tid + ".json", "r") as tf:
					dictio = json.load(tf)
				if ("secondsToStart" in dictio) or not dictio.get("isFinished", False):
					tourids[mo].remove(tid)
					os.remove(fpath + folder + "\\" + pref + tid + ".ndjson")
					os.remove(fpath + folder + "\\" + pref + tid + ".json")
					print(ev + " - " + mo + " - Removing future event " + tid + ".")
		
		print(ev + " - " + mo + " - Finished downloading tournament information.")
		
		#=========================================================================
		# 4a: Fetch existing tournament data from ndjson
		#=========================================================================

		if os.path.exists(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson"):
			with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson", "r") as tfile:
				for line in tfile:
					dictio = json.loads(line)
					touridinfo[dictio["id"]] = dictio
		
		print(ev + " - " + mo + " - Loaded tournament info for " + str(len(touridinfo)) + " events in memory.")
		
		#=========================================================================
		# 4: Fetch tournament dates from json for chronological ordering
		#=========================================================================
		
		for tid in tourids[mo]:
			if tid in touridinfo:
				continue
			with open(fpath + folder + "\\" + pref + tid + ".json") as datfile:
				data = json.load(datfile)
				touridinfo[tid] = dict()
				touridinfo[tid]["number"] = 0
				touridinfo[tid]["mode"] = mo
				touridinfo[tid]["event"] = ev
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
		
		print(ev + " - " + mo + " - Retrieved tournament dates from json-files for chronological ordering.")
		
		#=========================================================================
		# 5: Store tournament IDs back in separate files, sorted by date
		#=========================================================================
		
		# Delete empty files as these tournament series apparently do not exist
		if len(tourids[mo]) == 0:
			if os.path.exists(tourlistfiles[mo]):
				os.remove(tourlistfiles[mo])
			continue
		
		# For non-empty files, now store tournaments chronologically (with dates, csv)
		tourids[mo].sort(key = lambda v: touridinfo[v]["start"])
		with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson", "w") as outfile:
			tnum = 0
			for tid in tourids[mo]:
				tnum += 1
				touridinfo[tid]["number"] = tnum
				outfile.write(json.dumps(touridinfo[tid]) + "\n")
		
		print(ev + " - " + mo + " - Stored tournament IDs with json data, chronologically.")
		
print("ALL DONE!")