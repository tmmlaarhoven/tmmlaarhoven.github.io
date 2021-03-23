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
	"2021": "2021",
	"2020": "2020",
	"2019": "2019",
	"2018": "2018",
	"2017": "2017",
	"2016": "2016",
	"2015": "2015",
	"2014": "2014"
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
	"ultrabullet": "UltraBullet",
	"all": "All"
	}
	
Order = {
	"_points": "index.html", 
	"_trophies": "trophies.html", 
	"_events": "events.html", 
	#"_average": "average.html", 
	"_maximum": "maximum.html"
	}
	
TopToCheck = 200		# Check the top TopToCheck from each ranking
GroupSize = 50			# API requests in batches of size GroupSize
	
def Prefix(V, E):
	return V + "_" + E + "_"

def Folder(V, E):
	return V + "\\" + E + "\\"
	
def PrintMessage(V, E, Message):
	print("{:<11}".format(V) + " - {:<8}".format(E) + " - " + Message)

# Generate big list of players to scan
PlayersToScan = dict()
for E in Events:
	for V in Variants:
		for O in Order:
			if os.path.exists(PathRank + Folder(V, E) + V + "_" + E + "_ranking" + O + ".ndjson"):
				PrintMessage(V, E, "Processing " + Order[O] + ".")
				with open(PathRank + Folder(V, E) + V + "_" + E + "_ranking" + O + ".ndjson", "r") as RankFile:
					for Index, Line in enumerate(RankFile):
						UserRank = json.loads(Line.strip())
						PlayersToScan[UserRank["Username"].lower()] = 1
						if Index > TopToCheck:
							break	

# Sort alphabetically
PlayersToScan = {k: v for k, v in sorted(PlayersToScan.items(), key = lambda item: item[1], reverse = False)}
PrintMessage("all", "all", "Total players found: " + str(len(PlayersToScan)) + ".")

# Load those users which have been checked before
PlayersChecked = dict()
if os.path.exists(PathWeb + "PlayersChecked.txt"):
	with open(PathWeb + "PlayersChecked.txt", "r") as FileChecked:
		for Line in FileChecked:
			PlayersChecked[Line.strip().lower()] = 1
PlayersChecked = {k: v for k, v in sorted(PlayersChecked.items(), key = lambda item: item[1], reverse = False)}	
PrintMessage("all", "all", "Previously checked players: " + str(len(PlayersChecked)) + ".")

# Make list of new users to check
PlayersNew = []
for Player in PlayersToScan:
	if not Player in PlayersChecked:
		PlayersNew.append(Player)
PlayersNew.sort()
PrintMessage("all", "all", "New players to check: " + str(len(PlayersNew)) + ".")

# Obtain user data via API
PlayersClosed = dict()
PlayersTOS = dict()
PlayersBoost = dict()
PrintMessage("all", "all", "Groups to query via the API: " + str(math.ceil(len(PlayersNew) / GroupSize)) + " of " + str(GroupSize) + " users.")
for i in range(math.ceil(len(PlayersNew) / GroupSize)):
	
	time.sleep(3)
	if i % 60 == 59:
		time.sleep(60)
		
	begin = i * GroupSize
	end = min(i * GroupSize + GroupSize, len(PlayersNew))
	PrintMessage("all", "all", "Group " + str(i+1) + ": Users " + PlayersNew[begin] + " to " + PlayersNew[end-1] + ".")
	r = requests.post("https://lichess.org/api/users", headers = {"Authorization": "Bearer " + APIToken}, data = ",".join(PlayersNew[begin:end]))
	if r.status_code == 429:
		print("RATE LIMIT!")
		time.sleep(100000)

	APIResponse = ndjson.loads(r.content)[0]	# List of dictionaries
	for PlayerInfo in APIResponse:
		if ("disabled" in PlayerInfo):
			PlayersClosed[PlayerInfo["id"].lower()] = 1
		if ("tosViolation" in PlayerInfo):
			PlayersTOS[PlayerInfo["id"].lower()] = 1
		if ("booster" in PlayerInfo):
			PlayersBoost[PlayerInfo["id"].lower()] = 1

# Store closed accounts in file
if os.path.exists(PathWeb + "PlayersClosed.txt"):
	with open(PathWeb + "PlayersClosed.txt", "r") as FileClosed:
		for Line in FileClosed:
			PlayersClosed[Line.strip().lower()] = 1
PlayersClosed = {k: v for k, v in sorted(PlayersClosed.items(), key = lambda item: item[0], reverse = False)}	
PrintMessage("all", "all", "Exporting " + str(len(PlayersClosed)) + " closed accounts...")
with open(PathWeb + "PlayersClosed.txt", "w") as FileClosed:
	for Username in PlayersClosed:
		FileClosed.write(Username + "\n")

# Store TOS accounts in file
if os.path.exists(PathWeb + "PlayersTOS.txt"):
	with open(PathWeb + "PlayersTOS.txt", "r") as FileTOS:
		for Line in FileTOS:
			PlayersTOS[Line.strip().lower()] = 1
PlayersTOS = {k: v for k, v in sorted(PlayersTOS.items(), key = lambda item: item[0], reverse = False)}	
PrintMessage("all", "all", "Exporting " + str(len(PlayersTOS)) + " TOS accounts...")		
with open(PathWeb + "PlayersTOS.txt", "w") as FileTOS:
	for Username in PlayersTOS:
		FileTOS.write(Username + "\n")

# Store boostmarked accounts in file		
if os.path.exists(PathWeb + "PlayersBoost.txt"):
	with open(PathWeb + "PlayersBoost.txt", "r") as FileBoost:
		for Line in FileBoost:
			PlayersBoost[Line.strip().lower()] = 1
PlayersBoost = {k: v for k, v in sorted(PlayersBoost.items(), key = lambda item: item[0], reverse = False)}	
PrintMessage("all", "all", "Exporting " + str(len(PlayersBoost)) + " boost accounts...")
with open(PathWeb + "PlayersBoost.txt", "w") as FileBoost:
	for Username in PlayersBoost:
		FileBoost.write(Username + "\n")

# Store new checked users in files
# Make list of new users to check
PlayersAll = dict()
for Player in PlayersChecked:
	PlayersAll[Player.lower()] = 1
for Player in PlayersToScan:
	PlayersAll[Player.lower()] = 1
PlayersAll = {k: v for k, v in sorted(PlayersAll.items(), key = lambda item: item[0], reverse = False)}	
PrintMessage("all", "all", "Exporting " + str(len(PlayersAll)) + " total checked accounts...")
with open(PathWeb + "PlayersChecked.txt", "w") as FileChecked:
	for Player in PlayersAll:
		FileChecked.write(Player + "\n")

print("ALL DONE!")

