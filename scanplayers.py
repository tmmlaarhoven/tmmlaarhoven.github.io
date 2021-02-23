import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json

APItoken = ""
with open("E:\\lichess\\APItoken.txt", "r") as tokenfile:
	for line in tokenfile:
		APItoken = line

fpath = "E:\\lichess\\tournaments\\"
frpath = "E:\\lichess\\tournaments\\rankings\\"
fpathweb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

event = {
	"2000": "&lt;2000",
	"1700": "&lt;1700",
	"1600": "&lt;1600",
	"1500": "&lt;1500",
	"1300": "&lt;1300",
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

playerstoscan = []

for ev in event:
	for mo in mode:
		for ord in order:
			if os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking" + ord + ".ndjson"):
				print(mo + " -- " + ev + " -- " + ord)
				with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking" + ord + ".ndjson", "r") as rf:
					for count, line in enumerate(rf):
						dictio = json.loads(line.strip())
						playerstoscan.append(dictio["username"])
						if count > 100:
							break
			
playerstoscan = list(dict.fromkeys(playerstoscan))
#print(playerstoscan)

playersclosed = []
playersTOS = []
playersboost = []

print("Players: " + str(len(playerstoscan)))

for i in range(round(len(playerstoscan) / 100)):
	
	time.sleep(2)
	print("Group: " + str(i))
		
	begin = i * 100
	r = requests.post("https://lichess.org/api/users", headers = {'Authorization': 'Bearer ' + APItoken}, data = ",".join(playerstoscan[begin:begin+100]))
	if r.status_code == 429:
		print("RATE LIMIT!")
		time.sleep(100000)

	dict = ndjson.loads(r.content)[0]

	for i in range(len(dict)):
		if ("disabled" in dict[i]):
			playersclosed.append(dict[i]["id"])
		if ("tosViolation" in dict[i]):
			playersTOS.append(dict[i]["id"])
		if ("booster" in dict[i]):
			playersboost.append(dict[i]["id"])

with open("E:\\lichess\\playerclosed.txt", "w") as fileclosed:
	for val in playersclosed:
		fileclosed.write(val + "\n")

with open("E:\\lichess\\playerTOS.txt", "w") as fileTOS:
	for val in playersTOS:
		fileTOS.write(val + "\n")
		
with open("E:\\lichess\\playerboost.txt", "w") as fileboost:
	for val in playersboost:
		fileboost.write(val + "\n")