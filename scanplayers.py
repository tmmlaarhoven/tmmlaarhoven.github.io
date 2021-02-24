import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json
import math

APItoken = ""
with open("E:\\lichess\\APItoken.txt", "r") as tokenfile:
	for line in tokenfile:
		APItoken = line.strip()

fpath = "E:\\lichess\\tournaments\\"
frpath = "E:\\lichess\\tournaments\\rankings\\"
fpathweb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

event = {
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
	"ultrabullet": "UltraBullet",
	"all": "All"
	}
	
order = {"_points": "index.html", "_trophies": "trophies.html", "_events": "events.html", "_average": "average.html", "_maximum": "maximum.html"}


# Generate big list of players to scan
playerstoscan = dict()
for ev in event:
	for mo in mode:
		for ord in order:
			if os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking" + ord + ".ndjson"):
				print(mo + " -- " + ev + " -- " + ord)
				with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking" + ord + ".ndjson", "r") as rf:
					for count, line in enumerate(rf):
						dictio = json.loads(line.strip())
						playerstoscan[dictio["username"].lower()] = 1
						if count > 150:
							break	
playerstoscan = {k: v for k, v in sorted(playerstoscan.items(), key = lambda item: item[1], reverse = False)}
print("Total players: " + str(len(playerstoscan)))


# Load those users which have been checked before
playerschecked = dict()
if os.path.exists("E:\\lichess\\playerschecked.txt"):
	with open("E:\\lichess\\playerschecked.txt", "r") as filechecked:
		for line in filechecked:
			playerschecked[line.strip().lower()] = 1
playerschecked = {k: v for k, v in sorted(playerschecked.items(), key = lambda item: item[1], reverse = False)}	
print("Previously checked players: " + str(len(playerschecked)))


# Make list of new users to check
playersnew = []
for player in playerstoscan:
	if not player in playerschecked:
		playersnew.append(player)
print("New players to check: " + str(len(playersnew)))


# Obtain user data via API
playersclosed = dict()
playersTOS = dict()
playersboost = dict()
for i in range(math.ceil(len(playersnew) / 50)):
	
	time.sleep(3)
	if i % 60 == 59:
		time.sleep(60)
	
	print("Group: " + str(i))
		
	begin = i * 50
	end = min(i * 50 + 50, len(playersnew))
	r = requests.post("https://lichess.org/api/users", headers = {'Authorization': 'Bearer ' + APItoken}, data = ",".join(playersnew[begin:end]))
	if r.status_code == 429:
		print("RATE LIMIT!")
		time.sleep(100000)

	dictio = ndjson.loads(r.content)[0]

	for i in range(len(dictio)):
		if ("disabled" in dictio[i]):
			playersclosed[dictio[i]["id"].lower()] = 1
		if ("tosViolation" in dictio[i]):
			playersTOS[dictio[i]["id"].lower()] = 1
		if ("booster" in dictio[i]):
			playersboost[dictio[i]["id"].lower()] = 1


# Store new problematic accounts in files
with open("E:\\lichess\\playersclosed.txt", "r") as fileclosed:
	for line in fileclosed:
		playersclosed[line.strip().lower()] = 1
playersclosed = {k: v for k, v in sorted(playersclosed.items(), key = lambda item: item[0], reverse = False)}	
print("Exporting " + str(len(playersclosed)) + " closed accounts...")
with open("E:\\lichess\\playersclosed.txt", "w") as fileclosed:
	for val in playersclosed:
		fileclosed.write(val + "\n")


with open("E:\\lichess\\playersTOS.txt", "r") as fileTOS:
	for line in fileTOS:
		playersTOS[line.strip().lower()] = 1
playersTOS = {k: v for k, v in sorted(playersTOS.items(), key = lambda item: item[0], reverse = False)}	
print("Exporting " + str(len(playersTOS)) + " TOS accounts...")		
with open("E:\\lichess\\playersTOS.txt", "w") as fileTOS:
	for val in playersTOS:
		fileTOS.write(val + "\n")
		

with open("E:\\lichess\\playersboost.txt", "r") as fileboost:
	for line in fileboost:
		playersboost[line.strip().lower()] = 1
playersboost = {k: v for k, v in sorted(playersboost.items(), key = lambda item: item[0], reverse = False)}	
print("Exporting " + str(len(playersboost)) + " boost accounts...")
with open("E:\\lichess\\playersboost.txt", "w") as fileboost:
	for val in playersboost:
		fileboost.write(val + "\n")
		

# Store new checked users in files
# Make list of new users to check
playersall = dict()
for player in playerschecked:
	playersall[player.lower()] = 1
for player in playerstoscan:
	playersall[player.lower()] = 1
playersall = {k: v for k, v in sorted(playersall.items(), key = lambda item: item[0], reverse = False)}	
print("Exporting " + str(len(playersall)) + " total checked accounts...")
with open("E:\\lichess\\playerschecked.txt", "w") as filechecked:
	for player in playersall:
		filechecked.write(player + "\n")
