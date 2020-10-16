import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json
import datetime

# Update ranking information for a player based on new ranking information
def updateplayer(udata, prank, tdata):
	udata["ranking"] = 0
	udata["score"] = udata.get("score", 0) + prank["score"]
	udata["events"] = udata.get("events", 0) + 1
	if not "first" in udata:
		udata["first"] = tdata["start"]
		udata["firstid"] = tdata["id"]
	udata["last"] = tdata["start"]
	udata["lastid"] = tdata["id"]
	if prank["score"] >= udata.get("maxscore", -1):
		udata["maxscore"] = prank["score"]
		udata["maxid"] = tdata["id"]
	if prank["rank"] <= udata.get("maxrank", 1000000):
		udata["maxrank"] = prank["rank"]
		udata["maxrankid"] = tdata["id"]
	udata["username"] = prank["username"]
	if "title" in prank:
		udata["title"] = prank["title"]
	if prank["rank"] == 1:
		udata["#1"] = udata.get("#1", 0) + 1
	if prank["rank"] == 2:
		udata["#2"] = udata.get("#2", 0) + 1
	if prank["rank"] == 3:
		udata["#3"] = udata.get("#3", 0) + 1
	if prank["score"] == 0:
		udata["0s"] = udata.get("0s", 0) + 1

# Merge ranking information for a player based on two rankings (update to first)
# ASSUMPTION: BOTH EXIST
def mergeplayer(udata, udata2):
	udata["ranking"] = 0
	udata["score"] = udata.get("score", 0) + udata2.get("score", 0)
	udata["events"] = udata.get("events", 0) + udata2.get("events", 0)
	if udata.get("first", "2100-01-01") >= udata2.get("first", "2100-01-01"):
		udata["first"] = udata2["first"]
		udata["firstid"] = udata2["firstid"]
	if udata.get("last", "1900-01-01") <= udata2.get("last", "1900-01-01"):
		udata["last"] = udata2["last"]
		udata["lastid"] = udata2["lastid"]
	if udata.get("maxscore", -1) <= udata2.get("maxscore", -1):
		udata["maxscore"] = udata2["maxscore"]
		udata["maxid"] = udata2["maxid"]
	udata["maxrank"] = min(udata.get("maxrank", 1000000), udata2.get("maxrank", 1000000))
	if "title" in udata2:
		udata["title"] = udata2["title"]
	if ("#1" in udata) or ("#1" in udata2):
		udata["#1"] = udata.get("#1", 0) + udata2.get("#1", 0)
	if ("#2" in udata) or ("#2" in udata2):
		udata["#2"] = udata.get("#2", 0) + udata2.get("#2", 0)
	if ("#3" in udata) or ("#3" in udata2):
		udata["#3"] = udata.get("#3", 0) + udata2.get("#3", 0)
	if ("0s" in udata) or ("0s" in udata2):
		udata["0s"] = udata.get("0s", 0) + udata2.get("0s", 0)

# Update global ranking information based on new tournament ranking
def updatestats(rdata, tdata):
	rdata["events"] = rdata.get("events", 0) + 1
	rdata["participants"] = rdata.get("participants", 0) + tdata["players"]
	rdata["games"] = rdata.get("games", 0) + tdata["games"]
	rdata["moves"] = rdata.get("moves", 0) + tdata["moves"]
	rdata["wwins"] = rdata.get("wwins", 0) + tdata["wwins"]
	rdata["bwins"] = rdata.get("bwins", 0) + tdata["bwins"]
	rdata["berserks"] = rdata.get("berserks", 0) + tdata["berserks"]
	rdata["totrating"] = rdata.get("totrating", 0) + tdata["totrating"]
	if not "firstid" in rdata:
		rdata["firststart"] = tdata["start"]
		rdata["firstid"] = tdata["id"]
	rdata["laststart"] = tdata["start"]
	rdata["lastid"] = tdata["id"]
	if tdata["players"] > rdata.get("maxusers", 0):
		rdata["maxusers"] = tdata["players"]
		rdata["maxusersid"] = tdata["id"]
	if tdata["topscore"] > rdata.get("topscore", 0):
		rdata["topscore"] = tdata["topscore"]
		rdata["topid"] = tdata["id"]
		rdata["topuser"] = tdata["#1"]
		
# Merge global ranking information based on two rankings
def mergestats(rdata, rdata2):
	rdata["events"] = rdata.get("events", 0) + rdata2["events"]
	rdata["participants"] = rdata.get("participants", 0) + rdata2["participants"]
	rdata["points"] = rdata.get("points", 0) + rdata2["points"]
	rdata["games"] = rdata.get("games", 0) + rdata2["games"]
	rdata["moves"] = rdata.get("moves", 0) + rdata2["moves"]
	rdata["wwins"] = rdata.get("wwins", 0) + rdata2["wwins"]
	rdata["bwins"] = rdata.get("bwins", 0) + rdata2["bwins"]
	rdata["berserks"] = rdata.get("berserks", 0) + rdata2["berserks"]
	rdata["totrating"] = rdata.get("totrating", 0) + rdata2["totrating"]
	if rdata.get("firststart", "2100-01-01") > rdata2["firststart"]:
		rdata["firststart"] = rdata2["firststart"]
		rdata["firstid"] = rdata2["firstid"]
	if rdata.get("laststart", "1900-01-01") < rdata2["laststart"]:
		rdata["laststart"] = rdata2["laststart"]
		rdata["lastid"] = rdata2["lastid"]
	if rdata.get("maxusers", -1) < rdata2["maxusers"]:
		rdata["maxusers"] = rdata2["maxusers"]
		rdata["maxusersid"] = rdata2["maxusersid"]
	if rdata.get("topscore", -1) < rdata2["topscore"]:
		rdata["topscore"] = rdata2["topscore"]
		rdata["topid"] = rdata2["topid"]
		rdata["topuser"] = rdata2["topuser"]

# Store rankings in files in different orders, and only partial lists for some...
def storerankings(rdata, ndata, mo, ev):

	# 4: Print results back to json
	with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "w") as jf:
		jf.write(json.dumps(rdata))
		
	# 4: Re-sort rankings for proper ordering -- ONLY FULL RANKING, REST IS PARTIAL
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["score"], reverse = True)}
	with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson", "w") as nf:
		for index, userkey in enumerate(ndata):
			ndata[userkey]["ranking"] = index + 1
			nf.write(json.dumps(ndata[userkey]) + "\n")

	# 4: Re-sort rankings for medal-based ordering
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["score"], reverse = True)}
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: 100000000*item[1].get("#1", 0) + 10000*item[1].get("#2", 0) + item[1].get("#3", 0), reverse = True)}
	with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_trophies.ndjson", "w") as nf:
		for index, userkey in enumerate(ndata):
			ndata[userkey]["ranking"] = index + 1
			nf.write(json.dumps(ndata[userkey]) + "\n")
			if ndata[userkey]["ranking"] == 1000:
				break

	# 4: Re-sort rankings for activeness ordering
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["score"], reverse = True)}
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["events"] - item[1].get("0s", 0), reverse = True)}
	with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_events.ndjson", "w") as nf:
		for index, userkey in enumerate(ndata):
			ndata[userkey]["ranking"] = index + 1
			nf.write(json.dumps(ndata[userkey]) + "\n")
			if ndata[userkey]["ranking"] == 1000:
				break
			
	# 4: Re-sort rankings for aaverages
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["score"], reverse = True)}
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["score"] / max(1, item[1]["events"] - item[1].get("0s", 0)), reverse = True)}
	with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_average.ndjson", "w") as nf:
		for index, userkey in enumerate(ndata):
			ndata[userkey]["ranking"] = index + 1
			nf.write(json.dumps(ndata[userkey]) + "\n")
			if ndata[userkey]["ranking"] == 1000:
				break
			
	# 4: Re-sort rankings for maximum-based ordering
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["score"], reverse = True)}
	ndata = {k: v for k, v in sorted(ndata.items(), key = lambda item: item[1]["maxscore"], reverse = True)}
	with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_maximum.ndjson", "w") as nf:
		for index, userkey in enumerate(ndata):
			ndata[userkey]["ranking"] = index + 1
			nf.write(json.dumps(ndata[userkey]) + "\n")
			if ndata[userkey]["ranking"] == 1000:
				break

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

fpath = "E:\\lichess\\tournaments\\"
frpath = "E:\\lichess\\tournaments\\rankings\\"

curyear = datetime.datetime.now().year

# Standard rankings: event/mode totals
for mo in mode:
	for ev in event:
	
		print(mo + " - " + ev + " - Running...")

		pref = ev + "_" + mo + "_"
		folder = ev + "\\" + mo + "\\"
		
		# 1: Skip if no detailed tournament info file found (some might not yet be downloaded)
		if not os.path.exists(fpath + folder + ev + "_" + mo + ".ndjson"):
			print(mo + " - " + ev + " - No rankings.")
			continue

		# Create directory if it does not exist
		if not os.path.exists(frpath + mo + "\\" + ev):
			print(mo + " - " + ev + " - Creating directory " + frpath + mo + "\\" + ev)
			os.makedirs(frpath + mo + "\\" + ev)
		
		# 2: Load previous ranking, info json and ranking ndjson
		if os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json") and os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson"):
			with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as jf:
				rdata = json.load(jf)
			#ndata = []
			ndatap = dict()
			with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson", "r") as nf:
				dictio = dict()
				for line in nf:
					dictio = json.loads(line)
					ndatap[dictio["username"].lower()] = dictio
		else:
			rdata = dict()
			#ndata = []
			ndatap = dict()
		
		# rdata = {"events": 200, "participants": 50240, "players": 12104, "games": 1239052, "moves": 2130935, "firststart": "2014-...", "laststart": "2020-...", "lastid": "s923RMW4", "wwins": 11, "bwins": 12, "maxusers": 12340, "topscore": 123}
		# ndata = [{}, ..., {"ranking": 7, "score": 4102, "username": "thijscom", "title": "FM", "events": 23, "firstevent": 4, "lastevent": 123, "#1": 0, "#2": 1, "#3": 0, "maxscore": 12, "0s": 3, "maxrank": 5}, ...]
		# ndatap = {{}, ..., "thijscom": {}, ...}
		
		# 3: Scroll through tournament info file until new tournaments are found, then update from each file
		with open(fpath + folder + ev + "_" + mo + ".ndjson", "r") as tf:
			
			# Do sanity check that last tournament in previous ranking is indeed the Nth in the tournament file
			if ("events" in rdata) and ("lastid" in rdata):
				for i in range(rdata["events"] - 1):
					next(tf)
				print(mo + " - " + ev + " - Skipping " + str(rdata["events"]) + " events...")
				ptour = json.loads(tf.readline())
				# check if tournament is consistent
				if not (ptour["id"] == rdata["lastid"]):
					print("Error: last id wrong")
					time.sleep(1000000)
				
			# Process remaining lines by updating rankings
			newprocessed = 0
			for line in tf:
				
				# Load tournament info
				tdata = json.loads(line)
				print(mo + " - " + ev + " - New event: " + tdata["id"])
				
				# Update global statistics
				updatestats(rdata, tdata)
				
				# Load tournament rankings
				with open(fpath + folder + pref + tdata["id"] + ".ndjson", "r") as tfile:
					for line in tfile:
						prank = json.loads(line)
						# prank: {"rank": 1, "score": 36, "rating": 2267, "username": "kasparovsabe", "title": "FM", "performance": 2454}
						userkey = prank["username"].lower()
						if not userkey in ndatap:
							# New player
							ndatap[userkey] = dict()
							rdata["players"] = rdata.get("players", 0) + 1
						
						# Update player information
						updateplayer(ndatap[userkey], prank, tdata)
						ndatap[userkey]["username"] = prank["username"]
						rdata["points"] = rdata.get("points", 0) + prank["score"]
				
				newprocessed += 1
				if newprocessed % 1000 == 0:
					print(mo + " - " + ev + " - Intermediate dump after " + str(rdata["events"]) + " events.")
					storerankings(rdata, ndatap, mo, ev)
		
		if newprocessed >= 1:
			print(mo + " - " + ev + " - Final dump after " + str(rdata["events"]) + " events.")		
			storerankings(rdata, ndatap, mo, ev)
		else:
			print(mo + " - " + ev + " - No new events found, so nothing to do.")		
		
	#######################################################################################
	# Special rankings: (Yearly) overall rankings
	#######################################################################################
	for year in range(2014, curyear + 1):
		
		print(mo + " - " + str(year) + " - Running...")
		
		# 0: See if detailed list of tournaments or rankings already exists, then skip
		if os.path.exists(frpath + mo + "\\" + str(year) + "\\" + mo + "_" + str(year) + "_events.ndjson") and os.path.exists(frpath + mo + "\\" + str(year) + "\\" + mo + "_" + str(year) + "_ranking.json") and os.path.exists(frpath + mo + "\\" + str(year) + "\\" + mo + "_" + str(year) + "_ranking_points.ndjson") and (not year == curyear):
			print(mo + " - " + str(year) + " - Ranking exists, skipping.")
			continue
		
		# 1: Make detailed list of tournaments for this year, sorted by date
		tlist = []
		for ev in event:
		
			pref = ev + "_" + mo + "_"
			folder = ev + "\\" + mo + "\\"
			
			# See if any tournaments for this event category must be considered
			if not os.path.exists(fpath + folder + ev + "_" + mo + ".ndjson"):
				continue
				
			# Open detailed tournament list file, if it exists, and copy all entries for this year
			with open(fpath + folder + ev + "_" + mo + ".ndjson", "r") as tf:
			
				# Process lines to see which were played this year
				for line in tf:
					tdata = json.loads(line)			
					if tdata["start"][:4] == str(year):
						tdata["type"] = ev
						tlist.append(tdata)
					if int(tdata["start"][:4]) > year:
						break
			
		# Continue if nothing is to be done anyway
		if len(tlist) == 0:
			print(mo + " - " + str(year) + " - No events.")
			continue
			
		# Create directory if it does not exist
		if not os.path.exists(frpath + mo + "\\" + str(year) + "\\"):
			print(mo + " - " + str(year) + " - Creating directory " + frpath + mo + "\\" + str(year) + ".")
			os.makedirs(frpath + mo + "\\" + str(year) + "\\")	
		
		# Sort all events by date and store them in a file
		tlist.sort(key = lambda v: v["start"])
		with open(frpath + mo + "\\" + str(year) + "\\" + mo + "_" + str(year) + "_events.ndjson", "w") as outfile:
			tnum = 0
			for i in range(len(tlist)):
				tnum += 1
				tlist[i]["number"] = tnum
				outfile.write(json.dumps(tlist[i]) + "\n")
		
		# 2: Make ranking based on all these tournaments
		rdata = dict()
		ndatap = dict()
		for i in range(len(tlist)):
			
			# Load tournament info
			tdata = tlist[i]
			ev = tdata["type"]
			pref = ev + "_" + mo + "_"
			folder = ev + "\\" + mo + "\\"
			
			# Update global statistics
			updatestats(rdata, tdata)
				
			# Load tournament rankings
			with open(fpath + folder + pref + tdata["id"] + ".ndjson", "r") as tfile:
				for line in tfile:
					prank = json.loads(line)
					# prank: {"rank": 1, "score": 36, "rating": 2267, "username": "kasparovsabe", "title": "FM", "performance": 2454}
					userkey = prank["username"].lower()
					if not userkey in ndatap:
						# New player
						ndatap[userkey] = dict()
						rdata["players"] = rdata.get("players", 0) + 1
				
					# Update player information
					updateplayer(ndatap[userkey], prank, tdata)
					rdata["points"] = rdata.get("points", 0) + prank["score"]
		
		print(mo + " - " + str(year) + " - Final dump after " + str(rdata["events"]) + " events.")
		storerankings(rdata, ndatap, mo, str(year))
		
	#######################################################################################
	# GLOBAL rankings: Add up all tournaments per mode (blitz, bullet, ...)
	#######################################################################################
	
	print(mo + " - all - Running...")
				
	# Create directory if it does not exist
	if not os.path.exists(frpath + mo + "\\all\\"):
		print(mo + " - all - Creating directory " + frpath + mo + "\\all.")
		os.makedirs(frpath + mo + "\\all\\")	
	
	# Make detailed list of tournaments, sorted by date
	tlist = []
	for ev in event:
		
		# See if any tournaments for this event category must be considered
		if not os.path.exists(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson"):
			continue
			
		# Open detailed tournament list file, if it exists, and copy all entries
		with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson", "r") as tf:
		
			# Process lines
			for line in tf:
				tdata = json.loads(line)			
				tdata["type"] = ev
				tlist.append(tdata)
	
	# Sort all events by date and store them in a file
	tlist.sort(key = lambda v: v["start"])
	with open(frpath + mo + "\\all\\" + mo + "_all_events.ndjson", "w") as outfile:
		tnum = 0
		for i in range(len(tlist)):
			tnum += 1
			tlist[i]["number"] = tnum
			outfile.write(json.dumps(tlist[i]) + "\n")
	
	# Add up rankings for different events
	rdata = dict()
	ndatap = dict()
	for ev in event:
	
		# See if any tournaments for this event category must be considered
		if not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json") or not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson"):
			continue
					
		# Merge ranking info from both rankings
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as jf:
			rdata2 = json.load(jf)
		mergestats(rdata, rdata2)

		# Load new ranking
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson", "r") as nf:
			ndatap2 = dict()
			for line in nf:
				dictio = json.loads(line)
				userkey = dictio["username"].lower()
				if not userkey in ndatap:
					ndatap[userkey] = dictio
					rdata["players"] = rdata.get("players", 0) + 1
				else:
					mergeplayer(ndatap[userkey], dictio)
		
	print(mo + " - all - Final dump after " + str(rdata["events"]) + " events.")
	storerankings(rdata, ndatap, mo, "all")
	

#######################################################################################
# GLOBAL rankings: Add up all tournaments per type (hourly, daily, elite, ...)
#######################################################################################

eventp = event.copy()
for year in range(2014, curyear + 1):
	eventp[str(year)] = str(year)

for ev in eventp:

	print("all - " + ev + " - Running...")
				
	# Create directory if it does not exist
	if not os.path.exists(frpath + "all\\" + ev + "\\"):
		print("all - " + ev + " - Creating directory " + frpath + "all\\" + ev + "\\.")
		os.makedirs(frpath + "all\\" + ev + "\\")	
	
	# Make detailed list of tournaments, sorted by date
	tlist = []
	for mo in mode:
		
		# See if any tournaments for this event category must be considered
		if not os.path.exists(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson"):
			continue
			
		# Open detailed tournament list file, if it exists, and copy all entries
		with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson", "r") as tf:
		
			# Process lines
			for line in tf:
				tdata = json.loads(line)			
				tdata["type"] = ev
				tlist.append(tdata)
	
	# Sort all events by date and store them in a file
	tlist.sort(key = lambda v: v["start"])
	with open(frpath + "all\\" + ev + "\\all_" + ev + "_events.ndjson", "w") as outfile:
		tnum = 0
		for i in range(len(tlist)):
			tnum += 1
			tlist[i]["number"] = tnum
			outfile.write(json.dumps(tlist[i]) + "\n")
	
	# Add up rankings for different events
	rdata = dict()
	ndatap = dict()
	for mo in mode:
	
		# See if any tournaments for this event category must be considered
		if not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json") or not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson"):
			continue
					
		# Merge ranking info from both rankings
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as jf:
			rdata2 = json.load(jf)
		mergestats(rdata, rdata2)

		# Load new ranking
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson", "r") as nf:
			ndatap2 = dict()
			for line in nf:
				dictio = json.loads(line)
				userkey = dictio["username"].lower()
				if not userkey in ndatap:
					ndatap[userkey] = dictio
					rdata["players"] = rdata.get("players", 0) + 1
				else:
					mergeplayer(ndatap[userkey], dictio)
		
	print("all - " + ev + " - Final dump after " + str(rdata["events"]) + " events.")
	storerankings(rdata, ndatap, "all", ev)
	



#######################################################################################
# GLOBAL GLOBAL rankings: Everything
#######################################################################################

print("all - all - Running...")
				
# Create directory if it does not exist
if not os.path.exists(frpath + "all\\all\\"):
	print("all - all - Creating directory " + frpath + "all\\all\\.")
	os.makedirs(frpath + "all\\all\\")	

# Make detailed list of tournaments, sorted by date
tlist = []
for mo in mode:
	for ev in event:

		# See if any tournaments for this event category must be considered
		if not os.path.exists(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson"):
			continue
			
		# Open detailed tournament list file, if it exists, and copy all entries
		with open(fpath + ev + "\\" + mo + "\\" + ev + "_" + mo + ".ndjson", "r") as tf:
		
			# Process lines
			for line in tf:
				tdata = json.loads(line)			
				tdata["type"] = ev
				tlist.append(tdata)

# Sort all events by date and store them in a file
tlist.sort(key = lambda v: v["start"])
with open(frpath + "all\\all\\all_all_events.ndjson", "w") as outfile:
	tnum = 0
	for i in range(len(tlist)):
		tnum += 1
		tlist[i]["number"] = tnum
		outfile.write(json.dumps(tlist[i]) + "\n")

# Add up rankings for different events
rdata = dict()
ndatap = dict()
for mo in mode:
	for ev in event:
		# See if any tournaments for this event category must be considered
		if not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json") or not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson"):
			continue
					
		# Merge ranking info from both rankings
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as jf:
			rdata2 = json.load(jf)
		mergestats(rdata, rdata2)

		# Load new ranking
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson", "r") as nf:
			ndatap2 = dict()
			for line in nf:
				dictio = json.loads(line)
				userkey = dictio["username"].lower()
				if not userkey in ndatap:
					ndatap[userkey] = dictio
					rdata["players"] = rdata.get("players", 0) + 1
				else:
					mergeplayer(ndatap[userkey], dictio)
	
print("all - all - Final dump after " + str(rdata["events"]) + " events.")
storerankings(rdata, ndatap, "all", "all")

print("ALL DONE!")