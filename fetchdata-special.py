import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json

event = {
	"special": "Special"
}

#=========================================================================
# INPUT CHOICES
#=========================================================================

fpath = "E:\\lichess\\tournaments\\"

if not os.path.exists(fpath + "special\\"):
	os.makedirs(fpath + "special\\")

#=========================================================================
# 1: Load tournament IDs from files
#=========================================================================

# Existing files may already contain all/some tournament IDs
tourids = []
if os.path.exists(fpath + "special\\special.txt"):		
	with open(fpath + "special\\special.txt", "r") as tourfile:
		for line in tourfile:
			tourids.append(line[0:8])
				
		tourids.sort(key = lambda v: v.upper())

print("special - Loaded tournament IDs from files.")

#=========================================================================
# 2: Scrape potentially new tournament IDs from internet
#=========================================================================	

# Scrape webpages for tournament ids
totaltids = 0
emptypagesinarow = 0
print("special - Fetching new tournaments...")
for page in range(1, 100000):
	
	# Special URL for elite tournaments
	r = requests.get("https://lichess.org/tournament/history?page=" + str(page))
		
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
	tids = re.findall('/tournament/[0-9a-zA-Z]{8}"><span class="name">', r.text)	# Shield formatting
	
	# Add newly found tournament IDs to file
	for tid in tids:
		if not tid[12:20] in tourids:
			tourids.append(tid[12:20])		# The tournament code starts on position 12 in that reg. exp.
			newonpage += 1
	
	# Count collisions to stop fetching when we have been here before
	if newonpage == 0:
		emptypagesinarow += 1
		if emptypagesinarow > 10:
			break
	else:
		emptypagesinarow = 0
	
	# Pause to avoid rate limit
	print("special - Page " + str(page) + " - " + str(newonpage) + " new events found.")
	if page % 2 == 0:
		#print("Finished page " + str(page) + " -- Pausing!")
		time.sleep(0.5)

print("special - Scraped potentially new tournament IDs from internet.")

#=========================================================================
# Intermezzo: In case of quitting early, store tournament ids in file now
#=========================================================================

# If tournaments exist, store them in a file
tourids.sort(key = lambda v: v.upper())
with open(fpath + "special\\special.txt", "w") as outfile:
	for tid in tourids:
		outfile.write(tid + "\n")

#=========================================================================
# 3: Download tournament information and results files
#=========================================================================

# Use a dictionary with {id: date}, both in string formats
touridinfo = dict()

# Do rate limit-aware fetching of missing tournament IDs		
APIaccess = 0
for tid in tourids:
	
	# Download results file
	if not os.path.exists(fpath + "special\\special_" + tid + ".ndjson"):
		print("special - Downloading https://lichess.org/api/tournament/" + tid + "/results...")
		r = requests.get("https://lichess.org/api/tournament/" + tid + "/results")
		if r.status_code == 429:
			print("RATE LIMIT!")
			time.sleep(100000)
		with open(fpath + "special\\special_" + tid + ".ndjson", "wb") as localfile:
			localfile.write(r.content)
		APIaccess += 1
		
	# Download tournament info file
	if not os.path.exists(fpath + "special\\special_" + tid + ".json"):
		print("special - Downloading https://lichess.org/api/tournament/" + tid + "...")
		r = requests.get("https://lichess.org/api/tournament/" + tid)
		if r.status_code == 429:
			print("RATE LIMIT!")
			time.sleep(100000)
		with open(fpath + "special\\special_" + tid + ".json", "wb") as localfile:
			localfile.write(r.content)
		APIaccess += 1
	
	# Check for many API accesses without pausing
	if APIaccess > 2:
		time.sleep(1)
		APIaccess = 0

print("special - Finished downloading tournament information.")

#=========================================================================
# 4: Fetch tournament dates from json for chronological ordering
#=========================================================================

touridinfo = dict()
for tid in tourids:
	with open(fpath + "special\\special_" + tid + ".json") as datfile:
		data = json.load(datfile)
		touridinfo[tid] = dict()
		touridinfo[tid]["number"] = 0
		touridinfo[tid]["id"] = tid
		touridinfo[tid]["name"] = data["fullName"]
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

print("special - Retrieved tournament dates from json-files for chronological ordering.")

#=========================================================================
# 5: Store tournament IDs back in separate files, sorted by date
#=========================================================================

# For non-empty files, now store tournaments chronologically (with dates, csv)
tourids.sort(key = lambda v: touridinfo[v]["start"])
with open(fpath + "special\\special.ndjson", "w") as outfile:
	tnum = 0
	for tid in tourids:
		tnum += 1
		touridinfo[tid]["number"] = tnum
		outfile.write(json.dumps(touridinfo[tid]) + "\n")

print("special - Stored tournament IDs with json data, chronologically.")
		
print("ALL DONE!")