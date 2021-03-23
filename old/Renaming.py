import os
import time

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

if not os.path.exists("E:\\lichess\\tournaments\\data\\"):
	os.makedirs("E:\\lichess\\tournaments\\data\\")	
		
for V in Variants:
	if not os.path.exists("E:\\lichess\\tournaments\\data\\" + V):
		os.makedirs("E:\\lichess\\tournaments\\data\\" + V)	
	for E in Events:
		if not os.path.exists("E:\\lichess\\tournaments\\data\\" + V + "\\" + E):
			os.makedirs("E:\\lichess\\tournaments\\data\\" + V + "\\" + E)
		lengthprefix = len(E) + len(V) + 1
		newprefix = V + "_" + E
		for root, dirs, files in os.walk("E:\\lichess\\tournaments\\" + E + "\\" + V + "\\", topdown = False):
			for file in files:
				orfile = "E:\\lichess\\tournaments\\" + E + "\\" + V + "\\" + file
				tarfile = "E:\\lichess\\tournaments\\data\\" + V + "\\" + E + "\\" + V + "_" + E + file[lengthprefix:]
				print(orfile + " to " + tarfile)
				#time.sleep(2)
				os.rename(orfile, tarfile)