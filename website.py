import requests
import re
import os
import time
import collections
import os.path
import ndjson
import json

def strf(num, type):
	if num > 10000000000:
		return "<span class='info' title='" + str(num[:-9]) + "," + str(num[-9:-6]) + "," + str(num[-6:-3]) + "," + str(num[-3:]) + " " + type + "'>" + str(round(num / 1000000000)) + "B</span>"
	elif num > 1000000000: 
		return "<span class='info' title='" + str(num)[:-9] + "," + str(num)[-9:-6] + "," + str(num)[-6:-3] + "," + str(num)[-3:] + " " + type + "'>" + str(round(num / 100000000) / 10) + "B</span>"
	elif num > 10000000:
		return "<span class='info' title='" + str(num)[-9:-6] + "," + str(num)[-6:-3] + "," + str(num)[-3:] + " " + type + "'>" + str(round(num / 1000000)) + "M</span>"
	elif num > 1000000:
		return "<span class='info' title='" + str(num)[-9:-6] + "," + str(num)[-6:-3] + "," + str(num)[-3:] + " " + type + "'>" + str(round(num / 100000) / 10) + "M</span>"
	elif num > 10000:
		return "<span class='info' title='" + str(num)[-6:-3] + "," + str(num)[-3:] + " " + type + "'>" + str(round(num / 1000)) + "K</span>"
	elif num > 1000:
		return "<span class='info' title='" + str(num)[-6:-3] + "," + str(num)[-3:] + " " + type + "'>" + str(round(num / 100) / 10) + "K</span>"
	else:
		return str(num)

months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
def datestr(dstr):
	# dstr: "2020-02-27"
	return months[dstr[5:7]] + " " + dstr[8:10] + ", " + dstr[0:4]
	
def stattable(of, ri, func):
	of.write("\t\t</th>\n")
	of.write("\t</tr>\n")
	of.write("\t<tr>\n")
	of.write("\t\t<th colspan='10' style='width: 100%; padding: 0px;'>\n")
	of.write("\t\t<table class='stats' width='100%'>\n")
	of.write("\t\t\t<thead>\n")
	of.write("\t\t\t<tr>\n")
	of.write("\t\t\t\t<th class='stats'></th>\n")
	for index, mo in enumerate(moord):
		of.write("\t\t\t\t<th class='stats" + ("last" if index == 15 else "") + "'><span title='" + mode[mo] + "'>" + moordicon[mo] + "</span></th>\n")
	of.write("\t\t\t</tr>\n")
	of.write("\t\t\t</thead>\n")
	of.write("\t\t\t<tbody>\n")
	for index, ev in enumerate(event):
		of.write("\t\t\t<tr class='" + ("even" if (index % 2 == 1) else "odd") + "'>\n")
		of.write("\t\t\t\t<td class='statshead' width='90'>" + event[ev] + "</td>\n")
		for index, mo in enumerate(moord):
			of.write("\t\t\t\t<td class='stats" + ("last" if index == 15 else "") + "' width='" + ("50" if index == 15 else "50") + "' align='right'>" + str(func(ri, mo, ev)) + "</td>\n")
		of.write("\t\t\t</tr>\n")
	of.write("\t\t\t</tbody>\n")
	of.write("\t\t</table>\n")
	of.write("\t\t</th>\n")
	of.write("\t</tr>\n")
	of.write("\t<tr>\n")
	of.write("\t\t<th colspan='10' class='about'>\n")

event = {
	"all": "All",
	"hourly": "Hourly",
	"daily": "Daily",
	"weekly": "Weekly",
	"monthly": "Monthly",
	"yearly": "Yearly",
	"eastern": "Eastern",
	"elite": "Elite",
	"shield": "Shield",
	"titled": "Titled",
	"marathon": "Marathon",
	"2020": "2020",
	"2019": "2019",
	"2018": "2018",
	"2017": "2017",
	"2016": "2016",
	"2015": "2015",
	"2014": "2014",
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

# Ordered list of rankings 
evord = {
	"hourly": "Hourly",
	"daily": "Daily",
	"weekly": "Weekly",
	"monthly": "Monthly",
	"yearly": "Yearly",
	"eastern": "Eastern",
	"elite": "Elite",
	"shield": "Shield",
	"titled": "Titled",
	"marathon": "Marathon",
	"2020": "2020",
	"2019": "2019",
	"2018": "2018",
	"2017": "2017",
	"2016": "2016",
	"2015": "2015",
	"2014": "2014"
}

# Ordered list of variants/modes
moord = {
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

moordicon = {
	"all": "O",#"&#xe004;",
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

fpath = "E:\\lichess\\tournaments\\"
frpath = "E:\\lichess\\tournaments\\rankings\\"
fpathweb = "E:\\lichess\\tmmlaarhoven.github.io\\lichess\\rankings\\"

if not os.path.exists(fpathweb):
	os.makedirs(fpathweb)

#=========================================================================
# 1: Compact page of rankings per mode
#=========================================================================

# Display top 10 for each type
nplayers = 10	
for mo in mode:
	if not os.path.exists(fpathweb + mo + "\\"):
		print(mo + " - Creating directory " + fpathweb + mo + "\\")
		os.makedirs(fpathweb + mo + "\\")
	# with open(fpathweb + mo + "\\index.html", "w") as ofile:
		# ofile.write("<!DOCTYPE html>\n<html>\n")
		# ofile.write("<head>\n<title>" + mode[mo] + " Overview</title>\n<link rel='stylesheet' href='../../stylesheets/style.css'>\n</head>\n")
		# ofile.write("<body>\n<table>\n")

		# # Keep track of number of rankings, put four on each row
		# nevents = 0
		
		# # Compact ranking for each event type
		# for ev in event:
			
			# # If file not found, skip
			# if (not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json")) or (not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson")):
				# continue
			
			# # Load ranking info
			# with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as rf:
				# rankinfo = json.load(rf)

			# # Load top rankings in list
			# toplist = []
			# with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking_points.ndjson", "r") as rf:
				# for i in range(nplayers):
					# line = rf.readline()
					# dictio = json.loads(line.strip())
					# toplist.append(dictio)
			
			# # Stylize results in html
			# if nevents == 0:
				# ofile.write("\t<tr style='height: 200px'>\n")
			# ofile.write("\t\t<td valign='top' style='padding: 10px;'>\n")
			# ofile.write("\t\t<table style='width: 230px; border: 1px #000000 solid; border-spacing: 10px 2px; border-collapse: collapse; padding: 0px;'>\n")
			# ofile.write("\t\t\t<thead style='background: #EEEEEE;'>\n")
			# ofile.write("\t\t\t<tr>\n\t\t\t\t<th colspan='2' style='padding-top: 5px;'><b>" + event[ev] + " " + mode[mo] + " Arenas</b></th>\n\t\t\t</tr>\n")
			# ofile.write("\t\t\t<tr>\n\t\t\t\t<th colspan='2' style='padding-bottom: 5px'><div style='font-weight: normal; font-size: 11pt'>(" + rankinfo["firststart"][0:4] + (("&ndash;" + rankinfo["laststart"][0:4]) if not (rankinfo["firststart"][0:4] == rankinfo["laststart"][0:4]) else ("")) + ", " + str(rankinfo["events"]) + " events)</div></th>\n\t\t\t</tr>\n\t\t\t</thead>\n")
			# ofile.write("\t\t\t<tbody style='background: url(logo-g2c.png); background-size: 170px; background-position: center; background-repeat: no-repeat;'>\n")
			# for i in range(nplayers):
				# ofile.write("\t\t\t<tr>\n")
				# ofile.write("\t\t\t\t<td style='padding-left: 10px;'>" + toplist[i]["username"] + "</td>\n")
				# ofile.write("\t\t\t\t<td style='padding-right: 10px;' align='right'>" + str(toplist[i]["score"]) + "</td>\n")						
				# ofile.write("\t\t\t</tr>\n")
			# ofile.write("\t\t\t</tbody>\n")
			# ofile.write("\t\t\t<tfoot>\n\t\t\t<tr>\n\t\t\t\t<td style='padding-right: 10px; padding-left: 10px; text-align: center;' colspan='2'><a href='" + ev + "/index.html'>All " + str(rankinfo["players"]) + " players</a></td>\n\t\t\t</tr>\n\t\t\t</tfoot>\n")
			# ofile.write("\t\t</table>\n\t\t</td>\n")
			# nevents += 1
			# if nevents == 4:
				# ofile.write("\t</tr>\n")
				# nevents = 0
				
		# ofile.write("</table>\n</body>\n</html>\n")

#=========================================================================
# 2: Top rankings per mode and per event
#=========================================================================

# Display top 1000 for each type
nplayers = 1000
for mo in mode:
#for mo in []:
	for ev in event:		
		ord = {"_points": "index.html", "_trophies": "trophies.html", "_events": "events.html", "_average": "average.html", "_maximum": "maximum.html"}
		for order in ord:
		
			if not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json") or not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking" + order + ".ndjson"):
				continue
			
			print(mo + " - " + ev + " - Building " + ord[order] + "...")
			if not os.path.exists(fpathweb + mo + "\\" + ev + "\\"):
				print(mo + " - " + ev + " - Creating directory " + fpathweb + mo + "\\" + ev + "\\")
				os.makedirs(fpathweb + mo + "\\" + ev + "\\")

			# Load ranking info
			with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as rf:
				jinfo = json.load(rf)
			
			with open(fpathweb + mo + "\\" + ev + "\\" + ord[order], "w") as ofile:			
				ofile.write("<!DOCTYPE html>\n")
				ofile.write("<html lang='en-US'>\n")
				ofile.write("<!-- Rankings built using the Lichess API (https://lichess.org/api) and some manual (python-based) tournament scraping -->\n")
				ofile.write("<head>\n")
				if ev == "marathon":
					ofile.write("<title>Lichess Rankings &middot; " + mode[mo] + " Marathons</title>\n")
				elif mo == "all" or ev == "titled" or ev == "shield":
					if mo == "all" and ev == "all":
						ofile.write("<title>Lichess Rankings &middot; All Arenas</title>\n")
					else:
						ofile.write("<title>Lichess Rankings &middot; " + mode[mo] + " " + event[ev] + " Rankings</title>\n")
				else:
					ofile.write("<title>Lichess Rankings &middot; " + event[ev] + " " + mode[mo] + " Rankings</title>\n")
				ofile.write("<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>\n")
				ofile.write("<link rel='icon' type='image/png' href='../../../favicon.ico'>\n")
				ofile.write("<link rel='stylesheet' href='../../../style.css'>\n")
				ofile.write("</head>\n")
				ofile.write("<table class='content'>\n")
				ofile.write("\t<thead>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='mode'>\n")
				#ofile.write("\t\t\t<a class='" + ("active" if (ev == "all") else "back") + "' href='../all/" + ord[order] + "'>All</a>\n")
				ofile.write("\t\t\t<a class='mode' href='../../index.html'><span style='font-family: lichess' title='About'>&#xe005;</span></a>\n")
				for index, mod in enumerate(moord):
					if os.path.exists(frpath + mod + "\\" + ev + "\\" + mod + "_" + ev + "_ranking.json") and os.path.exists(frpath + mod + "\\" + ev + "\\" + mod + "_" + ev + "_ranking" + order + ".ndjson"):
						ofile.write("\t\t\t &middot; <a class='" + ("active" if (mo == mod) else "mode") + "' href='../../" + mod + "/" + ev + "/" + ord[order] + "'><span style='font-family: lichess' title='" + moord[mod] + "'>" + moordicon[mod] + "</span></a>\n")
					else:
						ofile.write("\t\t\t &middot; <a class='" + ("active" if (mo == mod) else "mode") + "' href='../../" + mod + "/all/" + ord[order] + "'><span style='font-family: lichess' title='" + moord[mod] + "'>" + moordicon[mod] + "</span></a>\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='type'>\n")
				ofile.write("\t\t<a class='" + ("active" if (ev == "all") else "type") + "' href='../all/" + ord[order] + "'>All</a>\n")
				for eve in evord:
					if os.path.exists(frpath + mo + "\\" + eve + "\\" + mo + "_" + eve + "_ranking.json") and os.path.exists(frpath + mo + "\\" + eve + "\\" + mo + "_" + eve + "_ranking" + order + ".ndjson"):
						ofile.write("\t\t &middot; <a class='" + ("active" if (ev == eve) else "type") + "' href='../" + eve + "/" + ord[order] + "'>" + evord[eve] + "</a>\n")
					else:
						ofile.write("\t\t &middot; " + evord[eve] + "\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='title'>\n")
				#ofile.write("\t\t<div class='lefticon'>" + moordicon[mo] + "</div>\n")
				if ev == "marathon":
					ofile.write("\t\t" + mode[mo] + " Marathons\n")
				elif mo == "all" or ev == "titled" or ev == "shield":
					if mo == "all" and ev == "all":
						ofile.write("\t\tAll Arenas\n")
					else:
						ofile.write("\t\t" + mode[mo] + " " + event[ev] + " Arenas\n")
				else:
					ofile.write("\t\t" + event[ev] + " " + mode[mo] + " Arenas\n")
				#ofile.write("\t\t<div class='righticon'>" + moordicon[mo] + "</div>\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='sort'>Show rankings sorted by: &nbsp;&nbsp;&nbsp;\n")
				ofile.write("\t\t<a class='" + ("active" if (order == "_trophies") else "sort") + "' href='trophies.html'>Trophies</a>\n")
				ofile.write("\t\t &middot; <a class='" + ("active" if (order == "_points") else "sort") + "' href='index.html'>Points</a>\n")
				ofile.write("\t\t &middot; <a class='" + ("active" if (order == "_events") else "sort") + "' href='events.html'>Events</a>\n")
				ofile.write("\t\t &middot; <a class='" + ("active" if (order == "_average") else "sort") + "' href='average.html'>Average</a>\n")
				ofile.write("\t\t &middot; <a class='" + ("active" if (order == "_maximum") else "sort") + "' href='maximum.html'>Maximum</a>\n")
				ofile.write("\t\t</th>\n")
				ofile.write("\t</tr>\n")
				ofile.write("\t<tr>\n")
				ofile.write("\t\t<th colspan='10' class='info'>\n")
				ofile.write("\t\tThe ranking below is based on a total of " + strf(jinfo["events"], "events") + " events played on <a href='https://lichess.org/'>lichess.org</a>, which in total featured " + strf(jinfo["games"], "games") + " games (with " + strf(jinfo["moves"], "moves") + " moves).\n")
				ofile.write("Overall, in these events white scored <span class='info' title='" + str(jinfo["wwins"]) + " out of " + str(jinfo["games"]) + " games'>" + str(round(100 * jinfo["wwins"] / jinfo["games"])) + "%</span> wins, <span class='info' title='" + str(jinfo["games"] - jinfo["wwins"] - jinfo["bwins"]) + " out of " + str(jinfo["games"]) + " games'>" + str(round(100 * (jinfo["games"] - jinfo["wwins"] - jinfo["bwins"]) / jinfo["games"])) + "%</span> draws, and <span class='info' title='" + str(jinfo["bwins"]) + " out of " + str(jinfo["games"]) + " games'>" + str(round(100 * jinfo["bwins"] / jinfo["games"])) + "%</span> losses.\n")
				ofile.write("The events in this ranking took place between <a title='First event' href='https://lichess.org/tournament/" + jinfo["firstid"] + "'>" + datestr(jinfo["firststart"][0:10]) + "</a> and <a title='Last event' href='https://lichess.org/tournament/" + jinfo["lastid"] + "'>" + datestr(jinfo["laststart"][0:10]) + "</a>.\n")
				ofile.write("\t\tIn total these events featured " + strf(jinfo["participants"], "participants") + " participants (" + strf(jinfo["players"], "players") + " unique players).\n")
				ofile.write("\t\tThe maximum number of participants in one event is <a title='Event with most players' href='https://lichess.org/tournament/" + jinfo["maxusersid"] + "'>" + str(jinfo["maxusers"]) + "</a>.\n")
				ofile.write("\t\tThe highest score achieved in one event is <a title='Event with highest score' href='https://lichess.org/tournament/" + jinfo["topid"] + "'>" + str(jinfo["topscore"]) + "</a> by <a href='https://lichess.org/@/" + jinfo["topuser"] + "'>" + jinfo["topuser"] + "</a>.\n")
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
				
				with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking" + order + ".ndjson", "r") as rf:
					for line in rf:
					
						# Process the player ranking
						dictio = json.loads(line.strip())
						
						if dictio["ranking"] % 2 == 0:
							ofile.write("\t<tr class='even'>\n")
						else:
							ofile.write("\t<tr class='odd'>\n")
						ofile.write("\t\t<td class='rank'>" + str(dictio["ranking"]) + ".</td>\n")
						ofile.write("\t\t<td class='fidetitle'>" + dictio.get("title", " ") + "&nbsp;</td>\n")
						ofile.write("\t\t<td class='username'><a href='https://lichess.org/@/" + dictio["username"] + "'>" + dictio["username"] + "</a></td>\n")
						ofile.write("\t\t<td class='gold'>" + str(dictio.get("#1", " ")) + "</td>\n")
						ofile.write("\t\t<td class='silver'>" + str(dictio.get("#2", " ")) + "</td>\n")
						ofile.write("\t\t<td class='bronze'>" + str(dictio.get("#3", " ")) + "</td>\n")
						ofile.write("\t\t<td class='points'>" + str(dictio["score"]) + "</td>\n")
						ofile.write("\t\t<td class='events'>&nbsp;/ " + str(dictio["events"] - dictio.get("0s", 0)) + "</td>\n")
						ofile.write("\t\t<td class='avg'>" + str(round(dictio["score"] / max(1, dictio["events"] - dictio.get("0s", 0)))) + "</td>\n")
						ofile.write("\t\t<td class='max'><a href='https://lichess.org/tournament/" + dictio["maxid"] + "'>" + str(dictio["maxscore"]) + "</a></td>\n")
						ofile.write("\t</tr>\n")
						
						if dictio["ranking"] == nplayers:
							break
				
				ofile.write("\t</tbody>\n")
				#ofile.write("\t<tfoot>\n")
				#ofile.write("\t<tr>\n")
				#ofile.write("\t\t<td colspan='10'><a href='hmm.html'>Download full CSV file</a></td>\n")
				#ofile.write("\t</tr>\n")
				#ofile.write("\t</tfoot>\n")
				ofile.write("</table>\n")
				ofile.write("</body>\n")
				ofile.write("</html>\n")

rankinfo = dict()
for mo in mode:
	rankinfo[mo] = dict()
	for ev in event:	
		rankinfo[mo][ev] = dict()
		if not os.path.exists(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json"):
			continue
		with open(frpath + mo + "\\" + ev + "\\" + mo + "_" + ev + "_ranking.json", "r") as rf:
			rankinfo[mo][ev] = json.load(rf)

################################################################
# Index page with statistics
################################################################

others = {"Lichess Rankings": "index.html", "Statistics": "stats.html", "Titled Arenas": "titled.html", "Seasonal Marathons": "marathon.html", "Special Events": "special.html", "About": "about.html"}
for oth in others:
	print("Building " + others[oth] + "...")
	with open(fpathweb + others[oth], "w") as ofile:			
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
		ofile.write("\t\t<th colspan='10' class='mode'>\n")
		#ofile.write("\t\t\t<a class='" + ("active" if (ev == "all") else "back") + "' href='../all/" + ord[order] + "'>All</a>\n")
		ofile.write("\t\t\t<a class='active' href='index.html'><span style='font-family: lichess' title='About'>&#xe005;</span></a>\n")
		for mod in moord:
			ofile.write("\t\t\t &middot; <a class='mode' href='" + mod + "/all/index.html'><span style='font-family: lichess' title='" + moord[mod] + "'>" + moordicon[mod] + "</span></a>\n")
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
		ofile.write("\t\t" + oth + "\n")
		#ofile.write("\t\t<div class='righticon'>&#xe005;</div>\n")
		ofile.write("\t\t</th>\n")
		ofile.write("\t</tr>\n")
		# ofile.write("\t<tr>\n")
		# ofile.write("\t\t<th colspan='10' class='sort'>Most recent tournament: <a title='Most recent event' href='https://lichess.org/tournament/" + rankinfo["all"]["all"]["lastid"] + "'>" + datestr(rankinfo["all"]["all"]["laststart"][0:10]) + "</a>\n")
		# ofile.write("\t\t</th>\n")
		# ofile.write("\t</tr>\n")
		ofile.write("\t<tr>\n")
		ofile.write("\t\t<th colspan='10' class='about'>\n")
		###############################################################################
		if oth == "Lichess Rankings":
			ofile.write("\t\t<span style='padding-top: 0px; font-style: italic; color: #888888;'>Most recent tournament: <a title='Most recent event' href='https://lichess.org/tournament/" + rankinfo["all"]["all"]["lastid"] + "'>" + datestr(rankinfo["all"]["all"]["laststart"][0:10]) + "</a>. To navigate the rankings, use the icons above. The icon <span style='font-family: lichess;'>" + moordicon["all"] + "</span> refers to global rankings for all categories combined. The duplicate icons for bullet and blitz are used to distinguish between (hyper)bullet and (super)blitz arenas.</span>\n")
			#ofile.write("\t\t<h1 class='about'>About</h1>\n")
			ofile.write("\t\t<p>The rankings on this webpage are based on all regularly-scheduled arenas played on <a href='https://lichess.org/'>lichess.org</a> (hourly, daily, weekly, monthly, yearly, eastern, elite, and shield arenas) as well as the <a href='all/marathon/index.html'>seasonal 24h marathons</a> and the <a href='all/titled/trophies.html'>titled arenas</a>. These rankings exclude irregular rating-restricted events (<1700 Bullet Arena, ...), themed arenas (King's Gambit Blitz Arena, ...), and arenas created by Lichess users. In total the rankings cover " + strf(rankinfo["all"]["all"]["events"], "events") + " events, which had a total of " + strf(rankinfo["all"]["all"]["players"], "players") + " unique players participating in the events.</p>") 
			ofile.write("<p>Additional, detailed statistics can be found on the <a href='stats.html'>statistics</a> page.</p>")
		###############################################################################
		elif oth == "Statistics":
			ofile.write("\t\tWith all the data about these tournaments available, we can obtain various statistics that tell us more about the average user, the popularity of different variants and time controls, and the growth of Lichess over time. Below we list some more detailed statistics.\n")
			ofile.write("\t\t<h2 class='head'>Partitioning the data</h2>\n")
			ofile.write("\t\tThe events in this ranking can be classified into 15 different time controls and/or variants, as listed below.\n")
			ofile.write("\t\t<ul style='list-style-type: none;'>\n")
			for mo in moord:
				if mo == "all":
					continue
				ofile.write("\t\t\t<li><span style='color: #BF811D;'><span style='font-family: lichess;'>" + moordicon[mo] + "</span> &nbsp;" + mode[mo] + ":</span> &nbsp; " + strf(rankinfo[mo]["all"]["events"], "events") + " events, " + strf(rankinfo[mo]["all"]["players"], "players") + " players, " + strf(rankinfo[mo]["all"]["moves"], "moves") + " moves, " + strf(rankinfo[mo]["all"]["games"], "games") + " games, " + strf(rankinfo[mo]["all"]["points"], "points") + " points.</li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<p>Partitioning the events included in the rankings by type, we unsurprisingly see that there were many more hourly arenas than yearly arenas. At the same time yearly arenas are more special (and generally last longer) and therefore get more participants per event than hourly arenas.</p>\n")
			ofile.write("\t\t<ul style='list-style-type:none;'>\n")
			for ev in event:
				if ev == "all" or ev[0] == "2":
					continue
				ofile.write("\t\t\t<li><span style='color: #BF811D;'>" + event[ev] + ":</span> &nbsp; " + strf(rankinfo["all"][ev]["events"], "events") + " events, " + strf(rankinfo["all"][ev]["players"], "players") + " players, " + strf(rankinfo["all"][ev]["moves"], "moves") + " moves, " + strf(rankinfo["all"][ev]["games"], "games") + " games, scoring " + strf(rankinfo["all"][ev]["points"], "points") + " points.</li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<p>When partitioning the events according to the year they were played in, we obtain the following overview. The first regular events included in these rankings took place in 2014. As Lichess has grown over the years, one can see that the number of players as well as the number of events has grown rapidly over time. (Part of the growth in 2020 might be attributed to the spread of COVID-19, with people around the world being forced to spend more time indoor and online, thus resulting in more people playing online than usual.)</p>\n")
			ofile.write("\t\t<ul style='list-style-type:none;'>\n")
			for ev in event:
				if not ev[0] == "2":
					continue
				ofile.write("\t\t\t<li><span style='color: #BF811D;'>" + event[ev] + ":</span> &nbsp; " + strf(rankinfo["all"][ev]["events"], "events") + " events, where " + strf(rankinfo["all"][ev]["players"], "players") + " players made " + strf(rankinfo["all"][ev]["moves"], "moves") + " moves in " + strf(rankinfo["all"][ev]["games"], "games") + " games.</li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<p>For an even more detailed breakdown of all events in these rankings in terms of types and variants, see the following table. Percentages in this table are rounded to the nearest integer; 1% means \"between 0.5% and 1.5%\" and 0% means \"less than 0.5%\", while a dash in all tables below means that no events in this combination of categories took place. Almost 30% of all events are bullet arenas, and as they take place (almost) every hour, almost 90% of the events included in these rankings are hourly arenas.</p>\n")
			ofile.write("\t\t<h2 class='stats'>Classification of all events</h2>\n")
			fpctevents = lambda r, m, e: (str(round(100 * r[m][e].get("events", 0) / r["all"]["all"].get("events", 1))) + "%") if "events" in r[m][e] else "-"
			stattable(ofile, rankinfo, fpctevents)
			#ofile.write("\t\t<h2 class='stats'>Classification of all points</h2>\n")
			#fpctevents = lambda r, m, e: (str(round(100 * r[m][e].get("games", 0) / r["all"]["all"].get("games", 1))) + "%") if "events" in r[m][e] else "-"
			#stattable(ofile, rankinfo, fpctevents)
			#ofile.write("\t\t<h2 class='stats'>Percentages  all points</h2>\n")
			#fpctevents = lambda r, m, e: (str(round(100 * r[m][e].get("points", 0) / r["all"]["all"].get("points", 1))) + "%") if "events" in r[m][e] else "-"
			#stattable(ofile, rankinfo, fpctevents)
			
			ofile.write("\t\t<h2 class='head'>Event statistics</h2>\n")
			ofile.write("\t\t<p>The tables below summarize various statistics per game type and per event type of arena tournaments. We briefly discuss some things one may conclude from these tables below.</p>\n")
			ofile.write("\t\t<ul>\n")
			ofile.write("\t\t\t<li><span class='title'>Average participants per event:</span> Overall, the average number of participants per event is <span class='dgreen'>165 players</span>. The yearly average grew from 32 in 2014 to 281 in 2020. Overall, rapid events see the most participants on average, and whereas all standard time controls have an average participation of >100 (and >90 for chess 960), all non-standard chess variants have an average of only <60 players per event.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average ratings per event:</span> While average ratings across Lichess may be around 1500, tournaments seem to have a bias towards higher-rated players. As lower-rated players have no chance of winning these events, they may prefer matchmaking over random arena pairings where they lose most of their games. Overall, the average rating in events is around <span class='dgreen'>1750</span>, with slightly higher averages in faster time controls and in crazyhouse. As for types of events with higher averages, we naturally see peaks for titled arenas and elite arenas, which are only open to high-rated players.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average points per player per event:</span> Overall, an average arena participant scored around <span class='dgreen'>8 points</span>. With many players joining for only a few games, and some players playing the entire events and scoring many points, the median might be significantly lower. The average number of points is highest for quick time controls, where it is easier to play many games in a short amount of time.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Maximum points achieved in one event:</span> Looking only at the highest scores ever achieved in arenas, we see that the highest score ever achieved was by <span class='title'>GM</span> <a href='https://lichess.org/@/penguingim1'>penguingim1</a> in one of the bullet marathons, scoring <span class='dgreen'>1645</span> points. (As explained on the page with <a href='special.html'>special events</a> this is not the maximum score ever achieved, as six players have scored over 2000 points in 24-hour hyperbullet events.)</li>\n")
			ofile.write("\t\t</ul>\n")
			#ofile.write("\t\t<p>Average participants per event:</p>\n")
			ofile.write("\t\t<h2 class='stats'>Average participants per event</h2>\n")
			favgplayers = lambda r, m, e: ("<span style='font-size: 9pt;'>" + str(round(r[m][e].get("participants", 0) / r[m][e].get("events", 1))) + "</span>") if "participants" in r[m][e] else "-"
			stattable(ofile, rankinfo, favgplayers)
			ofile.write("\t\t<h2 class='stats'>Average ratings per event</h2>\n")
			favgrating = lambda r, m, e: ("<span style='font-size: 9pt;'>" + str(round(r[m][e].get("totrating", 0) / r[m][e].get("participants", 1))) + "</span>") if "totrating" in r[m][e] else "-"
			stattable(ofile, rankinfo, favgrating)
			ofile.write("\t\t<h2 class='stats'>Average points per player per event</h2>\n")
			favgpoints = lambda r, m, e: (str(round(r[m][e].get("points", 0) / r[m][e].get("participants", 1)))) if "points" in r[m][e] else "-"
			stattable(ofile, rankinfo, favgpoints)
			ofile.write("\t\t<h2 class='stats'>Maximum points achieved in one event</h2>\n")
			fmax = lambda r, m, e: ("<a title='" + r[m][e].get("topuser", "") + "' href='https://lichess.org/tournament/" + r[m][e].get("topid") + "'>" + str(r[m][e].get("topscore")) + "</a>") if ("topscore" in r[m][e]) else "-"
			stattable(ofile, rankinfo, fmax)
			
			ofile.write("\t\t<h2 class='head'>Game statistics</h2>\n")
			ofile.write("\t\t<p>Finally, below are some tables listing game statistics per game type and per event type. We again briefly highlight some things one might observe in these tables.</p>\n")
			ofile.write("\t\t<ul>\n")
			ofile.write("\t\t\t<li><span class='title'>Average moves per player per game:</span> On average, games played in all these events lasted around <span class='dgreen'>33 moves</span>. In terms of variants, both extremely short (ultrabullet) and long time controls (classical) have a slightly lower average than \"medium\" time controls such as superblitz or blitz. Of the variants, racing kings (14), atomic (16), and three-check (18) have the lowest average moves per game due to the nature of these variants, while in horde (46) the average is significantly higher than for standard chess games. With the higher average rating and with more at stake, titled arenas (and elite arenas) have a higher average number of moves per game as well.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average score of white players:</span> While white may have a slight edge in chess in general, a (large) difference in playing strength will easily offset this small advantage. Overall, in all arenas combined, white players have scored approximately <span class='dgreen'>51%</span>. White still scores slightly more than 50% in (almost) all events, except in horde, where the black player seems to have a slight edge over white. We further notice a slightly larger win percentage for white in atomic, three-check, and crazyhouse, and due to the higher level of play and the narrower range of playing strengths in these events, in both elite arenas and titled arenas white players score slightly better with a 52% score.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average percentage of draws:</span> As most tournaments are open to a wide range of ratings, and as shorter games played online are more often decisive, it is no surprise that the overall percentage of draws is only around <span class='dgreen'>3%</span>. This percentage is even lower at faster time controls and some variants like crazyhouse and three-check, while racing kings has a remarkably high draw percentage of around 10%.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Average percentage of berserked games:</span> On average, players choose the berserk option in around <span class='dgreen'>11%</span> of their arena games. This percentage is slightly higher (20% or more) for slow time controls, since losing half the clock time still leaves plenty of time to play a serious game. In non-standard chess variants, berserking seems especially popular in atomic and racing kings events, a statistic which may be closely related to the lower average game lengths in these variants; if games are often decided in fewer moves, losing time on the clock is not as important as for long games played in e.g. horde arenas.</li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<h2 class='stats'>Average moves per player per game</h2>\n")
			favgmoves = lambda r, m, e: (strf(round(r[m][e].get("moves", 0) / r[m][e].get("games", 1) / 2), "moves")) if "moves" in r[m][e] else "-"
			stattable(ofile, rankinfo, favgmoves)
			ofile.write("\t\t<h2 class='stats'>Average score of white players</h2>\n")
			favgwhite = lambda r, m, e: (str(round(100 * r[m][e].get("wwins", 0) / r[m][e].get("games", 1) + 100 * (r[m][e].get("games", 0) - r[m][e].get("wwins", 0) - r[m][e].get("bwins", 0)) / r[m][e].get("games", 1) / 2)) + "%") if "participants" in r[m][e] else "-"
			stattable(ofile, rankinfo, favgwhite)
			ofile.write("\t\t<h2 class='stats'>Average percentage of draws</h2>\n")
			favgdraws = lambda r, m, e: (str(round(100 * (r[m][e].get("games", 0) - r[m][e].get("wwins", 0) - r[m][e].get("bwins", 0)) / r[m][e].get("games", 1))) + "%") if "participants" in r[m][e] else "-"
			stattable(ofile, rankinfo, favgdraws)
			ofile.write("\t\t<h2 class='stats'>Average percentage of berserked games</h2>\n")
			fberserk = lambda r, m, e: (str(round(100 * r[m][e].get("berserks", 0) / r[m][e].get("games", 1) / 2)) + "%") if "berserks" in r[m][e] else "-"
			stattable(ofile, rankinfo, fberserk)
			
		###############################################################################
		elif oth == "Titled Arenas":	

			with open(frpath + "all\\titled\\all_titled_ranking.json", "r") as rf:
				rinfo = json.load(rf)
				
			ofile.write("\t\tEver since the end of 2017, Lichess has been regularly hosting \"Titled Arenas\", open only to titled players and with a total prize fund of at least $1000 each. The <a href='https://lichess.org/tournament/GToVqkC9'>first marathon</a> was won by world champion Magnus Carlsen, and he has regularly participated in (and won) titled arenas since then under different aliases. Recently Alireza Firouzja has won many titled arenas as well, and is approaching Magnus' record number of titled arena victories. In total there have now been " + str(rinfo["events"]) + " titled arenas, with " + str(rinfo["players"]) + " unique players taking part in one or more of these events.\n")
			ofile.write("\t\t<p>The titled arenas are included in the rankings (see the overall rankings <a href='all/titled/trophies.html'>here</a>), and for completeness all events are listed below in chronological order, with the most recent events first.</p>\n")
			ofile.write("\t\t<table>")

			# Keep track of number of rankings, put four on each row
			nevents = 0
		
			# Load ranking info
			tdata = {}
			with open(frpath + "all\\titled\\all_titled_events.ndjson", "r") as rf:
				for line in rf:
					dictio = json.loads(line)
					tdata[dictio["id"]] = dictio
					tdata[dictio["id"]]["top10"] = []
					with open(fpath + "titled\\" + dictio["mode"] + "\\titled_" + dictio["mode"] + "_" + dictio["id"] + ".ndjson", "r") as ran:
						for index, line in enumerate(ran):
							player = json.loads(line)
							dicti = {"username": player["username"], "score": player["score"]}
							if "title" in player:
								dicti["title"] = player["title"]
							tdata[dictio["id"]]["top10"].append(dicti)
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
				ofile.write("\t\t\t\t\t\t<th class='minitable' colspan='3'><span style='color: #888888; font-size: 10pt;'>" + datestr(tdata[id]["start"][0:10]) + "</span><br/><span style='font-family: lichess; font-size: 10pt;'>C</span> Titled Arena " + str(tdata[id]["number"]) + "</th>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</thead>")
				ofile.write("\t\t\t\t\t<tbody>\n")
				for i in range(10):
					ofile.write("\t\t\t\t\t<tr class='" + ("even" if (i % 2 == 0) else "odd") + "'>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitabletitle'>" + (("<span style='color: #BF811D;'>" + tdata[id]["top10"][i].get("title", "") + "</span> ") if "title" in tdata[id]["top10"][i] else "") + "</td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablename'><a href='https://lichess.org/@/" + tdata[id]["top10"][i]["username"] + "'>" + tdata[id]["top10"][i]["username"] + "</a></td>\n")
					ofile.write("\t\t\t\t\t\t<td style='padding-right: 10px;' align='right'>" + str(tdata[id]["top10"][i]["score"]) + "</td>\n")						
					ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<td colspan='3' class='minitablefoot'>" + str(tdata[id]["players"]) + " players &middot; <a href='https://lichess.org/tournament/" + id + "'>More info</a></td>\n")
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
			with open(frpath + "all\\marathon\\all_marathon_events.ndjson", "r") as rf:
				for line in rf:
					dictio = json.loads(line)
					tdata[dictio["id"]] = dictio
					tdata[dictio["id"]]["top10"] = []
					with open(fpath + "marathon\\" + dictio["mode"] + "\\marathon_" + dictio["mode"] + "_" + dictio["id"] + ".ndjson", "r") as ran:
						for index, line in enumerate(ran):
							player = json.loads(line)
							dicti = {"username": player["username"], "score": player["score"]}
							if "title" in player:
								dicti["title"] = player["title"]
							tdata[dictio["id"]]["top10"].append(dicti)
							if index == 9:
								break
								
			with open(frpath + "all\\marathon\\all_marathon_ranking.json", "r") as rf:
				rinfo = json.load(rf)
		
			ofile.write("\t\tFour times a year, Lichess hosts a 24h marathon event with varying time controls, with the top players obtaining a unique trophy displayed on their user profile. These events have taken place since the summer of 2015, and numerous events have been won by Lichess veteran <span class='title'>LM</span> <a href='https://lichess.org/@/Lance5500'>Lance5500</a>. In total there have now been " + str(rinfo["events"]) + " seasonal marathons, with " + strf(rinfo["players"], "players") + " unique players taking part in one or more of these events.\n")
			ofile.write("\t\t<p>The marathons are included in the rankings (see the overall rankings <a href='all/marathon/index.html'>here</a>), and for completeness all events are listed below in chronological order, with the most recent events first.</p>\n")
			ofile.write("\t\t<table>")

			# Keep track of number of rankings, put four on each row
			nevents = 0

			# Compact ranking for each event type
			for id in reversed(list(tdata.keys())):
				
				# Stylize results in html
				if nevents == 0:
					ofile.write("\t\t\t<tr style='height: 200px'>\n")
				ofile.write("\t\t\t\t<td valign='top' style='padding: 10px;'>\n")
				ofile.write("\t\t\t\t<table class='minitable'>\n")
				ofile.write("\t\t\t\t\t<thead>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<th class='minitable' colspan='3'><span style='color: #888888; font-size: 10pt;'>" + datestr(tdata[id]["start"][0:10]) + "</span><br/><span style='font-family: lichess; font-size: 10pt;'>\</span> " + id[0:1].upper() + id[1:6] + " 20" + tdata[id]["start"][2:4] + "</th>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</thead>")
				ofile.write("\t\t\t\t\t<tbody>\n")
				for i in range(10):
					ofile.write("\t\t\t\t\t<tr class='" + ("even" if (i % 2 == 0) else "odd") + "'>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitabletitle'>" + (("<span style='color: #BF811D;'>" + tdata[id]["top10"][i].get("title", "") + "</span> ") if "title" in tdata[id]["top10"][i] else "") + "</td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablename'><a href='https://lichess.org/@/" + tdata[id]["top10"][i]["username"] + "'>" + tdata[id]["top10"][i]["username"] + "</a></td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablescore'>" + str(tdata[id]["top10"][i]["score"]) + "</td>\n")						
					ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<td colspan='3' class='minitablefoot'>" + str(tdata[id]["players"]) + " players &middot; <a href='https://lichess.org/tournament/" + id + "'>More info</a></td>\n")
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
		elif oth == "Special Events":	
			ofile.write("\t\tBesides user-generated arenas and rating-restricted events, various other special (official) arenas are not included in the rankings. These include warm-up arenas before titled arenas, one-time celebratory events, charity fundraisers, and privately-funded events with prize money. Special thanks go out to BitChess, sponsoring various events from 2016-2017, and <a href='https://lichess.org/@/FischyVischy'>FischyVischy</a>, sponsoring prize funds for Revolutions, Apocalypses, and numerous other variant events and championships over the years.\n")
			ofile.write("\t\t<p>We further highlight a few (series of) tournaments below:</p>\n")
			ofile.write("\t\t<ul>\n")
			ofile.write("\t\t\t<li><span class='title'>Highest scores:</span> A few 24h HyperBullet events have taken place on lichess, and naturally due to the low time control and long duration these have led to some of the highest scores ever recorded in a single arena. Users who scored more than <span class='dgreen'>2000 points</span> in one event include:\n")
			ofile.write("\t\t\t<ul>\n")
			ofile.write("\t\t\t\t<li><span class='title'>GM</span> <a href='https://lichess.org/@/penguingim1'>penguingim1</a> (<span class='dgreen'>2145</span>) and <span class='title'>GM</span> <a href='https://lichess.org/@/Tayka'>Tayka</a> (<span class='dgreen'>2023</span>) in the <a href='https://lichess.org/tournament/JBFIv9sW'>BitChess 24h Hyperbullet</a> arena;\n")
			ofile.write("\t\t\t\t<li><a href='https://lichess.org/@/Mr_Crabs'>Mr_Crabs</a> (<span class='dgreen'>2209</span>) and <span class='title'>IM</span> <a href='https://lichess.org/@/taheryoseph'>taheryoseph</a> (<span class='dgreen'>2042</span>) in the <a href='https://lichess.org/tournament/mfNJAKiv'>GM Andrew Tang Hyper Celebration</a> event;")
			ofile.write("\t\t\t\t<li><span class='title'>IM</span> <a href='https://lichess.org/@/toivok3'>toivok3</a> (<span class='dgreen'>2311</span>) and <span class='title'>IM</span> <a href='https://lichess.org/@/kiketf'>kiketf</a> (<span class='dgreen'>2122</span>) in the <a href='https://lichess.org/tournament/iS9Qmstg'>Opperwezen Roundabout</a>.\n")
			ofile.write("\t\t\t</ul>For variants such as Racing Kings and King of the Hill, the series of 24h \"Revolution\" events listed below contain some of the highest scores for these variants as well.</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Anniversaries:</span> Lichess hosted celebratory anniversary events in <a href='https://lichess.org/tournament/21ZMAsPg'>2020</a>, <a href='https://lichess.org/tournament/wEKI0Mrr'>2019</a>, and <a href='https://lichess.org/tournament/zqcpQFzR'>2018</a>. YouTube celebrity <a href='https://lichess.org/@/agadmator'>agadmator</a> hosted prize events when reaching YouTube milestones of <a href='https://lichess.org/tournament/Dd1kyEhY'>500k</a>, <a href='https://lichess.org/tournament/iRIDczTE'>400k</a>, <a href='https://lichess.org/tournament/7ctguzuH'>200k</a>, and <a href='https://lichess.org/tournament/sHsu5Yv2'>100k</a> YouTube subscribers.</li>\n")
			#ofile.write("\t\t\t<li><span class='title'>Streamer Battles:</span> ...</li>\n")
			ofile.write("\t\t\t<li><span class='title'>Charity events:</span> Some charity events hosted on Lichess include a tournament for the <a href='https://lichess.org/tournament/C696te7d'>Black Lives Matter</a> movement, the COVID-19 fundraisers <a href='https://lichess.org/tournament/0t0GLWau'>Offerspill Relief</a> and <a href='https://lichess.org/tournament/nn4UF6mP'>Marathon pour Mercy</a>, and the <a href='https://lichess.org/tournament/JBH25ivF'>Solidarity With Beirut</a> arena for the victims in Beirut.</li>\n")
			#ofile.write("\t\t\t<li><b><span class='title'></span><b>: ...</b></li>\n")
			ofile.write("\t\t</ul>\n")
			ofile.write("\t\t<p>A complete overview of the top 10 in each of these arenas is listed below, chronologically starting at the most recent events.\n")
			ofile.write("\t\t<table>")

			# Keep track of number of rankings, put four on each row
			nevents = 0
		
			# Load ranking info
			titev = []
			with open(frpath + "all\\titled\\all_titled_events.ndjson", "r") as rft:
				for line in rft:
					dictioo = json.loads(line)
					titev.append(dictioo["id"])
					
			tdata = {}
			with open(fpath + "special\\special.ndjson", "r") as rf:
				for line in rf:
					dictio = json.loads(line)
					if dictio["id"] in titev:
						continue
					tdata[dictio["id"]] = dictio					
					tdata[dictio["id"]]["top10"] = []
					with open(fpath + "special\\special_" + dictio["id"] + ".ndjson", "r") as ran:
						for index, line in enumerate(ran):
							player = json.loads(line)
							dicti = {"username": player["username"], "score": player["score"]}
							if "title" in player:
								dicti["title"] = player["title"]
							tdata[dictio["id"]]["top10"].append(dicti)
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
				ofile.write("\t\t\t\t\t\t<th class='minitable' colspan='3'><span style='color: #888888; font-size: 10pt;'>" + datestr(tdata[id]["start"][0:10]) + "</span><br/><span style='font-size: 9pt;'>" + tdata[id]["name"] + "</span></th>\n")
				ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t</thead>")
				ofile.write("\t\t\t\t\t<tbody>\n")
				for i in range(10):
					ofile.write("\t\t\t\t\t<tr class='" + ("even" if (i % 2 == 0) else "odd") + "'>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitabletitle'>" + (("<span style='color: #BF811D;'>" + tdata[id]["top10"][i].get("title", "") + "</span> ") if "title" in tdata[id]["top10"][i] else "") + "</td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablename'><a href='https://lichess.org/@/" + tdata[id]["top10"][i]["username"] + "'>" + tdata[id]["top10"][i]["username"] + "</a></td>\n")
					ofile.write("\t\t\t\t\t\t<td class='minitablescore'>" + str(tdata[id]["top10"][i]["score"]) + "</td>\n")						
					ofile.write("\t\t\t\t\t</tr>\n")
				ofile.write("\t\t\t\t\t<tr>\n")
				ofile.write("\t\t\t\t\t\t<td colspan='3' class='minitablefoot'>" + str(tdata[id]["players"]) + " players &middot; <a href='https://lichess.org/tournament/" + id + "'>More info</a></td>\n")
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