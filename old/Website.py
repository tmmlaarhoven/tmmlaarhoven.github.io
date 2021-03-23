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

def strf(num, type):
	if num > 10000000000:
		return f"<span class='info' title='{str(num)[:-9]},{str(num)[-9:-6]},{str(num)[-6:-3]},{str(num)[-3:]} {type}'>{round(num / 1000000000)}B</span>"
	elif num > 1000000000: 
		return f"<span class='info' title='{str(num)[:-9]},{str(num)[-9:-6]},{str(num)[-6:-3]},{str(num)[-3:]} {type}'>{round(num / 100000000) / 10}B</span>"
	elif num > 10000000:
		return f"<span class='info' title='{str(num)[-9:-6]},{str(num)[-6:-3]},{str(num)[-3:]} {type}'>{round(num / 1000000)}M</span>"
	elif num > 1000000:
		return f"<span class='info' title='{str(num)[-9:-6]},{str(num)[-6:-3]},{str(num)[-3:]} {type}'>{round(num / 100000) / 10}M</span>"
	elif num > 10000:
		return f"<span class='info' title='{str(num)[-6:-3]},{str(num)[-3:]} {type}'>{round(num / 1000)}K</span>"
	elif num > 1000:
		return f"<span class='info' title='{str(num)[-6:-3]},{str(num)[-3:]} {type}'>{round(num / 100) / 10}K</span>"
	else:
		return str(num)

Months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
def DateString(dstr):
	# dstr: "2020-02-27"
	return f"{Months[dstr[5:7]]} {dstr[8:10]}, {dstr[0:4]}"
	
def StatisticsTable(of, ri, func):
	of.write("\t\t</th>\n")
	of.write("\t</tr>\n")
	of.write("\t<tr>\n")
	of.write("\t\t<th colspan='10' style='width: 100%; padding: 0px;'>\n")
	of.write("\t\t<table class='stats' width='100%'>\n")
	of.write("\t\t\t<thead>\n")
	of.write("\t\t\t<tr>\n")
	of.write("\t\t\t\t<th class='stats'></th>\n")
	for Index, V in enumerate(VariantsOrdered):
		of.write(f"\t\t\t\t<th class='stats{'last' if Index == 15 else ''}'><span title='{Variants[V]}'>{VariantsOrderedIcons[V]}</span></th>\n")
	of.write("\t\t\t</tr>\n")
	of.write("\t\t\t</thead>\n")
	of.write("\t\t\t<tbody>\n")
	for Index, E in enumerate(Events):
		of.write(f"\t\t\t<tr class='{'even' if (Index % 2 == 1) else 'odd'}'>\n")
		of.write(f"\t\t\t\t<td class='statshead' width='90'>{Events[E]}</td>\n")
		for IndexV, V in enumerate(VariantsOrdered):
			of.write(f"\t\t\t\t<td class='stats{'last' if IndexV == 15 else ''}' width='50' align='right'>{func(ri, V, E)}</td>\n")
		of.write("\t\t\t</tr>\n")
	of.write("\t\t\t</tbody>\n")
	of.write("\t\t</table>\n")
	of.write("\t\t</th>\n")
	of.write("\t</tr>\n")
	of.write("\t<tr>\n")
	of.write("\t\t<th colspan='10' class='about'>\n")

Events = {
	"all": "All",
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
#	"2021": "2021",
#	"2020": "2020",
#	"2019": "2019",
#	"2018": "2018",
#	"2017": "2017",
#	"2016": "2016",
#	"2015": "2015",
#	"2014": "2014",
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

# Ordered list of rankings 
EventsOrdered = {
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
#	"2021": "2021",
#	"2020": "2020",
#	"2019": "2019",
#	"2018": "2018",
#	"2017": "2017",
#	"2016": "2016",
#	"2015": "2015",
#	"2014": "2014"
}

# Ordered list of variants/variants
VariantsOrdered = {
	"all": "All",
	"ultrabullet": "UltraBullet",
	"hyperbullet": "HyperBullet",
	"bullet": "Bullet",
	"superblitz": "SuperBlitz",
	"blitz": "Blitz",
	"rapid": "Rapid",
	"classical": "Classical",
	"crazyhouse": "Crazyhouse",
	"chess960": "Chess960",
	"koth": "King of the Hill",
	"3check": "Three-check",
	"antichess": "Antichess",
	"atomic": "Atomic",
	"horde": "Horde",
	"racingkings": "Racing Kings"
}

VariantsOrderedIcons = {
	"all": "O", #"&#xe004;",
	"ultrabullet": "{",
	"hyperbullet": "T",
	"bullet": "T",
	"superblitz": ")",
	"blitz": ")",
	"rapid": "#",
	"classical": "+",
	"crazyhouse": "&#xe00b;",
	"chess960": "'",
	"koth": "(",
	"3check": ".",
	"antichess": "@",
	"atomic": ">",
	"horde": "_",
	"racingkings": "&#xe00a;"
}

PathData = "E:\\lichess\\tournaments\\data\\"
PathRank = "E:\\lichess\\tournaments\\rankings\\"
PathWeb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

if not os.path.exists(PathWeb):
	os.makedirs(PathWeb)

for V in Variants:
	if not os.path.exists(PathWeb + V + "\\"):
		print(f"{V} - Creating directory {PathWeb}{V}\\")
		os.makedirs(f"{PathWeb}{V}\\")

#=========================================================================
# 2: Top rankings per Variants and per event
#=========================================================================

PlayersClosed = dict()
with open(PathWeb + "PlayersClosed.txt", "r") as FileClosed:
	for Line in FileClosed:
		PlayersClosed[Line.strip()] = "1"

PlayersTOS = dict()
with open(PathWeb + "PlayersTOS.txt", "r") as FileTOS:
	for Line in FileTOS:
		PlayersTOS[Line.strip()] = "1"

PlayersBoost = dict()
with open(PathWeb + "PlayersBoost.txt", "r") as FileBoost:
	for Line in FileBoost:
		PlayersBoost[Line.strip()] = "1"


# Display top 1000 for each type
nplayers = 200
for V in Variants:
#for V in []:
	for E in Events:		
		Orders = {"_points": "index.html", "_trophies": "trophies.html", "_events": "events.html", "_average": "average.html", "_maximum": "maximum.html"}
		for O in Orders:
		
			if not os.path.exists(f"{PathRank}{V}\\{E}\\{V}_{E}_ranking.json") or not os.path.exists(f"{PathRank}{V}\\{E}\\{V}_{E}_players{O}.ndjson"):
				continue
			if O == "_average":
				if os.path.exists(f"{PathWeb}{V}\\{E}\\{Orders[O]}"):
					os.remove(f"{PathWeb}{V}\\{E}\\{Orders[O]}")
					print(f"{V} - {E} - Removing {Orders[O]}...")
				continue
			
			print(f"{V} - {E} - Building {Orders[O]}...")
			if not os.path.exists(f"{PathWeb}{V}\\{E}\\"):
				print(f"{V} - {E} - Creating directory {PathWeb}{V}\\{E}\\")
				os.makedirs(f"{PathWeb}{V}\\{E}\\")

			# Load ranking info
			with open(f"{PathRank}{V}\\{E}\\{V}_{E}_ranking.json", "r") as rf:
				jinfo = json.load(rf)
			
			with open(f"{PathWeb}{V}\\{E}\\{Orders[O]}", "w") as ofile:			
				ofile.write("<!DOCTYPE html>\n")
				ofile.write("<html lang='en-US'>\n")
				ofile.write("<!-- Rankings built using the Lichess API (https://lichess.org/api) and some manual (python-based) tournament scraping. -->\n")
				ofile.write("<!-- Source code available at https://github.com/tmmlaarhoven/tmmlaarhoven.github.io -->\n")
				ofile.write("<head>\n")
				if E == "marathon":
					ofile.write(f"<title>Lichess Rankings &middot; {Variants[V]} Marathons</title>\n")
				elif V == "all" or E == "titled" or E == "shield":
					if V == "all" and E == "all":
						ofile.write("<title>Lichess Rankings &middot; All Arenas</title>\n")
					else:
						ofile.write(f"<title>Lichess Rankings &middot; {Variants[V]} {Events[E]} Rankings</title>\n")
				else:
					ofile.write(f"<title>Lichess Rankings &middot; {Events[E]} {Variants[V]} Rankings</title>\n")
				ofile.write("<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>\n")
				ofile.write("<link rel='icon' type='image/png' href='../../../favicon.ico'>\n")
				ofile.write("<link rel='stylesheet' href='../../../style.css'>\n")
				ofile.write("</head>\n")
				ofile.write("<table class='content'>\n")
				ofile.write("\t<thead>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='variant'>\n")
				#ofile.write("\t\t\t<a class='" + ("active" if (E == "all") else "back") + "' href='../all/" + Orders[O] + "'>All</a>\n")
				ofile.write("\t\t\t<a class='variant' href='../../index.html'><span style='font-family: lichess' title='About'>&#xe005;</span></a>\n")
				for index, mod in enumerate(VariantsOrdered):
					if os.path.exists(PathRank + mod + "\\" + E + "\\" + mod + "_" + E + "_ranking.json") and os.path.exists(PathRank + mod + "\\" + E + "\\" + mod + "_" + E + "_ranking" + O + ".ndjson"):
						ofile.write(f"\t\t\t &middot; <a class='{'active' if (V == mod) else 'variant'}' href='../../{mod}/{E}/{Orders[O]}'><span style='font-family: lichess' title='{VariantsOrdered[mod]}'>{VariantsOrderedIcons[mod]}</span></a>\n")
					else:
						ofile.write(f"\t\t\t &middot; <a class='{'active' if (V == mod) else 'variant'}' href='../../{mod}/all/{Orders[O]}'><span style='font-family: lichess' title='{VariantsOrdered[mod]}'>{VariantsOrderedIcons[mod]}</span></a>\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='type'>\n")
				ofile.write(f"\t\t<a class='{'active' if (E == 'all') else 'type'}' href='../all/{Orders[O]}'>All</a>\n")
				for eve in EventsOrdered:
					ofile.write("\t\t &middot; ")
					if os.path.exists(f"{PathRank}{V}\\{eve}\\{V}_{eve}_ranking.json") and os.path.exists(f"{PathRank}{V}\\{eve}\\{V}_{eve}_ranking{O}.ndjson"):
						ofile.write(f"<a class='{'active' if (E == eve) else 'type'}' href='../{eve}/{Orders[O]}'>{EventsOrdered[eve]}</a>\n")
					else:
						ofile.write(f"{EventsOrdered[eve]}\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='title'>\n")
				#ofile.write("\t\t<div class='lefticon'>" + VariantsOrderedIcons[V] + "</div>\n")
				if E == "marathon":
					ofile.write(f"\t\t{Variants[V]} Marathons\n")
				elif V == "all" or E == "titled" or E == "shield":
					if V == "all" and E == "all":
						ofile.write("\t\tAll Arenas\n")
					else:
						ofile.write(f"\t\t{Variants[V]} {Events[E]} Arenas\n")
				else:
					ofile.write(f"\t\t{Events[E]} {Variants[V]} Arenas\n")
				#ofile.write("\t\t<div class='righticon'>" + VariantsOrderedIcons[V] + "</div>\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='sort'><a class='sort' href='stats.html'>Show arena Stats</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Show rankings sorted by: &nbsp;\n")
				ofile.write(f"\t\t<a class='{'active' if (O == '_trophies') else 'sort'}' href='trophies.html'>Trophies</a>\n")
				ofile.write(f"\t\t &middot; <a class='{'active' if (O == '_points') else 'sort'}' href='index.html'>Points</a>\n")
				ofile.write(f"\t\t &middot; <a class='{'active' if (O == '_events') else 'sort'}' href='events.html'>Events</a>\n")
				#ofile.write(f"\t\t &middot; <a class='{'active' if (O == '_average') else 'sort'}' href='average.html'>Average</a>\n")
				ofile.write(f"\t\t &middot; <a class='{'active' if (O == '_maximum') else 'sort'}' href='maximum.html'>Maximum</a>\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='info'>\n")
				ofile.write(f"\t\tThe ranking below is based on a total of {strf(jinfo['Events'], 'events')} events played on <a href='https://lichess.org/'>lichess.org</a>, which in total featured {strf(jinfo['Games'], 'games')} games (with {strf(jinfo['Moves'], 'moves')} moves).\n")
				ofile.write(f"Overall, in these events white scored <span class='info' title='{jinfo['WhiteWins']} out of {jinfo['Games']} games'>{round(100 * jinfo['WhiteWins'] / jinfo['Games'])}%</span> wins, <span class='info' title='{jinfo['Games'] - jinfo['WhiteWins'] - jinfo['BlackWins']} out of {jinfo['Games']} games'>{round(100 * (jinfo['Games'] - jinfo['WhiteWins'] - jinfo['BlackWins']) / jinfo['Games'])}%</span> draws, and <span class='info' title='{jinfo['BlackWins']} out of {jinfo['Games']} games'>{round(100 * jinfo['BlackWins'] / jinfo['Games'])}%</span> losses.\n")
				ofile.write(f"The events in this ranking took place between <a title='First event' href='https://lichess.org/tournament/{jinfo['FirstID']}'>{DateString(jinfo['FirstStart'][0:10])}</a> and <a title='Last event' href='https://lichess.org/tournament/{jinfo['LastID']}'>{DateString(jinfo['LastStart'][0:10])}</a>.\n")
				ofile.write(f"\t\tIn total these events featured {strf(jinfo['Participants'], 'participants')} participants ({strf(jinfo['Players'], 'players')} unique players).\n")
				ofile.write(f"\t\tThe maximum number of participants in one event is <a title='Event with most players' href='https://lichess.org/tournament/{jinfo['MaxUsersID']}'>{jinfo['MaxUsers']}</a>.\n")
				ofile.write(f"\t\tThe highest score achieved in one event is <a title='Event with highest score' href='https://lichess.org/tournament/{jinfo['TopScoreID']}'>{jinfo['TopScore']}</a> by <a href='https://lichess.org/@/{jinfo['TopUser']}'>{jinfo['TopUser']}</a>.\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th class='rank'><span class='info' title='Ranking'>#</span>&nbsp;</th>\n")
				ofile.write("\t\t<th class='fidetitle'> </th>\n")
				ofile.write("\t\t<th class='username'>Username</th>\n")
				ofile.write("\t\t<th class='gold'><span style='font-family: lichess;' title='1st place finishes'>g</span></th>\n")
				ofile.write("\t\t<th class='silver'><span style='font-family: lichess;' title='2nd place finishes'>g</span></th>\n")
				ofile.write("\t\t<th class='bronze'><span style='font-family: lichess;' title='3rd place finishes'>g</span></th>\n")
				ofile.write("\t\t<th class='points'><span class='info' title='Total accumulated points'>Points</span></th>\n")
				ofile.write("\t\t<th class='events'>&nbsp;/ <span class='info' title='Events with at least 1 point'>Evts</span></th>\n")
				ofile.write("\t\t<th class='avg'><span class='info' title='Average points per event'>Avg</span></th>\n")
				ofile.write("\t\t<th class='max'><span class='info' title='Maximum score in one event'>Max</span></th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t</thead>\n")
				ofile.write("\t<tbody>\n")
				
				# Question mark: &#xe005; - information about rankings, etc.
				# Queen for titled?: 8
				# Marathons: \
				# Streamer battles: &#xe003;
				
				with open(f"{PathRank}{V}\\{E}\\{V}_{E}_players{O}.ndjson", "r") as rf:
					for Line in rf:
					
						# Process the player ranking
						dictio = json.loads(Line.strip())
						
						if dictio["Ranking"] % 2 == 0:
							ofile.write(f"\t<tr class='even'>\n")
						else:
							ofile.write(f"\t<tr class='odd'>\n")
						ofile.write(f"\t\t<td class='rank'>{dictio['Ranking']}.</td>\n")
						ofile.write(f"\t\t<td class='fidetitle'>{dictio.get('Title', ' ')}&nbsp;</td>\n")
						ofile.write(f"\t\t<td class='username'>")
						
						# Format usernames that have been closed/marked for boosting/marked for cheating
						if (dictio["Username"].lower() in PlayersClosed) or (dictio["Username"].lower() in PlayersTOS) or (dictio["Username"].lower() in PlayersBoost):
							ofile.write(f"<a class='closed' href='https://lichess.org/@/{dictio['Username']}'>{dictio['Username']}</a></td>\n")
						else:
							ofile.write(f"<a href='https://lichess.org/@/{dictio['Username']}'>{dictio['Username']}</a></td>\n")

						ofile.write(f"\t\t<td class='gold'>{dictio['Trophies'][0] if dictio['Trophies'][0] > 0 else ''}</td>\n")
						ofile.write(f"\t\t<td class='silver'>{dictio['Trophies'][1] if dictio['Trophies'][1] > 0 else ''}</td>\n")
						ofile.write(f"\t\t<td class='bronze'>{dictio['Trophies'][2] if dictio['Trophies'][2] > 0 else ''}</td>\n")
						ofile.write(f"\t\t<td class='points'>{dictio['Score']}</td>\n")
						ofile.write(f"\t\t<td class='events'>&nbsp;/ {dictio['Events'] - dictio.get('Zeros', 0)}</td>\n")
						ofile.write(f"\t\t<td class='avg'>{round(dictio['Score'] / max(1, dictio['Events'] - dictio.get('Zeros', 0)))}</td>\n")
						ofile.write(f"\t\t<td class='max'><a href='https://lichess.org/tournament/{dictio['TopScoreID']}'>{dictio['TopScore']}</a></td>\n")
						ofile.write(f"\t</tr>\n")
						
						if dictio["Ranking"] == nplayers:
							break
				
				ofile.write("\t</tbody>\n")
				ofile.write("</table>\n")
				ofile.write("</body>\n")
				ofile.write("</html>\n")

RankInfo = dict()
for V in Variants:
	RankInfo[V] = dict()
	for E in Events:	
		RankInfo[V][E] = dict()
		if not os.path.exists(f"{PathRank}{V}\\{E}\\{V}_{E}_ranking.json"):
			continue
		with open(f"{PathRank}{V}\\{E}\\{V}_{E}_ranking.json", "r") as rf:
			RankInfo[V][E] = json.load(rf)


# Separate pages for nice graphics

for V in Variants:
	for E in Events:		
		if not os.path.exists(f"{PathRank}{V}\\{E}\\{V}_{E}_ranking.json"):
			continue
		with open(f"{PathWeb}{V}\\{E}\\stats.html", "w") as ofile:			
			ofile.write("<!DOCTYPE html>\n")
			ofile.write("<html lang='en-US'>\n")
			ofile.write("<!-- Rankings built using the Lichess API (https://lichess.org/api) and some manual (python-based) tournament scraping. -->\n")
			ofile.write("<!-- Source code available at https://github.com/tmmlaarhoven/tmmlaarhoven.github.io -->\n")
			ofile.write("<head>\n")
			if E == "marathon":
				ofile.write(f"<title>Lichess Rankings &middot; {Variants[V]} Marathons</title>\n")
			elif V == "all" or E == "titled" or E == "shield":
				if V == "all" and E == "all":
					ofile.write("<title>Lichess Rankings &middot; All Arenas</title>\n")
				else:
					ofile.write(f"<title>Lichess Rankings &middot; {Variants[V]} {Events[E]} Rankings</title>\n")
			else:
				ofile.write(f"<title>Lichess Rankings &middot; {Events[E]} {Variants[V]} Rankings</title>\n")
			ofile.write("<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>\n")
			ofile.write("<link rel='icon' type='image/png' href='../../../favicon.ico'>\n")
			ofile.write("<link rel='stylesheet' href='../../../style.css'>\n")
			ofile.write("</head>\n")
			ofile.write("<table class='content'>\n")
			ofile.write("\t<thead>\n")
			ofile.write("\t<tr>\n")
			ofile.write("\t\t<th colspan='10' class='variant'>\n")
			#ofile.write("\t\t\t<a class='" + ("active" if (E == "all") else "back") + "' href='../all/" + Orders[O] + "'>All</a>\n")
			ofile.write("\t\t\t<a class='variant' href='../../index.html'><span style='font-family: lichess' title='About'>&#xe005;</span></a>\n")
			for index, mod in enumerate(VariantsOrdered):
				if os.path.exists(f"{PathRank}{mod}\\{E}\\{mod}_{E}_ranking.json"):
					ofile.write(f"\t\t\t &middot; <a class='{'active' if (V == mod) else 'variant'}' href='../../{mod}/{E}/stats.html'><span style='font-family: lichess' title='{VariantsOrdered[mod]}'>{VariantsOrderedIcons[mod]}</span></a>\n")
				else:
					ofile.write(f"\t\t\t &middot; <a class='{'active' if (V == mod) else 'variant'}' href='../../{mod}/all/stats.html'><span style='font-family: lichess' title='{VariantsOrdered[mod]}'>{VariantsOrderedIcons[mod]}</span></a>\n")
			ofile.write("\t\t</th>\n")
			ofile.write("\t</tr>\n")
			ofile.write("\t<tr>\n")
			ofile.write("\t\t<th colspan='10' class='type'>\n")
			ofile.write(f"\t\t<a class='{'active' if (E == 'all') else 'type'}' href='../all/stats.html'>All</a>\n")
			for eve in EventsOrdered:
				if os.path.exists(f"{PathRank}{V}\\{eve}\\{V}_{eve}_ranking.json"):
					ofile.write(f"\t\t &middot; <a class='{'active' if (E == eve) else 'type'}' href='../{eve}/stats.html'>{EventsOrdered[eve]}</a>\n")
				else:
					ofile.write(f"\t\t &middot; {EventsOrdered[eve]}\n")
			ofile.write("\t\t</th>\n")
			ofile.write("\t</tr>\n")
			ofile.write("\t<tr>\n")
			ofile.write("\t\t<th colspan='10' class='title'>\n")
			#ofile.write("\t\t<div class='lefticon'>" + VariantsOrderedIcons[V] + "</div>\n")
			if E == "marathon":
				ofile.write(f"\t\t{Variants[V]} Marathons\n")
			elif V == "all" or E == "titled" or E == "shield":
				if V == "all" and E == "all":
					ofile.write(f"\t\tAll Arenas\n")
				else:
					ofile.write(f"\t\t{Variants[V]} {Events[E]} Arenas\n")
			else:
				ofile.write(f"\t\t{Events[E]} {Variants[V]} Arenas\n")
			#ofile.write("\t\t<div class='righticon'>" + VariantsOrderedIcons[V] + "</div>\n")
			ofile.write("\t\t</th>\n")
			ofile.write("\t</tr>\n")
			ofile.write("\t<tr>\n")
			ofile.write("\t\t<th colspan='10' class='sort'><a class='active' href='stats.html'>Show arena stats</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Show rankings sorted by: &nbsp;\n")
			ofile.write("\t\t<a class='sort' href='trophies.html'>Trophies</a>\n")
			ofile.write("\t\t &middot; <a class='sort' href='index.html'>Points</a>\n")
			ofile.write("\t\t &middot; <a class='sort' href='events.html'>Events</a>\n")
			#ofile.write("\t\t &middot; <a class='sort' href='average.html'>Average</a>\n")
			ofile.write("\t\t &middot; <a class='sort' href='maximum.html'>Maximum</a>\n")
			ofile.write("\t\t</th>\n")
			ofile.write("\t</tr>\n")
			ofile.write("\t<tr>\n")
			ofile.write("\t\t<th colspan='10' class='info' style='padding: 0px; spacing: 0px;'>\n")
			ofile.write("\t\t<figure style='display: inline-block; padding: 0px; spacing: 0px;'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_players.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_games.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_points.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_moves.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_rating.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_berserk.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_topscore.png'>\n")
			ofile.write(f"\t\t<img src='figures/{V}_{E}_arena_results.png'>\n")
			ofile.write("\t\t</figure>\n")
			ofile.write("\t\t</th>\n")
			ofile.write("\t</thead>\n")	
			#ofile.write("\t<tfoot>\n")
			#ofile.write("\t<tr>\n")
			#ofile.write("\t\t<td colspan='10'><a href='hmm.html'>Download full CSV file</a></td>\n")
			#ofile.write("\t</tr>\n")
			#ofile.write("\t</tfoot>\n")
			ofile.write("</table>\n")
			ofile.write("</body>\n")
			ofile.write("</html>\n")

################################################################
# Index page with statistics
################################################################

others = {"Lichess Rankings": "index.html", "Statistics": "stats.html", "Titled Arenas": "titled.html", "Seasonal Marathons": "marathon.html", "Special Events": "special.html", "About": "about.html"}
for oth in others:
	print("Building " + others[oth] + "...")
	with open(PathWeb + others[oth], "w") as ofile:			
		ofile.write("<!DOCTYPE html>\n")
		ofile.write("<html lang='en-US'>\n")
		ofile.write("<!-- Rankings built using the Lichess API (https://lichess.org/api) and some manual (python-based) tournament scraping -->\n")
		ofile.write("<head>\n")
		ofile.write("<title>Lichess Rankings &middot; " + oth + "</title>\n")
		ofile.write("<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>\n")
		ofile.write("<link rel='icon' type='image/png' href='../favicon.ico'>\n")
		ofile.write("<link rel='stylesheet' href='../style.css'>\n")
		ofile.write("</head>\n")
		ofile.write("<table class='content'>\n")
		ofile.write("\t<thead>\n")
		ofile.write("\t<tr>\n")
		ofile.write("\t\t<th colspan='10' class='variant'>\n")
		#ofile.write("\t\t\t<a class='" + ("active" if (E == "all") else "back") + "' href='../all/" + Orders[O] + "'>All</a>\n")
		ofile.write("\t\t\t<a class='active' href='index.html'><span style='font-family: lichess' title='About'>&#xe005;</span></a>\n")
		for mod in VariantsOrdered:
			ofile.write(f"\t\t\t &middot; <a class='variant' href='{mod}/all/index.html'><span style='font-family: lichess' title='{VariantsOrdered[mod]}'>{VariantsOrderedIcons[mod]}</span></a>\n")
		ofile.write("\t\t</th>\n")
		ofile.write("\t</tr>\n")
		ofile.write("\t<tr>\n")
		ofile.write("\t\t<th colspan='10' class='type'>\n")
		ofile.write("\t\t<a class='" + ("active" if oth == "Lichess Rankings" else "type") + "' href='index.html'>Information</a>\n")
		ofile.write("\t\t &nbsp; &middot; &nbsp; <a class='" + ("active" if oth == "Statistics" else "type") + "' href='stats.html'>Statistics</a>\n")
		ofile.write("\t\t &nbsp; &middot; &nbsp; <a class='" + ("active" if oth == "Titled Arenas" else "type") + "' href='titled.html'>Titled Arenas</a>\n")
		ofile.write("\t\t &nbsp; &middot; &nbsp; <a class='" + ("active" if oth == "Seasonal Marathons" else "type") + "' href='marathon.html'>Seasonal Marathons</a>\n")
		ofile.write("\t\t &nbsp; &middot; &nbsp; <a class='" + ("active" if oth == "Special Events" else "type") + "' href='special.html'>Special Events</a>\n")
		ofile.write("\t\t &nbsp; &middot; &nbsp; <a class='" + ("active" if oth == "About" else "type") + "' href='about.html'>About</a>\n")
		ofile.write("\t\t &nbsp; &middot; &nbsp; <a class='type' href='https://github.com/tmmlaarhoven/tmmlaarhoven.github.io'>Source code</a>\n")
		ofile.write("\t\t</th>\n")
		ofile.write("\t</tr>\n")
		ofile.write("\t<tr>\n")
		ofile.write("\t\t<th colspan='10' class='title'>\n")
		#ofile.write("\t\t<div class='lefticon'>&#xe005;</div>\n")
		ofile.write(f"\t\t{oth}\n")
		#ofile.write("\t\t<div class='righticon'>&#xe005;</div>\n")
		ofile.write("\t\t</th>\n")
		ofile.write("\t</tr>\n")
		# ofile.write("\t<tr>\n")
		# ofile.write("\t\t<th colspan='10' class='sort'>Most recent tournament: <a title='Most recent event' href='https://lichess.org/tournament/" + RankInfo["all"]["all"]["LastID"] + "'>" + DateString(RankInfo["all"]["all"]["laststart"][0:10]) + "</a>\n")
		# ofile.write("\t\t</th>\n")
		# ofile.write("\t</tr>\n")
		ofile.write("\t<tr>\n")
		ofile.write("\t\t<th colspan='10' class='about'>\n")
		###############################################################################
		if oth == "Lichess Rankings":
			ofile.write("\t\t<span style='padding-top: 0px; font-style: italic; color: #888888;'>Most recent tournament: <a title='Most recent event' href='https://lichess.org/tournament/" + RankInfo["all"]["all"]["LastID"] + "'>" + DateString(RankInfo["all"]["all"]["LastStart"][0:10]) + "</a>. To navigate the rankings, use the icons above. The icon <span style='font-family: lichess;'>" + VariantsOrderedIcons["all"] + "</span> refers to global rankings for all categories combined. The duplicate icons for bullet and blitz are used to distinguish between (hyper)bullet and (super)blitz arenas.</span>\n")
			#ofile.write("\t\t<h1 class='about'>About</h1>\n")
			ofile.write("\t\t<p>The rankings on this webpage are based on all regularly-scheduled arenas played on <a href='https://lichess.org/'>lichess.org</a> (hourly, daily, weekly, monthly, yearly, eastern, elite, and shield arenas) as well as the <a href='all/marathon/index.html'>seasonal 24h marathons</a> and the <a href='all/titled/trophies.html'>titled arenas</a>. These rankings exclude irregular rating-restricted events (<1700 Bullet Arena, ...), themed arenas (King's Gambit Blitz Arena, ...), and arenas created by Lichess users. In total the rankings cover " + strf(RankInfo["all"]["all"]["Events"], "events") + " events, which had a total of " + strf(RankInfo["all"]["all"]["Players"], "players") + " unique players participating in the events.</p>") 
			ofile.write("<p>Additional, detailed statistics can be found on the <a href='stats.html'>statistics</a> page.</p>")
		###############################################################################
		elif oth == "Statistics":
			ofile.write("\t\tWith all the data about these tournaments available, we can obtain various statistics that tell us more about the average user, the popularity of different variants and time controls, and the growth of Lichess over time. Below we list some more detailed statistics.\n")
			
			# === Data by partition ===
			ofile.write("\t\t<h2 class='head'>Partitioning the data</h2>\n")
			
			# === VARIANT STATISTICS ===
			ofile.write("\t\tThe events in this ranking can be classified into 15 different time controls and/or variants, as listed below.\n")
			ofile.write("\t\t<ul style='list-style-type: none;'>\n")
			for V in VariantsOrdered:
				if V == "all":
					continue
				ofile.write(f"\t\t\t<li><span style='color: #BF811D;'><span style='font-family: lichess;'>{VariantsOrderedIcons[V]}</span> &nbsp;{Variants[V]}:</span> &nbsp; {strf(RankInfo[V]['all']['Events'], 'events')} events, {strf(RankInfo[V]['all']['Players'], 'players')} players, {strf(RankInfo[V]['all']['Moves'], 'moves')} moves, {strf(RankInfo[V]['all']['Games'], 'games')} games, {strf(RankInfo[V]['all'].get('TotalPoints', 0), 'points')} points.</li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<p>Partitioning the events included in the rankings by type, we unsurprisingly see that there were many more hourly arenas than yearly arenas. At the same time yearly arenas are more special (and generally last longer) and therefore get more participants per event than hourly arenas.</p>\n")
			ofile.write("\t\t<ul style='list-style-type:none;'>\n")
			for E in Events:
				if (E == "all") or (E[0] == "2" and E[2] != "0"):
					continue
				ofile.write(f"\t\t\t<li><span style='color: #BF811D;'>{Events[E]}:</span> &nbsp; {strf(RankInfo['all'][E].get('Events', 0), 'events')} events, {strf(RankInfo['all'][E].get('Players', 0), 'players')} players, {strf(RankInfo['all'][E].get('Moves', 0), 'moves')} moves, {strf(RankInfo['all'][E].get('Games', 0), 'games')} games, scoring {strf(RankInfo['all'][E].get('Points', 0), 'points')} points.</li>\n")
			ofile.write("\t\t</ul>\n")
			
			# === YEARLY STATISTICS ===
			#ofile.write("\t\t<p>When partitioning the events according to the year they were played in, we obtain the following overview. The first regular events included in these rankings took place in 2014. As Lichess has grown over the years, one can see that the number of players as well as the number of events has grown rapidly over time. (Part of the growth in 2020 might be attributed to the spread of COVID-19, with people around the world being forced to spend more time indoor and online, thus resulting in more people playing online than usual.)</p>\n")
			#ofile.write("\t\t<ul style='list-style-type:none;'>\n")
			#for E in Events:
			#	if not (E[0] == "2" and E[2] != "0"):
			#		continue
			#	if not "events" in RankInfo["all"][E]:
			#		continue
			#	ofile.write("\t\t\t<li><span style='color: #BF811D;'>" + Events[E] + ":</span> &nbsp; " + strf(RankInfo["all"][E].get("events", 0), "events") + " events, " + strf(RankInfo["all"][E].get("players", 0), "players") + " players, " + strf(RankInfo["all"][E].get("Moves", 0), "moves") + " moves, " + strf(RankInfo["all"][E].get("Games", 0), "games") + " games, scoring " + strf(RankInfo["all"][E].get("points", 0), "points") + " points.</li>\n")
			#ofile.write("\t\t</ul>\n")
			
			# === COMPLETE BREAKDOWN ===
			ofile.write("\t\t<p>For an even more detailed breakdown of all events in these rankings in terms of types and variants, see the following table. Percentages in this table are rounded to the nearest integer; 1% means \"between 0.5% and 1.5%\" and 0% means \"less than 0.5%\", while a dash in all tables below means that no events in this combination of categories took place. Almost 30% of all events are bullet arenas, and as they take place (almost) every hour, almost 90% of the events included in these rankings are hourly arenas.</p>\n")
			ofile.write("\t\t<h2 class='stats'>Classification of all events</h2>\n")
			fpctevents = lambda r, m, e: (str(round(100 * r[m][e].get("Events", 0) / r["all"]["all"].get("Events", 1))) + "%") if "Events" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, fpctevents)
			#ofile.write("\t\t<h2 class='stats'>Classification of all points</h2>\n")
			#fpctevents = lambda r, m, e: (str(round(100 * r[m][e].get("Games", 0) / r["all"]["all"].get("Games", 1))) + "%") if "events" in r[m][e] else "-"
			#StatisticsTable(ofile, RankInfo, fpctevents)
			#ofile.write("\t\t<h2 class='stats'>Percentages  all points</h2>\n")
			#fpctevents = lambda r, m, e: (str(round(100 * r[m][e].get("points", 0) / r["all"]["all"].get("points", 1))) + "%") if "events" in r[m][e] else "-"
			#StatisticsTable(ofile, RankInfo, fpctevents)
			
			# === MORE STATISTICS ===
			ofile.write("\t\t<h2 class='head'>Event statistics</h2>\n")
			ofile.write("\t\t<p>The tables below summarize various statistics per game type and per event type of arena tournaments. We briefly discuss some things one may conclude from these tables below.</p>\n")
			ofile.write("\t\t<ul>\n")
			ofile.write("\t\t\t<li><span class='title'>Average participants per event:</span> Overall, the average number of participants per event is <span class='dgreen'>" + str(round(RankInfo["all"]["all"].get("Participants", 0) / RankInfo["all"]["all"].get("Events", 1))) + " players</span>. Overall, rapid events see the most participants on average, and whereas all standard time controls have an average participation of over 100 players (and around 90 for chess 960), all non-standard chess variants have an average of fewer than 60 players per event.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average ratings per event:</span> While average ratings across Lichess may be around 1500, tournaments seem to have a bias towards higher-rated players. As lower-rated players have no chance of winning these events, they may prefer matchmaking over random arena pairings where they lose most of their games. Overall, the average rating in events is around <span class='dgreen'>" + str(round(RankInfo["all"]["all"].get("TotalRating", 0) / RankInfo["all"]["all"].get("Participants", 1))) + "</span>, with slightly higher averages in faster time controls and in crazyhouse. As for types of events with higher averages, we naturally see peaks for titled arenas and elite arenas, which are only open to high-rated players.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average points per player per event:</span> Overall, an average arena participant scored around <span class='dgreen'>" + str(round(RankInfo["all"]["all"].get("TotalPoints", 0) / RankInfo["all"]["all"].get("Participants", 1))) + " points</span>. With many players joining for only a few games, and some players playing the entire events and scoring many points, the median is even lower. The average number of points is highest for quick time controls, where it is easier to play many games in a short amount of time.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Maximum points achieved in one event:</span> Looking only at the highest scores ever achieved in arenas, we see that the highest score ever achieved was by <span class='title'>GM</span> <a href='https://lichess.org/@/penguingim1'>penguingim1</a> in one of the bullet marathons, scoring <span class='dgreen'>1645 points</span>. (As explained on the page with <a href='special.html'>special events</a> this is not the maximum score ever achieved, as six players have scored over 2000 points in 24-hour hyperbullet events.)</li>\n")
			ofile.write("\t\t</ul>\n")
			#ofile.write("\t\t<p>Average participants per event:</p>\n")
			ofile.write("\t\t<h2 class='stats'>Average participants per event</h2>\n")
			favgplayers = lambda r, m, e: ("<span style='font-size: 9pt;'>" + str(round(r[m][e].get("Participants", 0) / max(r[m][e].get("Events", 1), 1))) + "</span>") if "Participants" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, favgplayers)
			ofile.write("\t\t<h2 class='stats'>Average ratings per event</h2>\n")
			favgrating = lambda r, m, e: ("<span style='font-size: 9pt;'>" + str(round(r[m][e].get("TotalRating", 0) / max(r[m][e].get("Participants", 1), 1))) + "</span>") if "TotalRating" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, favgrating)
			ofile.write("\t\t<h2 class='stats'>Average points per player per event</h2>\n")
			favgpoints = lambda r, m, e: (str(round(r[m][e].get("Points", 0) / max(r[m][e].get("Participants", 1), 1)))) if "Points" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, favgpoints)
			ofile.write("\t\t<h2 class='stats'>Maximum points achieved in one event</h2>\n")
			fmax = lambda r, m, e: ("<a title='" + r[m][e].get("TopUser", "") + "' href='https://lichess.org/tournament/" + r[m][e].get("TopScoreID") + "'>" + str(r[m][e].get("TopScore")) + "</a>") if ("TopScore" in r[m][e]) else "-"
			StatisticsTable(ofile, RankInfo, fmax)
			
			ofile.write("\t\t<h2 class='head'>Game statistics</h2>\n")
			ofile.write("\t\t<p>Finally, below are some tables listing game statistics per game type and per event type. We again briefly highlight some things one might observe in these tables.</p>\n")
			ofile.write("\t\t<ul>\n")
			ofile.write("\t\t\t<li><span class='title'>Average moves per player per game:</span> On average, games played in all these events lasted around <span class='dgreen'>" + str(round(RankInfo["all"]["all"].get("Moves", 0) / RankInfo["all"]["all"].get("Games", 1) / 2)) + " moves</span>. In terms of variants, both extremely short (ultrabullet) and long time controls (classical) have a slightly lower average than \"medium\" time controls such as superblitz or blitz. Of the variants, racing kings (14), atomic (16), and three-check (18) have the lowest average moves per game due to the nature of these variants, while in horde (46) the average is significantly higher than for standard chess games. With the higher average rating and with more at stake, titled arenas (and elite arenas) have a higher average number of moves per game as well.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average score of white players:</span> While white may have a slight edge in chess in general, a (large) difference in playing strength will easily offset this small advantage. Overall, in all arenas combined, white players have scored approximately <span class='dgreen'>" + str(round(100 * RankInfo["all"]["all"].get("WhiteWins", 0) / RankInfo["all"]["all"].get("Games", 1) + 100 * (RankInfo["all"]["all"].get("Games", 0) - RankInfo["all"]["all"].get("WhiteWins", 0) - RankInfo["all"]["all"].get("BlackWins", 0)) / RankInfo["all"]["all"].get("Games", 1) / 2)) + "%</span>. White still scores slightly more than 50% in (almost) all events, except in horde, where the black player seems to have a slight edge over white. We further notice a slightly larger win percentage for white in atomic, three-check, and crazyhouse, and due to the higher level of play and the narrower range of playing strengths in these events, in both elite arenas and titled arenas white players score slightly better with a 52% score.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average percentage of draws:</span> As most tournaments are open to a wide range of ratings, and as shorter games played online are more often decisive, it is no surprise that the overall percentage of draws is only around <span class='dgreen'>" + str(round(100 * (RankInfo["all"]["all"].get("Games", 0) - RankInfo["all"]["all"].get("WhiteWins", 0) - RankInfo["all"]["all"].get("BlackWins", 0)) / RankInfo["all"]["all"].get("Games", 1))) + "%</span>. This percentage is even lower at faster time controls and some variants like crazyhouse and three-check, while racing kings has a remarkably high draw percentage of around 10%.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average percentage of berserked games:</span> On average, players choose the berserk option in around <span class='dgreen'>" + str(round(100 * RankInfo["all"]["all"].get("Berserks", 0) / RankInfo["all"]["all"].get("Games", 1) / 2)) + "%</span> of their arena games. This percentage is slightly higher (20% or more) for slow time controls, since losing half the clock time still leaves plenty of time to play a serious game. In non-standard chess variants, berserking seems especially popular in atomic and racing kings events, a statistic which may be closely related to the lower average game lengths in these variants; if games are often decided in fewer moves, losing time on the clock is not as important as for long games played in e.g. horde arenas.</li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<h2 class='stats'>Average moves per player per game</h2>\n")
			favgmoves = lambda r, m, e: (strf(round(r[m][e].get("Moves", 0) / max(r[m][e].get("Games", 1), 1) / 2), "moves")) if "Moves" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, favgmoves)
			ofile.write("\t\t<h2 class='stats'>Average score of white players</h2>\n")
			favgwhite = lambda r, m, e: (str(round(100 * r[m][e].get("WhiteWins", 0) / max(r[m][e].get("Games", 1), 1) + 100 * (r[m][e].get("Games", 0) - r[m][e].get("WhiteWins", 0) - r[m][e].get("BlackWins", 0)) / max(r[m][e].get("Games", 1), 1) / 2)) + "%") if "Participants" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, favgwhite)
			ofile.write("\t\t<h2 class='stats'>Average percentage of draws</h2>\n")
			favgdraws = lambda r, m, e: (str(round(100 * (r[m][e].get("Games", 0) - r[m][e].get("WhiteWins", 0) - r[m][e].get("BlackWins", 0)) / max(r[m][e].get("Games", 1), 1))) + "%") if "Participants" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, favgdraws)
			ofile.write("\t\t<h2 class='stats'>Average percentage of berserked games</h2>\n")
			fberserk = lambda r, m, e: (str(round(100 * r[m][e].get("Berserks", 0) / max(r[m][e].get("Games", 1), 1) / 2)) + "%") if "Berserks" in r[m][e] else "-"
			StatisticsTable(ofile, RankInfo, fberserk)
			
		###############################################################################
		elif oth == "Titled Arenas":	

			with open(PathRank + "all\\titled\\all_titled_ranking.json", "r") as rf:
				rinfo = json.load(rf)
				
			ofile.write("\t\tEver since the end of 2017, Lichess has been regularly hosting \"Titled Arenas\", open only to titled players and with a total prize fund of at least $1000 each. The <a href='https://lichess.org/tournament/GToVqkC9'>first titled arena</a> was won by world champion Magnus Carlsen, and he has regularly participated in (and won) titled arenas since then under different aliases. Recently Alireza Firouzja has won many titled arenas as well, and is approaching Magnus' record number of titled arena victories. In total there have now been " + str(rinfo["Events"]) + " titled arenas, with " + str(rinfo["Players"]) + " unique players taking part in one or more of these events.\n")
			ofile.write("\t\t<p>The titled arenas are included in the rankings (see the overall rankings <a href='all/titled/trophies.html'>here</a>), and for completeness all events are listed below in chronological O, with the most recent events first.</p>\n")
			ofile.write("\t\t<table>")

			# Keep track of number of rankings, put four on each row
			nevents = 0
		
			# Load ranking info
			tdata = {}
			with open(PathRank + "all\\titled\\all_titled_ranking.ndjson", "r") as rf:
				for Line in rf:
					dictio = json.loads(Line)
					tdata[dictio["ID"]] = dictio
					tdata[dictio["ID"]]["Top10"] = []
					with open(PathData + dictio["Variant"] + "\\titled\\" + dictio["Variant"] + "_titled_" + dictio["ID"] + ".ndjson", "r") as ran:
						for index, Line in enumerate(ran):
							player = json.loads(Line)
							dicti = {"Username": player["username"], "Score": player["score"]}
							if "Title" in player:
								dicti["Title"] = player["title"]
							tdata[dictio["ID"]]["Top10"].append(dicti)
							if index == 9:
								break

			# Compact ranking for each event type
			for id in reversed(list(tdata.keys())):
				
				# Stylize results in html
				if nevents == 0:
					ofile.write("\t\t\t<tr style='height: 200px'>\n")
				ofile.write("\t\t\t\t<td valign='top' style='padding: 10px;'>\n")
				ofile.write("\t\t\t\t<table class='minitable'>\n")
				ofile.write("\t\t\t\t\t<thead>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<th class='minitable' colspan='3'><span style='color: #888888; font-size: 10pt;'>" + DateString(tdata[id]["Start"][0:10]) + "</span><br/><span style='font-family: lichess; font-size: 10pt;'>C</span> Titled Arena " + str(tdata[id]["Number"]) + "</th>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</thead>")
				ofile.write("\t\t\t\t\t<tbody>\n")
				for i in range(10):
					ofile.write("\t\t\t\t\t<tr class='" + ("even" if (i % 2 == 0) else "odd") + "'>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitabletitle'>" + (("<span style='color: #BF811D;'>" + tdata[id]["Top10"][i].get("Title", "") + "</span> ") if "Title" in tdata[id]["Top10"][i] else "") + "</td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablename'><a href='https://lichess.org/@/" + tdata[id]["Top10"][i]["Username"] + "'>" + tdata[id]["Top10"][i]["Username"] + "</a></td>\n")
					ofile.write("\t\t\t\t\t\t<td style='padding-right: 10px;' align='right'>" + str(tdata[id]["Top10"][i]["Score"]) + "</td>\n")						
					ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<td colspan='3' class='minitablefoot'>" + str(tdata[id]["Players"]) + " players &middot; <a href='https://lichess.org/tournament/" + id + "'>More info</a></td>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</tbody>\n")
				ofile.write("\t\t\t\t</table>\n")
				ofile.write("\t\t\t\t</td>\n")
				nevents += 1
				if nevents == 3:
					ofile.write("\t\t\t</tr>\n")
					nevents = 0	
			ofile.write("\t\t</table>\n")
		###############################################################################
		elif oth == "Seasonal Marathons":	
		
			# Load ranking info
			tdata = {}
			with open(PathRank + "all\\marathon\\all_marathon_ranking.ndjson", "r") as rf:
				for Line in rf:
					dictio = json.loads(Line)
					tdata[dictio["ID"]] = dictio
					tdata[dictio["ID"]]["Top10"] = []
					with open(PathData + dictio["Variant"] + "\\marathon\\" + dictio["Variant"] + "_marathon_" + dictio["ID"] + ".ndjson", "r") as ran:
						for index, Line in enumerate(ran):
							player = json.loads(Line)
							dicti = {"Username": player["username"], "Score": player["score"]}
							if "Title" in player:
								dicti["Title"] = player["title"]
							tdata[dictio["ID"]]["Top10"].append(dicti)
							if index == 9:
								break
								
			with open(PathRank + "all\\marathon\\all_marathon_ranking.json", "r") as rf:
				rinfo = json.load(rf)
		
			ofile.write("\t\tFour times a year, Lichess hosts a 24h marathon event with varying time controls, with the top players obtaining a unique trophy displayed on their user profile. These events have taken place since the summer of 2015, and numerous events have been won by Lichess veteran <span class='title'>LM</span> <a href='https://lichess.org/@/Lance5500'>Lance5500</a>. In total there have now been " + str(rinfo["Events"]) + " seasonal marathons, with " + strf(rinfo["Players"], "players") + " unique players taking part in one or more of these events.\n")
			ofile.write("\t\t<p>The marathons are included in the rankings (see the overall rankings <a href='all/marathon/index.html'>here</a>), and for completeness all events are listed below in chronological order, with the most recent events first.</p>\n")
			ofile.write("\t\t<table>")

			# Keep track of number of rankings, put four on each row
			nevents = 0

			# Compact ranking for each event type
			for id in reversed(list(tdata.keys())):
				
				# Stylize results in html
				# "clock":{"limit":300,"increment":0}
				if nevents == 0:
					ofile.write("\t\t\t<tr style='height: 200px'>\n")
				ofile.write("\t\t\t\t<td valign='top' style='padding: 10px;'>\n")
				ofile.write("\t\t\t\t<table class='minitable'>\n")
				ofile.write("\t\t\t\t\t<thead>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<th class='minitable' colspan='3'><span style='color: #888888; font-size: 10pt;'>" + DateString(tdata[id]["Start"][0:10]))
				
				# Fetch clock times for convenience
				with open(PathData + tdata[id]["Variant"] + "\\marathon\\" + tdata[id]["Variant"] + "_marathon_" + tdata[id]["ID"] + ".json", "r") as getclock:
					dictia = json.load(getclock)
					ofile.write(" • " + str(int(dictia["clock"]["limit"]/60)) + "+" + str(int(dictia["clock"]["increment"])) + "")
				
				ofile.write("</span><br/><span style='font-family: lichess; font-size: 10pt;'>\</span> " + id[0:1].upper() + id[1:6] + " 20" + id[6:8] + "</th>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</thead>")
				ofile.write("\t\t\t\t\t<tbody>\n")
				for i in range(10):
					ofile.write("\t\t\t\t\t<tr class='" + ("even" if (i % 2 == 0) else "odd") + "'>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitabletitle'>" + (("<span style='color: #BF811D;'>" + tdata[id]["Top10"][i].get("Title", "") + "</span> ") if "Title" in tdata[id]["Top10"][i] else "") + "</td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablename'><a href='https://lichess.org/@/" + tdata[id]["Top10"][i]["Username"] + "'>" + tdata[id]["Top10"][i]["Username"] + "</a></td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablescore'>" + str(tdata[id]["Top10"][i]["Score"]) + "</td>\n")						
					ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<td colspan='3' class='minitablefoot'>" + str(tdata[id]["Players"]) + " players &middot; <a href='https://lichess.org/tournament/" + id + "'>More info</a></td>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</tbody>\n")
				ofile.write("\t\t\t\t</table>\n")
				ofile.write("\t\t\t\t</td>\n")
				nevents += 1
				if nevents == 3:
					ofile.write("\t\t\t</tr>\n")
					nevents = 0	
			ofile.write("\t\t</table>\n")
		###############################################################################
		# elif oth == "Special Events":	
			# ofile.write("\t\tBesides user-generated arenas and rating-restricted events, various other special (official) arenas are not included in the rankings. These include warm-up arenas before titled arenas, one-time celebratory events, charity fundraisers, and privately-funded events with prize money. Special thanks go out to BitChess, sponsoring various events from 2016-2017, and <a href='https://lichess.org/@/FischyVischy'>FischyVischy</a>, sponsoring prize funds for Revolutions, Apocalypses, and numerous other Variants events and championships over the years.\n")
			# ofile.write("\t\t<p>We further highlight a few (series of) tournaments below:</p>\n")
			# ofile.write("\t\t<ul>\n")
			# ofile.write("\t\t\t<li><span class='title'>Highest scores:</span> A few 24h HyperBullet events have taken place on lichess, and naturally due to the low time control and long duration these have led to some of the highest scores ever recorded in a single arena. Users who scored more than <span class='dgreen'>2000 points</span> in one event include:\n")
			# ofile.write("\t\t\t<ul>\n")
			# ofile.write("\t\t\t\t<li><span class='title'>GM</span> <a href='https://lichess.org/@/penguingim1'>penguingim1</a> (<span class='dgreen'>2145</span>) and <span class='title'>GM</span> <a href='https://lichess.org/@/Tayka'>Tayka</a> (<span class='dgreen'>2023</span>) in the <a href='https://lichess.org/tournament/JBFIv9sW'>BitChess 24h Hyperbullet</a> arena;\n")
			# ofile.write("\t\t\t\t<li><a href='https://lichess.org/@/Mr_Crabs'>Mr_Crabs</a> (<span class='dgreen'>2209</span>) and <span class='title'>IM</span> <a href='https://lichess.org/@/taheryoseph'>taheryoseph</a> (<span class='dgreen'>2042</span>) in the <a href='https://lichess.org/tournament/mfNJAKiv'>GM Andrew Tang Hyper Celebration</a> event;")
			# ofile.write("\t\t\t\t<li><span class='title'>IM</span> <a href='https://lichess.org/@/toivok3'>toivok3</a> (<span class='dgreen'>2311</span>) and <span class='title'>IM</span> <a href='https://lichess.org/@/kiketf'>kiketf</a> (<span class='dgreen'>2122</span>) in the <a href='https://lichess.org/tournament/iS9Qmstg'>Opperwezen Roundabout</a>.\n")
			# ofile.write("\t\t\t</ul>For variants such as Racing Kings and King of the Hill, the series of 24h \"Revolution\" events listed below contain some of the highest scores for these variants as well.</li>\n")
			# ofile.write("\t\t\t<li><span class='title'>Anniversaries:</span> Lichess hosted celebratory anniversary events in <a href='https://lichess.org/tournament/21ZMAsPg'>2020</a>, <a href='https://lichess.org/tournament/wEKI0Mrr'>2019</a>, and <a href='https://lichess.org/tournament/zqcpQFzR'>2018</a>. YouTube celebrity <a href='https://lichess.org/@/agadmator'>agadmator</a> hosted prize events when reaching YouTube milestones of <a href='https://lichess.org/tournament/Dd1kyEhY'>500k</a>, <a href='https://lichess.org/tournament/iRIDczTE'>400k</a>, <a href='https://lichess.org/tournament/7ctguzuH'>200k</a>, and <a href='https://lichess.org/tournament/sHsu5Yv2'>100k</a> YouTube subscribers.</li>\n")
			# #ofile.write("\t\t\t<li><span class='title'>Streamer Battles:</span> ...</li>\n")
			# ofile.write("\t\t\t<li><span class='title'>Charity events:</span> Some charity events hosted on Lichess include a tournament for the <a href='https://lichess.org/tournament/C696te7d'>Black Lives Matter</a> movement, the COVID-19 fundraisers <a href='https://lichess.org/tournament/0t0GLWau'>Offerspill Relief</a> and <a href='https://lichess.org/tournament/nn4UF6mP'>Marathon pour Mercy</a>, and the <a href='https://lichess.org/tournament/JBH25ivF'>Solidarity With Beirut</a> arena for the victims in Beirut.</li>\n")
			# #ofile.write("\t\t\t<li><b><span class='title'></span><b>: ...</b></li>\n")
			# ofile.write("\t\t</ul>\n")
			# ofile.write("\t\t<p>A complete overview of the top 10 in each of these arenas is listed below, chronologically starting at the most recent events.\n")
			# ofile.write("\t\t<table>")

			# # Keep track of number of rankings, put four on each row
			# nevents = 0
		
			# # Load ranking info
			# titev = []
			# with open(PathRank + "all\\titled\\all_titled_ranking.ndjson", "r") as rft:
				# for Line in rft:
					# dictioo = json.loads(Line)
					# titev.append(dictioo["ID"])
					
			# tdata = {}
			# with open(PathData + "special\\special.ndjson", "r") as rf:
				# for Line in rf:
					# dictio = json.loads(Line)
					# if dictio["ID"] in titev:
						# continue
					# tdata[dictio["ID"]] = dictio					
					# tdata[dictio["ID"]]["Top10"] = []
					# with open(PathData + "special\\special_" + dictio["ID"] + ".ndjson", "r") as ran:
						# for index, Line in enumerate(ran):
							# player = json.loads(Line)
							# dicti = {"Username": player["Username"], "Score": player["Score"]}
							# if "Title" in player:
								# dicti["Title"] = player["Title"]
							# tdata[dictio["ID"]]["Top10"].append(dicti)
							# if index == 9:
								# break

			# # Compact ranking for each event type
			# for id in reversed(list(tdata.keys())):
				
				# # Stylize results in html
				# if nevents == 0:
					# ofile.write("\t\t\t<tr style='height: 200px'>\n")
				# ofile.write("\t\t\t\t<td valign='top' style='padding: 10px;'>\n")
				# ofile.write("\t\t\t\t<table class='minitable'>\n")
				# ofile.write("\t\t\t\t\t<thead>\n")
				# ofile.write("\t\t\t\t\t<tr>\n")
				# ofile.write("\t\t\t\t\t\t<th class='minitable' colspan='3'><span style='color: #888888; font-size: 10pt;'>" + DateString(tdata[id]["Start"][0:10]) + "</span><br/><span style='font-size: 9pt;'>" + tdata[id]["Name"] + "</span></th>\n")
				# ofile.write("\t\t\t\t\t</tr>\n")
				# ofile.write("\t\t\t\t\t</thead>")
				# ofile.write("\t\t\t\t\t<tbody>\n")
				# for i in range(10):
					# ofile.write("\t\t\t\t\t<tr class='" + ("even" if (i % 2 == 0) else "odd") + "'>\n")
					# ofile.write("\t\t\t\t\t\t<td class='minitabletitle'>" + (("<span style='color: #BF811D;'>" + tdata[id]["Top10"][i].get("Title", "") + "</span> ") if "Title" in tdata[id]["Top10"][i] else "") + "</td>\n")
					# ofile.write("\t\t\t\t\t\t<td class='minitablename'><a href='https://lichess.org/@/" + tdata[id]["Top10"][i]["Username"] + "'>" + tdata[id]["Top10"][i]["Username"] + "</a></td>\n")
					# ofile.write("\t\t\t\t\t\t<td class='minitablescore'>" + str(tdata[id]["Top10"][i]["Score"]) + "</td>\n")						
					# ofile.write("\t\t\t\t\t</tr>\n")
				# ofile.write("\t\t\t\t\t<tr>\n")
				# ofile.write("\t\t\t\t\t\t<td colspan='3' class='minitablefoot'>" + str(tdata[id]["Players"]) + " players &middot; <a href='https://lichess.org/tournament/" + id + "'>More info</a></td>\n")
				# ofile.write("\t\t\t\t\t</tr>\n")
				# ofile.write("\t\t\t\t\t</tbody>\n")
				# ofile.write("\t\t\t\t</table>\n")
				# ofile.write("\t\t\t\t</td>\n")
				# nevents += 1
				# if nevents == 3:
					# ofile.write("\t\t\t</tr>\n")
					# nevents = 0	
			# ofile.write("\t\t</table>\n")
		###############################################################################
		elif oth == "About":
			ofile.write("\t\tTo follow later with how these rankings were made, an explanation of the python scripts, and perhaps an online repository with all the data that was used to generate these rankings. (In total my hard drive contains around 560,000 files used to generate these pages, which together take up around 10GB of memory.) In the meantime you can always reach me with questions, suggestions, or comments on <a href='https://lichess.org/@/thijscom'>my lichess account</a>.<p></p>\n")
		ofile.write("\t\t</th>\n")
		ofile.write("\t</tr>\n")
		ofile.write("\t<tr>\n")
		ofile.write("\t\t<th class='rank'></th>\n")
		ofile.write("\t\t<th class='fidetitle'></th>\n")
		ofile.write("\t\t<th class='username'></th>\n")
		ofile.write("\t\t<th class='gold'></th>\n")
		ofile.write("\t\t<th class='silver'></th>\n")
		ofile.write("\t\t<th class='bronze'></th>\n")
		ofile.write("\t\t<th class='points'></th>\n")
		ofile.write("\t\t<th class='events'></th>\n")
		ofile.write("\t\t<th class='avg'></th>\n")
		ofile.write("\t\t<th class='max'></th>\n")
		ofile.write("\t</tr>\n")
		ofile.write("</table>\n")
		ofile.write("</body>\n")
		ofile.write("</html>\n")

print("ALL DONE!")