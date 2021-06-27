import requests
import re
import os
import time
import os.path
import ndjson
import json
import math
import datetime
import numpy as np
import matplotlib.pyplot as mpl
import random
from collections import OrderedDict
from typing import List, Union
from matplotlib.ticker import PercentFormatter
from itertools import product

#######################################################################################################################################################################################
#######################################################################################################################################################################################
#######################################################################################################################################################################################

PureVariants = {
	"3check": 		{"Name": "Three-check", 		"RGB": (204,121,167), 	"WebOrder": 11,		"Code": "3c",	"Icon": "."},
	"antichess": 	{"Name": "Antichess",			"RGB": (223, 83, 83),	"WebOrder": 12,		"Code": "an",	"Icon": "@"},
	"atomic": 		{"Name": "Atomic",				"RGB": (102, 85,140),	"WebOrder": 13,		"Code": "at",	"Icon": ">"},
	"blitz": 		{"Name": "Blitz",				"RGB": (  0,114,178),	"WebOrder": 5,		"Code": "bz",	"Icon": ")"},
	"bullet": 		{"Name": "Bullet",				"RGB": ( 86,180,233),	"WebOrder": 3,		"Code": "bu",	"Icon": "T"},
	"chess960": 	{"Name": "Chess960",			"RGB": (230,159,  0),	"WebOrder": 9,		"Code": "c9",	"Icon": "'"},
	"classical": 	{"Name": "Classical",			"RGB": ( 69,159, 59),	"WebOrder": 7,		"Code": "cl",	"Icon": "+"},
	"crazyhouse": 	{"Name": "Crazyhouse",			"RGB": ( 86,180,233),	"WebOrder": 8,		"Code": "ch",	"Icon": "&#xe00b;"},
	"horde": 		{"Name": "Horde",				"RGB": (153,230,153),	"WebOrder": 14,		"Code": "ho",	"Icon": "_"},
	"hyperbullet": 	{"Name": "HyperBullet",			"RGB": ( 86,180,233),	"WebOrder": 2,		"Code": "hb",	"Icon": "T"},
	"koth": 		{"Name": "King of the Hill",	"RGB": (213, 94,  0),	"WebOrder": 10,		"Code": "kh",	"Icon": "("},
	"racingkings": 	{"Name": "Racing Kings",		"RGB": (255,174,170),	"WebOrder": 15,		"Code": "rk",	"Icon": "&#xe00a;"},
	"rapid": 		{"Name": "Rapid",				"RGB": (  0,158,115),	"WebOrder": 6,		"Code": "ra",	"Icon": "#"},
	"superblitz": 	{"Name": "SuperBlitz",			"RGB": (  0,114,178),	"WebOrder": 4,		"Code": "sb",	"Icon": ")"},
	"ultrabullet": 	{"Name": "UltraBullet",			"RGB": (  0,158,115),	"WebOrder": 1,		"Code": "ub",	"Icon": "{"}
}
AllVariants = dict(PureVariants)
AllVariants["all"] = {"Name": "All",				"RGB": (200,200,200),	"WebOrder": 0,		"Code": "al",	"Icon": "O"}

PureEvents = {
	"hourly": 		{"Name": "Hourly",				"RGB": (  0,158,115),	"WebOrder": 1,		"Code": "ho"},
	"2000": 		{"Name": "<2000",				"RGB": (  0,158,115),	"WebOrder": 2,		"Code": "20"},
	"1700": 		{"Name": "<1700",				"RGB": (  0,158,115),	"WebOrder": 3,		"Code": "17"},
	"1600": 		{"Name": "<1600",				"RGB": (  0,158,115),	"WebOrder": 4,		"Code": "16"},
	"1500": 		{"Name": "<1500",				"RGB": (  0,158,115),	"WebOrder": 5,		"Code": "15"},
	"1300": 		{"Name": "<1300",				"RGB": (  0,158,115),	"WebOrder": 6,		"Code": "13"},
	"daily": 		{"Name": "Daily",				"RGB": (  0,158,115),	"WebOrder": 7,		"Code": "da"},
	"weekly": 		{"Name": "Weekly",				"RGB": (  0,158,115),	"WebOrder": 8,		"Code": "we"},
	"monthly": 		{"Name": "Monthly",				"RGB": (  0,158,115),	"WebOrder": 9,		"Code": "mo"},
	"yearly": 		{"Name": "Yearly",				"RGB": (  0,158,115),	"WebOrder": 10,		"Code": "ye"},
	"eastern": 		{"Name": "Eastern",				"RGB": (  0,158,115),	"WebOrder": 11,		"Code": "ea"},
	"elite": 		{"Name": "Elite",				"RGB": (  0,158,115),	"WebOrder": 12,		"Code": "el"},
	"shield": 		{"Name": "Shield",				"RGB": (  0,158,115),	"WebOrder": 13,		"Code": "sh"},
	"titled": 		{"Name": "Titled",				"RGB": (  0,158,115),	"WebOrder": 14,		"Code": "ti"},
	"marathon": 	{"Name": "Marathon",			"RGB": (  0,158,115),	"WebOrder": 15,		"Code": "ma"},
	"liga": 		{"Name": "Liga",				"RGB": (  0,158,115),	"WebOrder": 16,		"Code": "li"}
}
AllEvents = dict(PureEvents)
AllEvents["all"] = 	{"Name": "All",					"RGB": (200,200,200),	"WebOrder": 0,		"Code": "al"}

#######################################################################################################################################################################################
#######################################################################################################################################################################################
#######################################################################################################################################################################################

# https://www.materialui.co/colors - the "100", "200", "500", "800" (16 each), and "A100", "A200", "A400" (19 each) color sets, from left to right
Colors100 =		[(255,205,210), (248,187,208), (225,190,231), (209,196,233), (197,202,233), (187,222,251), (179,229,252), (178,235,242), (178,223,219), (200,230,201), 
				 (220,237,200), (240,244,195), (255,249,196), (255,236,179), (255,224,178), (255,204,188), (215,204,200), (245,245,245), (207,216,220)]
Colors200 =		[(239,154,154), (244,143,177), (206,147,216), (179,157,219), (159,168,218), (144,202,249), (129,212,250), (128,222,234), (128,203,196), (165,214,167), 
				 (197,225,165), (230,238,156), (255,245,157), (255,224,130), (255,204,128), (255,171,145), (188,170,164), (238,238,238), (176,190,197)]
Colors500 = 	[(244, 67, 54), (233, 30, 99), (156, 39,176), (103, 58,183), ( 63, 81,181), ( 33,150,243), (  3,169,244), (  0,188,212), (  0,150,136), ( 76,175, 80), 
				 (139,195, 74), (205,220, 57), (255,235, 59), (255,193,  7), (255,152,  0), (255, 87, 34), (121, 85, 72), (158,158,158), ( 96,125,139)]
Colors800 =		[(198, 40, 40), (173, 20, 87), (106, 27,154), ( 69, 39,160), ( 40, 53,147), ( 21,101,192), (  2,119,189), (  0,131,143), (  0,105, 92), ( 46,125, 50), 
				 ( 85,139, 47), (158,157, 36), (249,168, 37), (255,143,  0), (239,108,  0), (216, 67, 21), ( 78, 52, 46), ( 66, 66, 66), ( 55, 71, 79)]
ColorsA100 =	[(255,138,128), (255,128,171), (234,128,252), (179,136,255), (140,158,255), (130,177,255), (128,216,255), (132,255,255), (167,255,235), (185,246,202), 
				 (204,255,144), (244,255,129), (255,255,141), (255,229,127), (255,209,128), (255,158,128)]
ColorsA200 =	[(255, 82, 82), (255, 64,129), (224, 64,251), (124, 77,255), ( 83,109,254), ( 68,138,255), ( 64,196,255), ( 24,255,255), (100,255,218), (105,240,174), 
				 (178,255, 89), (238,255, 65), (255,255,  0), (255,215, 64), (255,171, 64), (255,110, 64)]		
ColorsA400 =	[(255, 23, 68), (245,  0, 87), (213,  0,249), (101, 31,255), ( 61, 90,254), ( 41,121,255), (  0,176,255), (  0,229,255), ( 29,233,182), (  0,230,118), 
				 (118,255,  3), (198,255,  0), (255,234,  0), (255,196,  0), (255,145,  0), (255, 61,  0)]

# Variants: Use A100 series, skip 12th entry
for V in PureVariants:
	if PureVariants[V]["WebOrder"] < 12:
		PureVariants[V]["RGB"] = ColorsA100[PureVariants[V]["WebOrder"] - 1]
	else:
		PureVariants[V]["RGB"] = ColorsA100[PureVariants[V]["WebOrder"]]

# Events: Use 100 series, skip 12th entry
for E in PureEvents:
	PureEvents[E]["RGB"] = Colors100[PureEvents[E]["WebOrder"] - 1]


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
		
		
# Temporary function to fix points, which was corrupted for some mixed categories (name changed from "Points" to "TotalPoints" at some point)
def FixPoints():
	for V in AllVariants:
		for E in AllEvents:
			if os.path.exists(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_ranking.json") and os.path.exists(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_arenas.ndjson"):
				print(f"Fixing {V} / {E}.")
				TotalPoints = 0
				with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_arenas.ndjson", "r") as ArenaFile:
					for Line in ArenaFile:
						ArenaData = json.loads(Line)
						TotalPoints = TotalPoints + ArenaData["TotalPoints"]
				with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_ranking.json", "r") as CatStatFile:
					CatStats = json.load(CatStatFile)
				print(f"New total for {V} / {E}: from {CatStats['TotalPoints']} to {TotalPoints}.")
				CatStats["TotalPoints"] = TotalPoints
				if "Points" in CatStats:
					del CatStats["Points"]
				with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_ranking.json", "w") as CatStatFile:
					CatStatFile.write(json.dumps(CatStats))


# Website: index page
def BuildIndexPage():
	
	# Pie charts
	SomePieChart(lambda RankingInfo: RankingInfo["Participants"], "participants", "Total participants in each arena category")
	SomePieChart(lambda RankingInfo: RankingInfo["Events"], "events", "Total events in each arena category")
	SomePieChart(lambda RankingInfo: RankingInfo["Games"], "games", "Total games played in each arena category")
	SomePieChart(lambda RankingInfo: RankingInfo["Moves"], "moves", "Total moves made in each arena category")
	SomePieChart(lambda RankingInfo: RankingInfo["TotalPoints"], "points", "Total points scored in each arena category")

	# Build box plots
	SomeBoxPlot(lambda ArenaData: ArenaData["Players"], "participants", "Participants per hourly arena")
	SomeBoxPlot(lambda ArenaData: ArenaData["TotalRating"] / ArenaData["Players"], "rating", "Average rating per hourly arena")
	SomeBoxPlot(lambda ArenaData: ArenaData["Moves"] / ArenaData["Games"] / 2., "moves", "Moves per player per game in hourly arenas")
	SomeBoxPlot(lambda ArenaData: ArenaData["TopScore"], "topscore", "Top scores in hourly arenas")
	SomeBoxPlot(lambda ArenaData: 100. * ArenaData["Berserks"] / ArenaData["Games"] / 2., "berserk", "Berserk rates in hourly arenas")
	SomeBoxPlot(lambda ArenaData: 100. * (ArenaData["Games"] - ArenaData["WhiteWins"] - ArenaData["BlackWins"]) / ArenaData["Games"], "draws", "Draw rates in hourly arenas")
	SomeBoxPlot(lambda ArenaData: 100. * (ArenaData["WhiteWins"] + 0.5 * (ArenaData["Games"] - ArenaData["WhiteWins"] - ArenaData["BlackWins"])) / ArenaData["Games"], "white", "White's score in hourly arenas")
	
	FilePlayersSorts = {
		"points": 		{"Name": "Players by total points",		"Plot": "Total points"},
		"trophies": 	{"Name": "Players by trophies",			"Plot": "Tournament victories"},
		"events":		{"Name": "Players by events",			"Plot": "Events participated"},
		#"average":		{"Name": "Players by average score",	"Plot": "Average score"},
		"maximum":		{"Name": "Players by high score",		"Plot": "High score"},
		"title":		{"Name": "Players by title",			"Plot": "Titled players by points"}
	}

	# Sorted partial rankings of arenas
	FileArenasSorts = {
		"newest": 		{"Name": "Arenas by date",				"Plot": "Cumulative arenas"},
		"players": 		{"Name": "Arenas by participants",		"Plot": "Participants"},
		"points": 		{"Name": "Arenas by points per player",	"Plot": "Points per player"},
		#"games":		{"Name": "Arenas by games per player",	"Plot": "Games per player"},
		"moves":		{"Name": "Arenas by moves per game",	"Plot": "Moves per player per game"},
		"rating":		{"Name": "Arenas by average rating",	"Plot": "Average rating"},
		"maximum":		{"Name": "Arenas by high score",		"Plot": "High score"},
		"berserk":		{"Name": "Arenas by berserk rate",		"Plot": "Berserk rate"}
	}

	# Build actual webpage
	with open("E:\\GitHub\\lichess\\rankings\\index.html", "w") as File:
		File.write("<!DOCTYPE html>\n")
		File.write("<html lang='en-US'>\n")
		File.write("<!-- Rankings built using the Lichess API (https://lichess.org/api) and some manual (python-based) tournament scraping. -->\n")
		File.write("<!-- Source code available at https://github.com/tmmlaarhoven/lichess -->\n")
		File.write("<head>\n")
		File.write(f"<title>Lichess Arena Rankings &middot; Information</title>\n")
		File.write("<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>\n")
		File.write("<link rel='icon' type='image/png' href='../favicon.ico'>\n")
		File.write("<link rel='stylesheet' href='../style-new.css'>\n")
		File.write("<link rel='stylesheet' href='../style-colors.css'>\n")
		File.write("<meta property='og:type' content='website'>\n")
		File.write("<meta property='og:title' content='Lichess Arena Rankings' />\n")
		File.write("<meta property='og:description' content='Statistics and rankings built from official Lichess arenas, ranging from hourly bullet arenas to titled arenas to bundesliga events. See who scored the most tournament victories, who played in the most events, who holds the all-time record for the highest score in each type of arena, and more!' />\n")
		File.write("<meta property='og:url' content='https://tmmlaarhoven.github.io/lichess/rankings' />\n")
		File.write("<meta property='og:image' content='https://tmmlaarhoven.github.io/lichess/rankings/box_rating.png' />\n")
		#File.write("<link rel='stylesheet' href='style-new.css'>\n")
		File.write("</head>\n\n")
		File.write("<body>\n")
		File.write(f"<div class=\"title\">Lichess Arena Rankings &middot; Information</div>\n")
		
		# Begin menu
		File.write("<div class='menu'>\n")
		
		# Information icon
		File.write("\t<span class='VariantIcon' style='font-size: 16pt; position: absolute; left: 0px;'><a href='index.html'>&#xe005;</a></span>\n")
		
		# Variants menu
		File.write("\t<span class='dropdown-el' style='left: 30px; min-width: 190px; max-width: 190px;'>\n")
		for V, Val in sorted(AllVariants.items(), key = lambda item: item[1]["WebOrder"]):
			File.write(f"\t\t<input type='radio' name='Variant' value='lichess/rankings/{V}' id='variant-{V}'{' checked' if V == 'all' else ''}><label class='V{V}' for='variant-{V}'><span class='VariantIcon'>{AllVariants[V]['Icon']}</span> {AllVariants[V]['Name'] if V != 'all' else 'All variants'}</label>\n")
		File.write("\t</span>\n")
		
		# Events menu
		File.write("\t<span class='dropdown-el' style='left: 230px; min-width: 170px; max-width: 170px;'>\n")
		for E, Val in sorted(AllEvents.items(), key = lambda item: item[1]["WebOrder"]):
			File.write(f"\t\t<input type='radio' name='Event' value='{E}' id='events-{E}'{' checked' if E == 'all' else ''}><label class='E{E}' for='events-{E}'>{AllEvents[E]['Name'] + ' Arenas' if E not in ['marathon', 'liga'] else ('Marathons' if E == 'marathon' else 'Bundesliga')}</label>\n")
		File.write("\t</span>\n")
		
		# Sorting menu
		File.write("\t<span class='dropdown-el' style='left: 410px; min-width: 260px; max-width: 260px;'>\n")
		for O in FilePlayersSorts:
			File.write(f"\t\t<input type='radio' name='Page' value='players_{O}' id='players_{O}'{' checked' if ('players_' + O) == 'players_trophies' else ''}><label for='players_{O}'>{FilePlayersSorts[O]['Name']}</label>\n")
		for O in FileArenasSorts:
			File.write(f"\t\t<input type='radio' name='Page' value='arenas_{O}' id='arenas_{O}'><label for='arenas_{O}'>{FileArenasSorts[O]['Name']}</label>\n")
		File.write("\t</span>\n")
		
		# List or graph?
		File.write("\t<span class='dropdown-el' style='left: 680px; min-width: 120px; max-width: 120px;'>\n")
		File.write(f"\t\t<input type='radio' name='Type' value='list' id='list' checked><label for='list'><span class='VariantIcon'>?</span> List</label>\n")
		File.write(f"\t\t<input type='radio' name='Type' value='graph' id='graph'><label for='graph'><span class='VariantIcon'>9</span> Graph</label>")
		File.write("\t</span>\n")
		
		File.write("</div>\n\n")				
		# End menu
		
		File.write("<span class='maincontent'>\n")
		File.write("<!-- START OF ACTUAL CONTENT -->\n\n")
		
		File.write("The rankings on this webpage are based on all official regularly-scheduled arenas played on <a href='https://lichess.org'>lichess.org</a> (hourly, <2000, <1700, <1600, <1500, <1300, daily, weekly, monthly, yearly, eastern, elite, and shield arenas) as well as the seasonal 24h marathons and the titled arenas. These rankings exclude irregular themed arenas (King's Gambit Blitz Arena, ...), and custom arenas created by users. In total these rankings cover over 400.000 events, in which over 200.000.000 games were played by over 80.000.000 arena participants (over 1.500.000 unique users), and together in all these games the users made over 14.000.000.000 moves. <br/><br/>\n\n")
		File.write("Some additional, detailed statistics about the rankings can be found below.")
		
		File.write("<img src='pie_participants.png' class='Graph'>\n")
		File.write("<img src='pie_events.png' class='Graph'>\n")
		File.write("<img src='pie_games.png' class='Graph'>\n")
		File.write("<img src='pie_moves.png' class='Graph'>\n")
		File.write("<img src='pie_points.png' class='Graph'>\n")
		
		File.write("<img src='box_participants.png' class='Graph'>\n")
		File.write("<img src='box_rating.png' class='Graph'>\n")
		File.write("<img src='box_moves.png' class='Graph'>\n")
		File.write("<img src='box_topscore.png' class='Graph'>\n")
		File.write("<img src='box_berserk.png' class='Graph'>\n")
		File.write("<img src='box_draws.png' class='Graph'>\n")
		File.write("<img src='box_white.png' class='Graph'>\n")
		
		
		
		File.write("<!-- END OF ACTUAL CONTENT -->\n")
		File.write("</span>\n")
		File.write("<script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>\n")
		File.write("<script src='../menu.js'></script>\n")
		File.write("</body>\n")
		File.write("</html>\n")
	

# For the index page: Pie charts
def SomePieChart(Function, Filename, Title):
	
	mpl.close()
	mpl.figure()
	valout = list()
	colout = list()
	labout = list()
	valin = list()
	colin = list()
	labin = list()
	
	#key = "Games"
	NewPureVariants = PureVariants.copy()
	NewPureVariants = dict(sorted(NewPureVariants.items(), key = lambda item: item[1]["WebOrder"]))
	for V in NewPureVariants:
		for E in PureEvents:
			if os.path.exists(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_ranking.json"):
				with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\{E}\\{V}_{E}_ranking.json", "r") as CatStatFile:
					CatStats = json.load(CatStatFile)
				newval = Function(CatStats)	
			else:
				newval = 0
			valin.append(newval)
			colin.append(tuple(x/255. for x in PureEvents[E]["RGB"]))
			labin.append(PureEvents[E]["Code"])
		if os.path.exists(f"E:\\lichess\\tournaments\\rankings\\{V}\\all\\{V}_all_ranking.json"):
			with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\all\\{V}_all_ranking.json", "r") as CatStatFile:
				CatStats = json.load(CatStatFile)
			newval = Function(CatStats)	
		else:
			newval = 0
		valout.append(newval)
		colout.append(tuple(x/255. for x in NewPureVariants[V]["RGB"]))
		labout.append(NewPureVariants[V]["Name"])
		
	fig1, ax1 = mpl.subplots()
	ax1.pie(valout, radius=1, colors=colout, labels=labout, rotatelabels=True, labeldistance=1.05, textprops={'fontsize': 10}, wedgeprops=dict(width=0.4, linewidth=0.5, edgecolor=(0.5,0.5,0.5)))
	#ax1.pie(valin, radius=0.6, colors=colin, labels=labin, labeldistance=1.1, textprops={'fontsize': 0}, wedgeprops=dict(width=0.3, edgecolor='w'))
	ax1.pie(valin, radius=0.6, colors=colin, wedgeprops=dict(width=0.3, linewidth=0.5, edgecolor=(0.5,0.5,0.5)))
	ax1.set(aspect="equal")
	ax1.set_title(Title, fontdict={'fontsize': 14})
	mpl.tight_layout()
	mpl.savefig(f"E:\\GitHub\\lichess\\rankings\\pie_{Filename}.png")
	print(f"Saving pie_{Filename}.png")
	mpl.clf()	
	

# For the index page: box plots
def SomeBoxPlot(Function, Filename, Title):

	mpl.close()
	mpl.figure()
	val = list()
	col = list()
	lab = list()
	fig1, ax1 = mpl.subplots()
	
	#key = "Games"
	NewPureVariants = PureVariants.copy()
	NewPureVariants = dict(sorted(NewPureVariants.items(), key = lambda item: item[1]["WebOrder"]))
	for Index, V in enumerate(NewPureVariants):
		newlist = list()
		if os.path.exists(f"E:\\lichess\\tournaments\\rankings\\{V}\\hourly\\{V}_hourly_arenas_newest.ndjson"):
			with open(f"E:\\lichess\\tournaments\\rankings\\{V}\\hourly\\{V}_hourly_arenas_newest.ndjson", "r") as ArenaFile:
				for Line in ArenaFile:
					ArenaData = json.loads(Line)
					newval = Function(ArenaData)
					newlist.append(newval)
		col1 = (tuple(min(1.,x/200.) for x in NewPureVariants[V]["RGB"]))
		col2 = (tuple(x/350. for x in NewPureVariants[V]["RGB"]))
		bp = ax1.boxplot([newlist], positions=[Index], widths=0.8, patch_artist=True)
		for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
			mpl.setp(bp[element], color=col1)
		mpl.setp(bp['fliers'], markeredgecolor=col2)
		mpl.setp(bp['boxes'], facecolor=col2)
		
	mpl.xticks(range(15), list(NewPureVariants[x]['Name'] for x in NewPureVariants))
	if Filename in {"draws", "white", "berserk"}:
		mpl.gca().yaxis.set_major_formatter(PercentFormatter(decimals = 0))
	if Filename in {"white", "berserk"}:
		mpl.gca().set_ylim([0, 100])
	if Filename in {"draws", "moves", "participants", "topscore"}:
		mpl.gca().set_ylim([0, None])
	mpl.setp(ax1.get_xticklabels(), rotation=45)
	ax1.set_title(Title, fontdict={'fontsize': 14})
	ax1.yaxis.grid(True) # Show the horizontal gridlines
	mpl.tight_layout()
	mpl.savefig(f"E:\\GitHub\\lichess\\rankings\\box_{Filename}.png")
	print(f"Saving box_{Filename}.png")
	mpl.clf()	


#######################################################################################################################################################################################
#######################################################################################################################################################################################
#######################################################################################################################################################################################

# Set global plot settings
mpl.style.use(['dark_background'])
mpl.rcParams.update({
	"axes.facecolor": 		(0.2, 0.2, 0.2, 1.0),  # green with alpha = 50%
	"savefig.facecolor": 	(0.0, 0.0, 1.0, 0.0),  # blue  with alpha = 20%
	"figure.figsize": 		(6.5, 6.5),
	"axes.labelsize": 		12,
	"xtick.labelsize": 		11,
	"ytick.labelsize": 		11,
	"legend.labelspacing": 	0.3,
	"legend.handlelength":	2.0,
	"legend.handletextpad": 0.3,
	"grid.color": 			(0.8, 0.8, 0.8),
	"grid.linestyle": 		":",
	"grid.linewidth": 		0.5,
	"legend.framealpha":	0.5,
	"font.family": 			['Roboto', 'serif'],
})

# Load horsey background for plots
LichessLogo = mpl.imread("logo.png")

# User plot colors: Use 500 series
UserPlotColors = Colors500 + Colors800
UserPlotColors.remove(( 66, 66, 66))	# Remove dark gray, making total 37
UserPlotColors[-1] = (176,190,197)		# Change dark blue gray to light blue gray (hourly bullet)
UserPlotColors[-2] = (188,170,164)		# Change dark brown to light brown

# User line plot styles
UserPlotStyles = ['solid', 'dashed', 'dotted']

# User plot markers
UserPlotMarkers = ['o', 'v', '^', '<', '>', 's', 'D']

# Assumption: lengths of Colors, Style, Markers are coprime
UserPlotModulus = len(UserPlotColors) * len(UserPlotStyles) * len(UserPlotMarkers)

# Hash username into tuple of color, style, marker
def UserHash(Username):
	UserID = Username.lower()
	UserValue = (sum(ord(UserID[i]) * ord(UserID[i]) for i in range(len(UserID))) + len(UserID)) % UserPlotModulus
	UserColorX = UserPlotColors[UserValue % len(UserPlotColors)]
	UserColor = tuple(x/255. for x in UserColorX)
	UserStyle = UserPlotStyles[UserValue % len(UserPlotStyles)]
	UserMarker = UserPlotMarkers[UserValue % len(UserPlotMarkers)]
	return (UserColor, UserStyle, UserMarker)

#######################################################################################################################################################################################
#######################################################################################################################################################################################
#######################################################################################################################################################################################

'''
ArenaCategory object: controls local data and update functions for a combination of event and variant.
Internally has functions for e.g. loading rankings, updating the rankings, the cumulative player rankings, plots, website.
'''
class ArenaCategory:
	
	# Initializing the category. Input: variant and event.
	def __init__(self, Variant: str, Event: str):
	
		# Check for correct input
		assert(Variant in AllVariants), f"Incorrect variant description."
		assert(Event in AllEvents), f"Incorrect event description."
		
		# Set variant, event
		self._V = Variant
		self._E = Event
		self.PrintMessage("Starting...")
		self._Prefix = f"{self._V}_{self._E}"
		self._Mixed = (False if (self._V in PureVariants and self._E in PureEvents) else True)
		self._Pure = not self._Mixed
		if self._V == "all":
			self._Vs = list(PureVariants.keys())
		else:
			self._Vs = [self._V]
		if self._E == "all":
			self._Es = list(PureEvents.keys())
		else:
			self._Es = [self._E]
			
		# Name of category for displays
		if self._E == "marathon":
			self._Name = f"{AllVariants[self._V]['Name']} Marathons"
		elif self._E == "liga":
			self._Name = f"{AllVariants[self._V]['Name']} Bundesliga Arenas"
		elif self._E == "all" and self._V == "all":
			self._Name = f"All Arenas"
		elif self._E == "shield" or (self._V == "all" and self._E != "all" and self._E != "marathon"):
			self._Name = f"{AllVariants[self._V]['Name']} {AllEvents[self._E]['Name']} Arenas"
		else:
			self._Name = f"{AllEvents[self._E]['Name']} {AllVariants[self._V]['Name']} Arenas"
			
		# Files stored locally in the data directory
		self._PathData = f"E:\\lichess\\tournaments\\data\\"
		if self._Pure:
			self._FileDataList = f"{self._PathData}{self._Prefix}.txt"
			self._FileDataDetailedList = f"{self._PathData}{self._Prefix}.ndjson"
		
		# Files stored locally in the rankings directory
		self._PathRanking = f"E:\\lichess\\tournaments\\rankings\\{self._V}\\{self._E}\\"
		self._FileRankingInfo = f"{self._PathRanking}{self._Prefix}_ranking.json"	
	
		# Sorted partial rankings of players
		self._FilePlayersFull = f"{self._PathRanking}{self._Prefix}_players.ndjson"
		self._FilePlayersSorts = {
			"points": 		{"Function": self._SortPlayersPoints, 		"Reverse": True, 	"Name": "Players by total points",		"Plot": "Total points"},
			"trophies": 	{"Function": self._SortPlayersTrophies, 	"Reverse": True, 	"Name": "Players by trophies",			"Plot": "Tournament victories"},
			"events":		{"Function": self._SortPlayersEvents,		"Reverse": True,	"Name": "Players by events",			"Plot": "Events participated"},
			#"average":		{"Function": self._SortPlayersAverage,		"Reverse": True,	"Name": "Players by average score",		"Plot": "Average score"},
			"maximum":		{"Function": self._SortPlayersMaximum,		"Reverse": True,	"Name": "Players by high score",		"Plot": "High score"},
			"title":		{"Function": self._SortPlayersTitle,		"Reverse": True,	"Name": "Players by title",				"Plot": "Titled players by points"}
		}
	
		# Sorted partial rankings of arenas
		self._FileArenasFull = f"{self._PathRanking}{self._Prefix}_arenas.ndjson"	
		self._FileArenasSorts = {
			"newest": 		{"Function": self._SortArenasNewest, 		"Reverse": True, 	"Name": "Arenas by date",				"Plot": "Cumulative arenas"},
			"players": 		{"Function": self._SortArenasPlayers, 		"Reverse": True, 	"Name": "Arenas by participants",		"Plot": "Participants"},
			"points": 		{"Function": self._SortArenasPoints, 		"Reverse": True, 	"Name": "Arenas by points per player",	"Plot": "Points per player"},
			#"games":		{"Function": self._SortArenasGames,			"Reverse": True,	"Name": "Arenas by games per player",	"Plot": "Games per player"},
			"moves":		{"Function": self._SortArenasMoves,			"Reverse": True,	"Name": "Arenas by moves per game",		"Plot": "Moves per player per game"},
			"rating":		{"Function": self._SortArenasRating,		"Reverse": True,	"Name": "Arenas by average rating",		"Plot": "Average rating"},
			"maximum":		{"Function": self._SortArenasMaximum,		"Reverse": True,	"Name": "Arenas by high score",			"Plot": "High score"},
			"berserk":		{"Function": self._SortArenasBerserk,		"Reverse": True,	"Name": "Arenas by berserk rate",		"Plot": "Berserk rate"}
		}
		
		# Files stored locally about player cumulative scores over time (for plots)
		self._PathPlayers = f"{self._PathRanking}players\\"
		self._FilePlayerList = f"{self._PathPlayers}{self._Prefix}.txt"
		
		# ALl files stored locally and externally in the website directory
		self._PathWeb = f"E:\\GitHub\\lichess\\rankings\\{self._V}\\{self._E}\\"
		self._PathWebRoot = f"E:\\GitHub\\lichess\\"
		self._PathFigures = f"E:\\GitHub\\lichess\\rankings\\{self._V}\\{self._E}\\figures\\"
		self._WebListLength = 200
		
		# Initialize data maintenance parameters
		self._DataList = OrderedDict()			# All arena IDs:		{"jf03alf3": {"Number": 1, "ID": "jf03alf3", "Players": 23, "Variant": "bullet", "Event": "hourly", ...}, "dkweo3kX", ...}
		self._NewList = OrderedDict()			# IDs not in ranking:	["jf03alf3": {...}, ...]
		self._RankingInfo = dict()				# Global ranking info:	{"Events": 200, "Participants": 50240, "Players": 12104, "Games": 1239052, "Moves": 2130935, ...}
		self._RankingList = OrderedDict()		# Arenas in ranking:	{"jf03alf3": {"Number": 1, "ID": "jf03alf3", "Players": 23, "Variant": "bullet", "Event": "hourly", ...}, ...}
		self._Ranking = OrderedDict()			# Player rankings:		{"thijscom": {"Username": "thijscom", "Ranking": 1, "Points": 354, "Events": 12, ...}, ...}
		self._PlayerList = OrderedDict()		# Players potentially for plots, and for whom we keep track of cumulative rankings:	["thijscom", "DrNykterstein", "dugong161", ...]
		self._PlayerListTop = OrderedDict()		# Players actually used for plots:	["DrNykterstein", "penguingim1", ...]
		self._PlayerStatus = OrderedDict()			# Latest player status:	{"thijscom": {..., "CumTrophies": [13, 11, 15], "CumEvents": 210, "CumTopScore": ...}, ...}
		self._UpToDate = False
		
		# Initialize some directories if they do not exist yet
		for Path in {self._PathData, self._PathRanking, self._PathPlayers, self._PathWeb, self._PathFigures}:
			if not os.path.exists(Path):
				self.PrintMessage(f"Creating directory {Path}.")
				os.makedirs(Path)
				
		# Load API token for Lichess API queries
		with open(f"E:\\lichess\\APIToken.txt", "r") as TokenFile:
			for Line in TokenFile:
				self._APIToken = Line.strip()
				assert(len(self._APIToken) == 16), f"API token not of length 16."

	
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	'''
	Functionalities implemented:
	
	1. LoadRankings(self)						 (P	/ M)	
	 a. _LoadDataList(self)						# P	/ M	#	Load list of IDs for which data has been fetched -- assumption is that FetchData.py finished and updated the data files
	 b. _LoadRankingInfo(self)					# P	/ M	#	Loads information about rankings to date
	 c. _LoadRankingList(self)					# P	/ M	#	Loads list of IDs previously included in rankings
	 d. _LoadRankingData(self)					# P	/ M	#	Loads actual detailed rankings in big dictionary
	 e. _LoadPlayerList(self)					# P	/ M	#	Loads list of top players to update cumulative rankings for plots
	 f. _FixPlayers(self)						# P / M #	If no list of players exists, fix this and make up to date lists
	 g. _LoadPlayerStatus(self)					# P / M #	Loads latest player statuses for cumulative updates
	 h. _LoadMissingList(self)					# P	/ M	#	Generates list of missing IDs and detailed info for later
	
	2. UpdateRankings(self)						 (P	/ M)
	 a. _UpdateRankingPlayer(self, ...)			# P	/ M	#	For a given player and tournament result, update their ranking
	 b. _UpdateRankingStats(self, ArenaData)	# P	/ M	#	Update the ranking info based on the stats of one new tournament
	 c. _StorePlayerRankings(self)				# P	/ M	#	Store the player rankings to files, the full list and partial lists in different orders
	 d. _StoreArenaRankings(self)				# P	/ M	#	Store the list of arenas to files, the full list and partial lists in different orders
	
	3. UpdatePlots(self)						 (P	/ M)	
	 a. _UpdatePlayerPlots(self)				# P	/ M	#	Generate plots of top 10 players in these lists over time	
	 b. _UpdateArenaPlots(self)					# P	/ M	#	Generate plots of the arena statistics over time (individual and moving average)
	 
		
	4. UpdateWebsite(self)						 (P / M)	
	 a. _WritePre(self, ...)					# P	/ M	#	The part of the website before the main content (menu, styles, etc.)
	 b. _WritePost(self, ...)					# P	/ M	#	The part of the website after the main content (menu script, closing)
	 
	'''
	
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# Functions for sorting player rankings
	def _SortPlayersFull(self, item):
		return item["Score"]
	def _SortPlayersPoints(self, item):
		return item["Score"]
	def _SortPlayersTrophies(self, item):
		return 100000000 * item["Trophies"][0] + 10000 * item["Trophies"][1] + item["Trophies"][2]
	def _SortPlayersEvents(self, item):
		return item["Events"] - item.get("Zeros", 0)
	def _SortPlayersAverage(self, item):
		return item["Score"] / max(1, item["Events"])
	def _SortPlayersMaximum(self, item):
		return item["TopScore"]
	_TitleMapping = {"GM": 11, "WGM": 10, "IM": 9, "WIM": 8, "FM": 7, "WFM": 6, "CM": 5, "WCM": 4, "NM": 3, "WNM": 2, "LM": 1, "BOT": 0}
	def _SortPlayersTitle(self, item):
		if not "Title" in item or item["Score"] == 0:
			return 0
		else:
			return self._TitleMapping[item["Title"]]
	
	# Functions for sorting arena rankings
	def _SortArenasFull(self, item):
		return item["Start"]
	def _SortArenasNewest(self, item):
		return item["Start"]
	def _SortArenasPlayers(self, item):
		return item["Players"]
	def _SortArenasPoints(self, item):
		return item["TotalPoints"] / max(1, item["Players"])
	def _SortArenasGames(self, item):
		return item["Games"] / max(1, item["Players"])
	def _SortArenasMoves(self, item):
		return item["Moves"] / max(1, item["Games"])
	def _SortArenasRating(self, item):
		return item["TotalRating"] / max(1, item["Players"])
	def _SortArenasMaximum(self, item):
		return item["TopScore"]
	def _SortArenasBerserk(self, item):
		return item["Berserks"] / max(1, item["Games"])
		
	# Printing a message to the command line, when running in verbose mode.
	def PrintMessage(self, Message: str):
		print(f"{self._V:<11} - {self._E:<8} - {Message}")	
		
	# Converting a date string to something that can be displayed
	_Months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
	def DateString(self, Date):
		# DateString: "2020-02-27"
		return f"<span class='info' title='{self._Months[Date[5:7]]} {Date[8:10]}, {Date[0:4]} at {Date[11:16]} UTC'>{self._Months[Date[5:7]]} {Date[8:10]}, {Date[0:4]}</span>"
	
	# Time range for when a user has been active in this category
	def TimeRange1(self, Date):
		return f"<span class='info' title='{self._Months[Date[5:7]]} {Date[8:10]}, {Date[0:4]} at {Date[11:16]} UTC'>{self._Months[Date[5:7]]}'{Date[2:4]}</span>"
	def TimeRange2(self, Date):
		return f"<span class='info' title='{self._Months[Date[5:7]]} {Date[8:10]}, {Date[0:4]} at {Date[11:16]} UTC'>{self._Months[Date[5:7]]}'{Date[2:4]}</span>"

	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# 1. Load all data in memory
	def LoadRankings(self):
		self.PrintMessage("1. Loading...")	
		self._LoadDataList()			# Up to date data that has been fetched
		self._LoadRankingInfo()			# Current global information about rankings
		if len(self._DataList) == self._RankingInfo["Events"]:
			self._UpToDate = True
			self.PrintMessage("Nothing to do...")

			# To reset player cumulative rankings
			if len(self._DataList) > 0 and (not os.path.exists(self._FilePlayerList)):
				self.PrintMessage("Fixing some missing files...")
				self._LoadRankingList()		# Detailed list of events currently in rankings
				self._LoadRankingData()		# Detailed state of rankings
				self._LoadPlayerList()		# Top players for cumulative scores
				self._LoadPlayerStatus()	# For those top players, load most recent info
				self._LoadMissingList()		# Make a list of detailed arena info for updates


		else:
			self._UpToDate = False
			self.PrintMessage(f"Out of {len(self._DataList)} events, only {self._RankingInfo['Events']} included in rankings so far.")
			self._LoadRankingList()		# Detailed list of events currently in rankings
			self._LoadRankingData()		# Detailed state of rankings
			self._LoadPlayerList()		# Top players for cumulative scores
			self._LoadPlayerStatus()	# For those top players, load most recent info
			self._LoadMissingList()		# Make a list of detailed arena info for updates
		# self._FIXUSERFILES()		# TEMPORARY FIX	
	
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
		
	# 1a. Load all IDs till now from a file (both IDs included in the ranking and those not yet in the ranking).
	def _LoadDataList(self):
		for V, E in product(self._Vs, self._Es):
			if os.path.exists(f"{self._PathData}{V}\\{E}\\{V}_{E}.txt") and os.path.exists(f"{self._PathData}{V}\\{E}\\{V}_{E}.ndjson"):
				with open(f"{self._PathData}{V}\\{E}\\{V}_{E}.ndjson", "r") as FileDataDetailedList:
					for Line in FileDataDetailedList:
						ArenaData = json.loads(Line)
						self._DataList[ArenaData["ID"]] = ArenaData
		self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda Arena: Arena[1]["Start"]))

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	# 1b. Load ranking information from JSON file.
	def _LoadRankingInfo(self):
		if os.path.exists(self._FileRankingInfo): 
			with open(self._FileRankingInfo, "r") as FileRankingInfo:
				self._RankingInfo = json.load(FileRankingInfo)
			if self._RankingInfo["Events"] == 0:
				os.remove(self._FileRankingInfo)
		else:
			
			self._RankingInfo = {"Events": 0, "Participants": 0, "Games": 0, "Moves": 0, "WhiteWins": 0, "BlackWins": 0, "Berserks": 0, "TotalPoints": 0, "TotalRating": 0, "FirstStart": "2030-01-01T00:00:00.000Z", "FirstID": "XXXXXXXX", "LastStart": "2010-01-01T00:00:00.000Z", "LastID": "YYYYYYYY", "MaxUsers": 0, "MaxUsersID": "ZZZZZZZZ", "TopScore": 0, "TopScoreID": "WWWWWWWW", "TopUser": "-", "Players": 0}
			if len(self._DataList) > 0:
				for ID in self._DataList:
					self._RankingInfo["FirstID"] = self._DataList[ID]["ID"]
					self._RankingInfo["FirstStart"] = self._DataList[ID]["Start"]
					break
			with open(self._FileRankingInfo, "w") as FileRankingInfo:
				FileRankingInfo.write(json.dumps(self._RankingInfo))

		assert(self._RankingInfo["Events"] <= len(self._DataList)), f"Ranking information shows more events than the more up to date list of IDs!" 		

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1c. Load ranking list of arenas from file (subset of all IDs, namely those that have been processed).
	def _LoadRankingList(self):
		if os.path.exists(self._FileArenasFull):	
			with open(self._FileArenasFull, "r") as FileRankingList:
				for Line in FileRankingList:
					ArenaData = json.loads(Line)
					self._RankingList[ArenaData["ID"]] = ArenaData
			self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda Arena: Arena[1]["Start"]))
			self.PrintMessage(f"Loaded {len(self._RankingList)} detailed arena statistics from file.")
		else:
			self.PrintMessage(f"No file with detailed arena statistics found.")

		assert(self._RankingInfo["Events"] == len(self._RankingList)), f"Ranking information shows a different number of events than the detailed ranking list."	

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1d. If we need to update rankings, then we need to load the rankings data.
	def _LoadRankingData(self):
		if os.path.exists(self._FilePlayersFull):	
			with open(self._FilePlayersFull, "r") as FileRankingData:
				for Line in FileRankingData:
					UserRank = json.loads(Line)
					self._Ranking[UserRank["Username"].lower()] = UserRank
		else:
			self.PrintMessage(f"No file with detailed ranking data found.")
			assert(len(self._RankingList) == 0), f"How come no detailed ranking file exists?"

		# Checks for internal consistency of existing rankings
		if len(self._RankingList) > 0:
			assert("Events" in self._RankingInfo), "Inconsistent ranking files. No entry Events in RankInfo."
			assert("FirstID" in self._RankingInfo), "Inconsistent ranking files. No entry FirstID in RankInfo."
			assert("LastID" in self._RankingInfo), "Inconsistent ranking files. No entry LastID in RankInfo."
			assert(self._RankingInfo["Events"] == len(self._RankingList)), "Inconsistent ranking files. Unequal number of events."
			assert(self._RankingInfo["FirstID"] in self._RankingList), "Inconsistent ranking files. Unequal first IDs."
			assert(self._RankingInfo["LastID"] in self._RankingList), "Inconsistent ranking files. Unequal last IDs."
		
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1e. Load players for cumulative rankings from file.
	def _LoadPlayerList(self):
		if not os.path.exists(self._FilePlayerList):
			self.PrintMessage(f"No list of players yet. Making one based on rankings...")
			if len(self._RankingList) > 0:
				self._FixPlayers()
		else:
			with open(self._FilePlayerList, "r") as FilePlayerList:
				for Line in FilePlayerList:
					UserID = Line.strip().lower()
					self._PlayerList[UserID] = 1
			self._PlayerList = OrderedDict(sorted(self._PlayerList.items(), key = lambda item: item[0]))
			self.PrintMessage(f"Loaded {len(self._PlayerList)} users from file for chronological rankings.")

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1f. In case no player files exist yet, generate them now from past tournaments.
	def _FixPlayers(self):
		# First build list of relevant players to maintain, say top 100
		self.PrintMessage(f"Building list of relevant players...")
		for SortOrder in self._FilePlayersSorts:
			if SortOrder == "points":
				FileName = f"{self._PathRanking}{self._Prefix}_players.ndjson"
			else:
				FileName = f"{self._PathRanking}{self._Prefix}_players_{SortOrder}.ndjson"
			with open(FileName, "r") as FileTopPlayers:
				for Index, Line in enumerate(FileTopPlayers):
					UserRanking = json.loads(Line.strip())
					UserID = UserRanking["Username"].lower()
					self._PlayerList[UserID] = 1
					if Index > 100:
						break
		self.PrintMessage(f"Loaded {len(self._PlayerList)} users into a list.")
		self._PlayerList = OrderedDict(sorted(self._PlayerList.items(), key = lambda item: item[0]))
		
		# Initialize empty JSON and NDJSON files
		UserJSON = dict()
		UserNDJSON = dict()
		for Username in self._PlayerList:
			UserID = Username.lower()
			UserJSON[UserID] = dict()
			UserJSON[UserID]["Variant"] = self._V
			UserJSON[UserID]["Event"] = self._E
			UserJSON[UserID]["Username"] = UserID
			UserJSON[UserID]["FirstID"] = "-"
			UserJSON[UserID]["LastID"] = "-"
			UserJSON[UserID]["CumTrophies"] = [0, 0, 0]
			UserJSON[UserID]["CumPoints"] = 0
			UserJSON[UserID]["CumEvents"] = 0
			UserJSON[UserID]["CumTopScore"] = 0
			UserNDJSON[UserID] = []
		
		# Then fetch data from arenas already in rankings and update
		self.PrintMessage(f"Updating the users based on past events.")
		for Index, ID in enumerate(self._RankingList):
			V = self._RankingList[ID]["Variant"]
			E = self._RankingList[ID]["Event"]
			with open(f"{self._PathData}{V}\\{E}\\{V}_{E}_{ID}.ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					if UserResult["score"] == 0:
						break
					if UserResult["username"].lower() in self._PlayerList and UserResult["score"] > 0:
						
						# Update JSON stats
						UserID = UserResult["username"].lower()
						if UserJSON[UserID]["FirstID"] == "-":
							UserJSON[UserID]["FirstID"] = ID
						UserJSON[UserID]["LastID"] = ID
						if UserResult["rank"] == 1:
							UserJSON[UserID]["CumTrophies"][0] = UserJSON[UserID]["CumTrophies"][0] + 1
						elif UserResult["rank"] == 2:
							UserJSON[UserID]["CumTrophies"][1] = UserJSON[UserID]["CumTrophies"][1] + 1
						elif UserResult["rank"] == 3:
							UserJSON[UserID]["CumTrophies"][2] = UserJSON[UserID]["CumTrophies"][2] + 1
						UserJSON[UserID]["CumPoints"] = UserJSON[UserID]["CumPoints"] + UserResult["score"]
						UserJSON[UserID]["CumEvents"] = UserJSON[UserID]["CumEvents"] + 1
						UserJSON[UserID]["CumTopScore"] = max(UserJSON[UserID]["CumTopScore"], UserResult["score"])
						
						# Update NSJSON stats
						newdict = dict()
						newdict["ID"] = ID
						newdict["Start"] = self._RankingList[ID]["Start"]
						newdict["CumTrophies"] = UserJSON[UserID]["CumTrophies"].copy()
						newdict["CumPoints"] = UserJSON[UserID]["CumPoints"]
						newdict["CumEvents"] = UserJSON[UserID]["CumEvents"]
						newdict["CumTopScore"] = UserJSON[UserID]["CumTopScore"]
						UserNDJSON[UserID].append(newdict)
			
			# Intermediate progress update
			if Index % 1000 == 999:
				self.PrintMessage(f"Finished processing {Index + 1} events. (Nothing saved...)")
		
		# Final dump
		self.PrintMessage(f"Storing cumulative player scores after {len(self._RankingList)} past events.")
		for UserID in self._PlayerList:
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json", "w") as JSONFile:
				json.dump(UserJSON[UserID], JSONFile)
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson", "w") as NDJSONFile:
				for Index in range(len(UserNDJSON[UserID])):
					NDJSONFile.write(json.dumps(UserNDJSON[UserID][Index]) + "\n")
					
		# Print list of usernames to file
		self._PlayerList = OrderedDict(sorted(self._PlayerList.items(), key = lambda item: item[0]))
		with open(f"{self._PathPlayers}{self._V}_{self._E}.txt", "w") as UsernameFile:
			for Username in self._PlayerList:
				UsernameFile.write(Username.lower() + "\n")
					
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1g. In case no player files exist yet, generate them now from past tournaments.
	def _LoadPlayerStatus(self):	
		#assert(len(self._PlayerList) > 100), "How is this possible?"
		for UserID in self._PlayerList:
			assert(os.path.exists(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json")), "What?"
			assert(os.path.exists(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson")), "What??"
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json", "r") as JSONFile:
				self._PlayerStatus[UserID] = json.load(JSONFile)	

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 1h. Find list of missing events
	def _LoadMissingList(self):
		for ID in self._DataList:
			if ID not in self._RankingList:
				self._NewList[ID] = self._DataList[ID].copy()
		self._NewList = OrderedDict(sorted(self._NewList.items(), key = lambda Arena: Arena[1]["Start"]))
	
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# 2. Updating the rankings
	def UpdateRankings(self):
	
		self.PrintMessage("2. Updating rankings...")
		if self._UpToDate:
			self.PrintMessage("Nothing to do! Already up to date.")
			return
		
		# Checks for internal consistency of existing rankings
		if len(self._RankingList) > 0:
			for ID in self._DataList:
				self._RankingInfo["FirstID"] = self._DataList[ID]["ID"]
				self._RankingInfo["FirstStart"] = self._DataList[ID]["Start"]
				break
			assert(len(self._Ranking) > 0), "Inconsistent ranking files. No users in rankings."
			assert("Events" in self._RankingInfo), "Inconsistent ranking files. No entry Events in RankInfo."
			assert("LastID" in self._RankingInfo), "Inconsistent ranking files. No entry LastID in RankInfo."
			assert(self._RankingInfo["Events"] == len(self._RankingList)), f"Inconsistent ranking files. Unequal number of events. {self._RankingInfo['Events']} != {len(self._RankingList)}"
			assert(self._RankingInfo["FirstID"] in self._RankingList), "Inconsistent ranking files. Unequal first IDs."
			assert(self._RankingInfo["LastID"] in self._RankingList), "Inconsistent ranking files. Unequal last IDs."
	
		# Go through all new events
		for Index, ID in enumerate(self._NewList):
			ArenaData = self._NewList[ID]
			V = ArenaData["Variant"]
			E = ArenaData["Event"]
			self.PrintMessage(f"New event: {ID}.")
			assert(ArenaData["ID"] not in self._RankingList), "Inconsistent rankings. New tournament ID already included."
			
			# Load tournament results
			with open(f"{self._PathData}{V}\\{E}\\{V}_{E}_{ID}.ndjson", "r") as ResultsFile:
				for Line in ResultsFile:
					UserResult = json.loads(Line)
					# UserResult: {"rank": 1, "score": 36, "rating": 2267, "username": "kasparovsabe", "title": "FM", "performance": 2454}
					UserID = UserResult["username"].lower()
					
					if UserID not in self._Ranking:
						# New player
						self._Ranking[UserID] = dict()
						self._RankingInfo["Players"] = self._RankingInfo.get("Players", 0) + 1
					
					# Update player information
					self._UpdateRankingPlayer(UserID, UserResult, ArenaData)
					self._Ranking[UserID]["Username"] = UserResult["username"].lower()
					
					# For special players, add new cumulative score to files
					if UserID in self._PlayerList and UserResult["score"] > 0:
						
						# Update JSON stats
						self._PlayerStatus[UserID]["LastID"] = ID
						if UserResult["rank"] == 1:
							self._PlayerStatus[UserID]["CumTrophies"][0] = self._PlayerStatus[UserID]["CumTrophies"][0] + 1
						elif UserResult["rank"] == 2:
							self._PlayerStatus[UserID]["CumTrophies"][1] = self._PlayerStatus[UserID]["CumTrophies"][1] + 1
						elif UserResult["rank"] == 3:
							self._PlayerStatus[UserID]["CumTrophies"][2] = self._PlayerStatus[UserID]["CumTrophies"][2] + 1
						self._PlayerStatus[UserID]["CumPoints"] = self._PlayerStatus[UserID]["CumPoints"] + UserResult["score"]
						self._PlayerStatus[UserID]["CumEvents"] = self._PlayerStatus[UserID]["CumEvents"] + 1
						self._PlayerStatus[UserID]["CumTopScore"] = max(self._PlayerStatus[UserID]["CumTopScore"], UserResult["score"])

						# Save new entry to user files
						with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.ndjson", "a+") as NDJSONFile:
							newdict = dict()
							newdict["ID"] = ID
							newdict["Start"] = ArenaData["Start"]
							newdict["CumTrophies"] = self._PlayerStatus[UserID]["CumTrophies"].copy()
							newdict["CumPoints"] = self._PlayerStatus[UserID]["CumPoints"]
							newdict["CumEvents"] = self._PlayerStatus[UserID]["CumEvents"]
							newdict["CumTopScore"] = self._PlayerStatus[UserID]["CumTopScore"]
							NDJSONFile.write(json.dumps(newdict) + "\n")

			# Update global statistics
			self._UpdateRankingInfo(ArenaData)
				
			# Update newly processed events, and do intermediate data dumps
			if Index % 1000 == 0 and Index > 0:
				self.PrintMessage(f"Processed {Index} new events.")

		# Wrap up
		self.PrintMessage(f"Final dump after {len(self._NewList)} new events.")	
		self._StorePlayerRankings()
		
		# Print information to json
		with open(self._FileRankingInfo, "w") as RankInfoFile:
			RankInfoFile.write(json.dumps(self._RankingInfo))
		
		# Store new user JSON status in files
		for UserID in self._PlayerList:
			with open(f"{self._PathPlayers}{self._V}_{self._E}_{UserID}.json", "w") as JSONFile:
				json.dump(self._PlayerStatus[UserID], JSONFile)	
		
		# Sort all events by date (should be unnecessary) and store them in a file
		self._DataList = OrderedDict(sorted(self._DataList.items(), key = lambda Arena: Arena[1]["Start"]))
		with open(self._FileArenasFull, "w") as RankListFile:
			for Index, (ID, Arena) in enumerate(self._DataList.items()):
				Arena["Number"] = Index + 1
				RankListFile.write(json.dumps(Arena) + "\n")	
				
		# Also store arenas in different orders
		self._StoreArenaRankings()
		
		# Finally, now that we have a list of top players, see if we need to go back and make cumulative user rankings
		if not os.path.exists(self._FilePlayerList) and len(self._RankingList) > 0:
			self.PrintMessage(f"Rankings stored but no list of players yet. Making one based on rankings...")
			self._FixPlayers()

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	# 2a. Update player ranking in self._Ranking
	def _UpdateRankingPlayer(self, UserID, UserResult, ArenaData):
		self._Ranking[UserID]["Ranking"] = 0
		self._Ranking[UserID]["Score"] = self._Ranking[UserID].get("Score", 0) + UserResult["score"]
		self._Ranking[UserID]["Events"] = self._Ranking[UserID].get("Events", 0) + 1
		if not "First" in self._Ranking[UserID]:
			self._Ranking[UserID]["First"] = ArenaData["Start"]
			self._Ranking[UserID]["FirstID"] = ArenaData["ID"]
		self._Ranking[UserID]["Last"] = ArenaData["Start"]
		self._Ranking[UserID]["LastID"] = ArenaData["ID"]
		if self._Ranking[UserID].get("TopScore", -1) <= UserResult["score"]:
			self._Ranking[UserID]["TopScore"] = UserResult["score"]
			self._Ranking[UserID]["TopScoreID"] = ArenaData["ID"]
		if self._Ranking[UserID].get("MaxRank", 1000000) >= UserResult["rank"]:
			self._Ranking[UserID]["MaxRank"] = UserResult["rank"]
			self._Ranking[UserID]["MaxRankID"] = ArenaData["ID"]
		self._Ranking[UserID]["Username"] = UserResult["username"]
		if not "Trophies" in self._Ranking[UserID]:
			self._Ranking[UserID]["Trophies"] = [0, 0, 0]
		self._Ranking[UserID]["Trophies"][0] = self._Ranking[UserID]["Trophies"][0] + (1 if UserResult["rank"] == 1 else 0)
		self._Ranking[UserID]["Trophies"][1] = self._Ranking[UserID]["Trophies"][1] + (1 if UserResult["rank"] == 2 else 0)
		self._Ranking[UserID]["Trophies"][2] = self._Ranking[UserID]["Trophies"][2] + (1 if UserResult["rank"] == 3 else 0)
		if "title" in UserResult:
			self._Ranking[UserID]["Title"] = UserResult["title"]
		self._Ranking[UserID]["Zeros"] = self._Ranking[UserID].get("Zeros", 0) + (1 if UserResult["score"] == 0 else 0)

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	# 2b. Updating ranking info based on some arena data
	def _UpdateRankingInfo(self, ArenaData):
		self._RankingInfo["Events"] = self._RankingInfo.get("Events", 0) + 1
		self._RankingInfo["Participants"] = self._RankingInfo.get("Participants", 0) + ArenaData["Players"]
		self._RankingInfo["Games"] = self._RankingInfo.get("Games", 0) + ArenaData["Games"]
		self._RankingInfo["Moves"] = self._RankingInfo.get("Moves", 0) + ArenaData["Moves"]
		self._RankingInfo["WhiteWins"] = self._RankingInfo.get("WhiteWins", 0) + ArenaData["WhiteWins"]
		self._RankingInfo["BlackWins"] = self._RankingInfo.get("BlackWins", 0) + ArenaData["BlackWins"]
		self._RankingInfo["Berserks"] = self._RankingInfo.get("Berserks", 0) + ArenaData["Berserks"]
		self._RankingInfo["TotalPoints"] = self._RankingInfo.get("TotalPoints", 0) + ArenaData["TotalPoints"]
		self._RankingInfo["TotalRating"] = self._RankingInfo.get("TotalRating", 0) + ArenaData["TotalRating"]
		if not "FirstID" in self._RankingInfo:
			self._RankingInfo["FirstStart"] = ArenaData["Start"]
			self._RankingInfo["FirstID"] = ArenaData["ID"]
		self._RankingInfo["LastStart"] = ArenaData["Start"]
		self._RankingInfo["LastID"] = ArenaData["ID"]
		if self._RankingInfo.get("MaxUsers", 0) < ArenaData["Players"]:
			self._RankingInfo["MaxUsers"] = ArenaData["Players"]
			self._RankingInfo["MaxUsersID"] = ArenaData["ID"]
		if self._RankingInfo.get("TopScore", 0) < ArenaData["TopScore"]:
			self._RankingInfo["TopScore"] = ArenaData["TopScore"]
			self._RankingInfo["TopScoreID"] = ArenaData["ID"]
			self._RankingInfo["TopUser"] = ArenaData["#1"]
		
		# Also update list of events included in rankings
		self._RankingList[ArenaData["ID"]] = ArenaData
	
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 2c. Sort and store rankings to files
	def _StorePlayerRankings(self):
		
		# Store full rankings
		self._Ranking = OrderedDict(sorted(self._Ranking.items(), key = lambda item: self._SortPlayersFull(item[1]), reverse = True))
		with open(self._FilePlayersFull, "w") as UserFile:
			for Index, UserID in enumerate(self._Ranking):
				self._Ranking[UserID]["Ranking"] = Index + 1
				UserFile.write(json.dumps(self._Ranking[UserID]) + "\n")					
		
		# Store partial rankings in different orders
		for SortPlayerOrder in self._FilePlayersSorts:
			self._Ranking = OrderedDict(sorted(self._Ranking.items(), key = lambda item: self._SortPlayersFull(item[1]), reverse = True))
			self._Ranking = OrderedDict(sorted(self._Ranking.items(), key = lambda item: self._FilePlayersSorts[SortPlayerOrder]["Function"](item[1]), reverse = self._FilePlayersSorts[SortPlayerOrder]["Reverse"]))
			with open(f"{self._PathRanking}{self._Prefix}_players_{SortPlayerOrder}.ndjson", "w") as UserFile:
				for Index, UserID in enumerate(self._Ranking):
					self._Ranking[UserID]["Ranking"] = Index + 1
					UserFile.write(json.dumps(self._Ranking[UserID]) + "\n")					
					if Index == 999:
						break
		
		# Restore list in proper order
		self._Ranking = OrderedDict(sorted(self._Ranking.items(), key = lambda item: self._SortPlayersFull(item[1]), reverse = True))
		for Index, UserID in enumerate(self._Ranking):
			self._Ranking[UserID]["Ranking"] = Index + 1
		
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	# 2d. Sort and store lists of arenas to files		
	def _StoreArenaRankings(self):

		# Store full rankings
		self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda item: self._SortArenasFull(item[1]), reverse = False))
		with open(self._FileArenasFull, "w") as ArenaFile:
			for Index, ArenaID in enumerate(self._RankingList):
				self._RankingList[ArenaID]["Number"] = Index + 1
				ArenaFile.write(json.dumps(self._RankingList[ArenaID]) + "\n")	
				
		# Store partial rankings in different orders
		for SortArenaOrder in self._FileArenasSorts:
			self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda item: self._SortArenasFull(item[1]), reverse = False))
			self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda item: self._FileArenasSorts[SortArenaOrder]["Function"](item[1]), reverse = self._FileArenasSorts[SortArenaOrder]["Reverse"]))
			with open(f"{self._PathRanking}{self._Prefix}_arenas_{SortArenaOrder}.ndjson", "w") as ArenaFile:
				for Index, ArenaID in enumerate(self._RankingList):
					self._RankingList[ArenaID]["Number"] = Index + 1
					ArenaFile.write(json.dumps(self._RankingList[ArenaID]) + "\n")					
					if Index == 999:
						break		

		# Restore list in proper order
		self._RankingList = OrderedDict(sorted(self._RankingList.items(), key = lambda item: self._SortArenasFull(item[1]), reverse = False))
		for Index, ArenaID in enumerate(self._RankingList):
			self._RankingList[ArenaID]["Number"] = Index + 1
		
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	
	# 3. Making plots for the website
	def UpdatePlots(self):
		self.PrintMessage("3. Updating plots...")
		self._UpdatePlayerPlots()
		self._UpdateArenaPlots()
		return



	# 3a. Plots of the top user statistics over time
	def _UpdatePlayerPlots(self):
	
		# Load arenas list into temporary object
		if not os.path.exists(f"{self._PathRanking}{self._Prefix}_players.ndjson"):
			self.PrintMessage("Nothing to do...")
			return	
		
		# Process each sort order
		for SortPlayerOrder in self._FilePlayersSorts:
				
			# Initialize plotting procedure
			mpl.close()
			mpl.figure()
			Legend = []
	
			# Open rankings to find top 10 players
			TopPlayers = []
			with open(f"{self._PathRanking}{self._Prefix}_players_{SortPlayerOrder}.ndjson", "r") as RankFile:
				for Line in RankFile:
					RankEntry = json.loads(Line)
					TopPlayers.append(RankEntry["Username"].lower())
					Legend.append(RankEntry["Username"].lower())
					if RankEntry["Ranking"] == 10:
						break
				
			# For each of the top 10 players
			for Index in range(10):
				UserID = TopPlayers[Index]
				# Load right variables
				X = []
				Y = []
				CumTrophies = 0
				CumPoints = 0
				CumEvents = 0
				CumTopScore = 0
				with open(f"{self._PathPlayers}{self._Prefix}_{UserID}.ndjson", "r") as UserFile:
					for Line in UserFile:
						UserEntry = json.loads(Line)
						TimeNext = datetime.datetime(int(UserEntry["Start"][0:4]), int(UserEntry["Start"][5:7]), int(UserEntry["Start"][8:10]), int(UserEntry["Start"][11:13]), int(UserEntry["Start"][14:16]), int(UserEntry["Start"][17:19]))
						if SortPlayerOrder == "trophies":
							X.append(TimeNext - datetime.timedelta(minutes = 15))
							Y.append(CumTrophies)
							X.append(TimeNext)
							Y.append(UserEntry["CumTrophies"][0])
							CumTrophies = UserEntry["CumTrophies"][0]
						elif SortPlayerOrder == "points" or SortPlayerOrder == "title":
							X.append(TimeNext - datetime.timedelta(minutes = 15))
							Y.append(CumPoints)
							X.append(TimeNext)
							Y.append(UserEntry["CumPoints"])
							CumPoints = UserEntry["CumPoints"]
						elif SortPlayerOrder == "events":
							X.append(TimeNext - datetime.timedelta(minutes = 15))
							Y.append(CumEvents)
							X.append(TimeNext)
							Y.append(UserEntry["CumEvents"])
							CumEvents = UserEntry["CumEvents"]
						elif SortPlayerOrder == "maximum":
							X.append(TimeNext - datetime.timedelta(minutes = 15))
							Y.append(CumTopScore)
							X.append(TimeNext)
							Y.append(UserEntry["CumTopScore"])
							CumTopScore = UserEntry["CumTopScore"]
				# Add plot to mpl
				UserColor, UserStyle, UserMarker = UserHash(UserID)
				mpl.plot(X, Y, antialiased = True, color = UserColor, linestyle = UserStyle, marker = UserMarker, markevery = 0.1)	
	
			# Processing plot
			mpl.gca().set_ylim([0, None])
			mpl.legend(Legend, loc = 'upper left', fontsize = 11, title = "Top 10 players", title_fontsize = 11)	
			
			# Post-processing for all plots	
			mpl.xticks(rotation = 45)
			mpl.grid(alpha = 0.5)
			mpl.title(f"{self._Name} • {self._FilePlayersSorts[SortPlayerOrder]['Plot']}")
			mpl.tight_layout()
			
			# Add lichess logo as background, and fix aspect ratio to 1
			XMin, XMax = mpl.gca().get_xlim()
			YMin, YMax = mpl.gca().get_ylim()
			mpl.gca().imshow(LichessLogo, extent = [XMin, XMax, YMin, YMax], aspect = 'auto', alpha = 0.1)
			mpl.gca().set_aspect(abs((XMax - XMin) / (YMax - YMin)))
			
			# Export figure to file
			mpl.savefig(f"{self._PathFigures}{self._Prefix}_players_{SortPlayerOrder}.png")
			self.PrintMessage(f"Saved file {self._Prefix}_players_{SortPlayerOrder}.png.")
			mpl.clf()
		
	# 3b. Plots of arena statistics over time
	def _UpdateArenaPlots(self):

		# Load arenas list into temporary object
		if not os.path.exists(f"{self._PathRanking}{self._Prefix}_arenas.ndjson"):
			self.PrintMessage("Nothing to do...")
			return	
		self._LoadRankingList()
		if len(self._RankingList) == 0:
			self.PrintMessage("Nothing to do...")
			return

		# Process each sort order
		for SortArenaOrder in self._FileArenasSorts:
			
			# Initialize plotting procedure
			mpl.close()
			mpl.figure()
			Legend = []
			X = []
			Y = []

			# Load right data into X, Y lists
			for Index, ArenaID in enumerate(self._RankingList):
				ArenaInfo = self._RankingList[ArenaID]
				X.append(datetime.datetime(int(ArenaInfo["Start"][0:4]), int(ArenaInfo["Start"][5:7]), int(ArenaInfo["Start"][8:10]), int(ArenaInfo["Start"][11:13]), int(ArenaInfo["Start"][14:16]), int(ArenaInfo["Start"][17:19])))
				if SortArenaOrder == "newest":
					Y.append(Index)
				elif SortArenaOrder == "players":
					Y.append(ArenaInfo["Players"])
				elif SortArenaOrder == "points":
					Y.append(ArenaInfo["TotalPoints"] / max(1, ArenaInfo["Players"]))
				elif SortArenaOrder == "games":
					Y.append(ArenaInfo["Games"] / max(1, ArenaInfo["Players"]))
				elif SortArenaOrder == "moves":
					Y.append(ArenaInfo["Moves"] / max(1, ArenaInfo["Games"]) / 2)
				elif SortArenaOrder == "rating":
					Y.append(ArenaInfo["TotalRating"] / max(1, ArenaInfo["Players"]))
				elif SortArenaOrder == "maximum":
					Y.append(ArenaInfo["TopScore"])
				elif SortArenaOrder == "berserk":
					Y.append(100. * ArenaInfo["Berserks"] / max(1, ArenaInfo["Games"]) / 2.)	
			
			# Scatter plot of data
			PointSize = min(20., max(0.3, 1000./len(X)))
			mpl.scatter(X, Y, s = [PointSize] * len(X), color = tuple(x/510. for x in AllVariants[self._V]["RGB"]))
			Legend.insert(0, "All arenas")	
				
			# For big data sets, compute a moving average mean graph to plot as well	
			Thresholds = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
			# Moving average based on windows of 2% of the data, with step size 1%
			if len(X) > 200 and SortArenaOrder != "newest":
				CurThreshold = 0
				while len(X) > Thresholds[CurThreshold + 1]:
					CurThreshold = CurThreshold + 1
				WindowSize = round(Thresholds[CurThreshold] / 50)
				if self._E == "liga" and WindowSize < 100:
					WindowSize = 100
				HalfWindow = round(WindowSize / 2)
				XMean = []
				YMean = []
				for i in range(HalfWindow, len(X) - HalfWindow, HalfWindow):
					XMean.append(X[i])
					YMean.append(sum(Y[i - HalfWindow: i + HalfWindow]) / WindowSize / 1.)
				PointSizeMean = min(20., max(0.3, 1000./len(XMean)))
				#mpl.scatter(XMean, YMean, s = [PointSizeMean] * len(XMean), color = tuple(x/255. for x in AllVariants[self._V]["RGB"]))
				mpl.plot(XMean, YMean, color = tuple(x/255. for x in AllVariants[self._V]["RGB"]))
				Legend.insert(0, f"Moving average")
			
			lgnd = mpl.legend(Legend, markerscale = 3./PointSize, fontsize = 11, loc = 'upper left')
			
			#lgnd = mpl.legend(Legend, markerscale = 3./PointSize, fontsize = 10)
			for handle in lgnd.legendHandles:
				if str(handle) != 'Line2D(_line0)':
					handle.set_sizes([6.0])
				break
			
			# Add percent sign to y-axis for percentages
			if SortArenaOrder == "results" or SortArenaOrder == "berserk":
				mpl.gca().yaxis.set_major_formatter(PercentFormatter(decimals = 0))

			#mpl.yscale("log")
			# Post-processing for all plots
			mpl.xticks(rotation = 45)
			mpl.grid(alpha = 0.5)
			mpl.title(f"{self._Name} • {self._FileArenasSorts[SortArenaOrder]['Plot']}")
			mpl.tight_layout()
			
			# Add lichess logo as background, and fix aspect ratio to 1
			XMin, XMax = mpl.gca().get_xlim()
			YMin, YMax = mpl.gca().get_ylim()
			mpl.gca().imshow(LichessLogo, extent = [XMin, XMax, YMin, YMax], aspect = 'auto', alpha = 0.1)
			mpl.gca().set_aspect(abs((XMax - XMin) / (YMax - YMin)))
			
			# Export figure to file				
			mpl.savefig(f"{self._PathFigures}{self._Prefix}_arenas_{SortArenaOrder}.png")
			self.PrintMessage(f"Saved file {self._Prefix}_arenas_{SortArenaOrder}.png.")
			mpl.clf()	
		
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
	#######################################################################################################################################################################################
		
	# 4. Building the website for publication
	def UpdateWebsite(self):
		self.PrintMessage("4. Updating webpages...")
		if self._V == "3check" and self._E == "hourly":
			self._MakeColorCSS()
		self._UpdatePlayerPages()
		self._UpdateArenaPages()
		#self._MakeRedirects()
		
	# 4a. Update pages of lists/graphs of top players
	def _UpdatePlayerPages(self):

		for SortPlayerOrder in self._FilePlayersSorts:

			# Figure page
			with open(f"{self._PathWeb}graph_players_{SortPlayerOrder}.html", "w") as WebFile:
				self._WritePre(WebFile, "players_" + SortPlayerOrder, "graph")
				
				if len(self._DataList) == 0:
					WebFile.write("No rankings.")
				else:
					WebFile.write(f"<img src='figures/{self._V}_{self._E}_players_{SortPlayerOrder}.png' class='Graph'>")
					
				self._WritePost(WebFile)

			# List page
			with open(f"{self._PathWeb}list_players_{SortPlayerOrder}.html", "w") as WebFile:
				
				# Write preamble
				self._WritePre(WebFile, "players_" + SortPlayerOrder, "list")
						
				if len(self._DataList) == 0:
					WebFile.write("No rankings.")
				
				else:
					# Start of ranking list
					WebFile.write(f"This ranking is based on {strf(len(self._DataList), 'events')} events held between <a title='First event' href='https://lichess.org/tournament/{self._RankingInfo['FirstID']}'>{DateString(self._RankingInfo['FirstStart'][0:10])}</a> and <a title='Last event' href='https://lichess.org/tournament/{self._RankingInfo['LastID']}'>{DateString(self._RankingInfo['LastStart'][0:10])}</a>.\n\n")

					WebFile.write(f"In total, these arenas featured {strf(self._RankingInfo['Games'], 'games')} games (with {strf(self._RankingInfo['Moves'], 'moves')} moves), and the {strf(self._RankingInfo['Participants'], 'participants')} participants ({strf(self._RankingInfo['Players'], 'players')} unique players) scored a total of {strf(self._RankingInfo['TotalPoints'], 'points')} arena points.\n\n")
					
					WebFile.write(f"In these games, white scored <span class='info' title='{self._RankingInfo['WhiteWins']} out of {self._RankingInfo['Games']} games'>{round(100 * self._RankingInfo['WhiteWins'] / self._RankingInfo['Games'])}%</span> wins, <span class='info' title='{self._RankingInfo['Games'] - self._RankingInfo['WhiteWins'] - self._RankingInfo['BlackWins']} out of {self._RankingInfo['Games']} games'>{round(100 * (self._RankingInfo['Games'] - self._RankingInfo['WhiteWins'] - self._RankingInfo['BlackWins']) / self._RankingInfo['Games'])}%</span> draws, and <span class='info' title='{self._RankingInfo['BlackWins']} out of {self._RankingInfo['Games']} games'>{round(100 * self._RankingInfo['BlackWins'] / self._RankingInfo['Games'])}%</span> losses.\n\n")
					
					WebFile.write(f"The average berserk rate is <span class='info' title='{self._RankingInfo['Berserks']} berserks in {self._RankingInfo['Games']} games'>{round(500. * self._RankingInfo['Berserks'] / self._RankingInfo['Games']) / 10}%</span>, and the average rating is <span class='info' title='{self._RankingInfo['TotalRating']} over {self._RankingInfo['Participants']} participants'>{round(self._RankingInfo['TotalRating'] / self._RankingInfo['Participants'])}</span>.\n\n")
					
					WebFile.write("<table class='PlayersList'>\n")
					WebFile.write("\t<thead>\n")
					WebFile.write("\t<tr height='30px'>\n")
					WebFile.write("\t\t<td><span class='info' title='Ranking'><b>#</b></span></td>\n")
					WebFile.write("\t\t<td></td>\n")
					WebFile.write("\t\t<td><b>Username</b></td>\n")
					WebFile.write("\t\t<td><span class='info' style='font-family: lichess;' title='1st place finishes'>g</span></td>\n")
					WebFile.write("\t\t<td><span class='info' style='font-family: lichess;' title='2nd place finishes'>g</span></td>\n")
					WebFile.write("\t\t<td><span class='info' style='font-family: lichess;' title='3rd place finishes'>g</span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Total accumulated points'><b>Points</b></span></td>\n")
					WebFile.write("\t\t<td>/ <span class='info' title='Events with at least 1 point'><b>Events</b></span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Dates of first/last events'><b>First - Last</b></span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Average points per event'><b>Avg</b></span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Maximum score in one event'><b>Max</b></span></td>\n")
					WebFile.write("\t</tr>\n")
					WebFile.write("\t</thead>\n")
					WebFile.write("\t<tbody>\n")
					
					with open(f"{self._PathRanking}{self._Prefix}_players_{SortPlayerOrder}.ndjson", "r") as PlayersFile:
						for Index, Line in enumerate(PlayersFile):
							PlayerData = json.loads(Line)
							WebFile.write("\t<tr>\n")
							WebFile.write(f"\t\t<td>{Index + 1}.</td>\n")
							WebFile.write(f"\t\t<td>{PlayerData.get('Title', '')}</td>\n")
							WebFile.write(f"\t\t<td><a href='https://lichess.org/@/{PlayerData['Username'].lower()}'>{PlayerData['Username'].lower()}</a></td>\n")
							WebFile.write(f"\t\t<td>{PlayerData['Trophies'][0] if PlayerData['Trophies'][0] > 0 else ''}</td>\n")
							WebFile.write(f"\t\t<td>{PlayerData['Trophies'][1] if PlayerData['Trophies'][1] > 0 else ''}</td>\n")
							WebFile.write(f"\t\t<td>{PlayerData['Trophies'][2] if PlayerData['Trophies'][2] > 0 else ''}</td>\n")
							WebFile.write(f"\t\t<td>{PlayerData['Score']}</td>\n")
							WebFile.write(f"\t\t<td>/ {PlayerData['Events'] - PlayerData['Zeros']}</td>\n")
							WebFile.write(f"\t\t<td><!--<a href='https://lichess.org/tournament/{PlayerData['FirstID']}'>-->{self.TimeRange1(PlayerData['First'])}<!--</a>--> - ")
							WebFile.write(f"<!--<a href='https://lichess.org/tournament/{PlayerData['LastID']}'>-->{self.TimeRange2(PlayerData['Last'])}<!--</a>--></td>\n")
							#WebFile.write(f"\t<td><a href='https://lichess.org/tournament/{PlayerData['FirstID']}'>{self.TimeRange1(PlayerData['First'])}</a> - ")
							#WebFile.write(f"<a href='https://lichess.org/tournament/{PlayerData['LastID']}'>{self.TimeRange2(PlayerData['Last'])}</a></td>\n")
							WebFile.write(f"\t\t<td>{round(PlayerData['Score'] / max(1, (PlayerData['Events'] - PlayerData['Zeros'])))}</td>\n")
							WebFile.write(f"\t\t<td><a href='https://lichess.org/tournament/{PlayerData['TopScoreID']}'>{PlayerData['TopScore']}</a></td>\n")
							WebFile.write("\t</tr>\n")
							if Index == self._WebListLength - 1:
								break
					
					WebFile.write("\t</tbody>\n")
					WebFile.write("</table>\n")
			
				# Write after-code
				self._WritePost(WebFile)


	# 4b. Update pages of lists/graphs of arenas
	def _UpdateArenaPages(self):
		# Building list-pages of arenas
		for SortArenaOrder in self._FileArenasSorts:
		
			# Figure page
			with open(f"{self._PathWeb}graph_arenas_{SortArenaOrder}.html", "w") as WebFile:
				
				self._WritePre(WebFile, "arenas_" + SortArenaOrder, "graph")
				if len(self._DataList) == 0:
					WebFile.write("No rankings.")
				else:
					WebFile.write(f"<img src='figures/{self._V}_{self._E}_arenas_{SortArenaOrder}.png' class='Graph'>")
				self._WritePost(WebFile)
			
			# List page
			with open(f"{self._PathWeb}list_arenas_{SortArenaOrder}.html", "w") as WebFile:
				
				# Write preamble
				self._WritePre(WebFile, "arenas_" + SortArenaOrder, "list")
				
				if len(self._DataList) == 0:
					WebFile.write("No rankings.")
				
				else:
			
					# Start of ranking list
					WebFile.write(f"This ranking is based on {strf(len(self._DataList), 'events')} events held between <a title='First event' href='https://lichess.org/tournament/{self._RankingInfo['FirstID']}'>{DateString(self._RankingInfo['FirstStart'][0:10])}</a> and <a title='Last event' href='https://lichess.org/tournament/{self._RankingInfo['LastID']}'>{DateString(self._RankingInfo['LastStart'][0:10])}</a>.\n\n")

					WebFile.write(f"In total, these arenas featured {strf(self._RankingInfo['Games'], 'games')} games (with {strf(self._RankingInfo['Moves'], 'moves')} moves), and the {strf(self._RankingInfo['Participants'], 'participants')} participants ({strf(self._RankingInfo['Players'], 'players')} unique players) scored a total of {strf(self._RankingInfo['TotalPoints'], 'points')} arena points.\n\n")
					
					WebFile.write(f"In these games, white scored <span class='info' title='{self._RankingInfo['WhiteWins']} out of {self._RankingInfo['Games']} games'>{round(100 * self._RankingInfo['WhiteWins'] / self._RankingInfo['Games'])}%</span> wins, <span class='info' title='{self._RankingInfo['Games'] - self._RankingInfo['WhiteWins'] - self._RankingInfo['BlackWins']} out of {self._RankingInfo['Games']} games'>{round(100 * (self._RankingInfo['Games'] - self._RankingInfo['WhiteWins'] - self._RankingInfo['BlackWins']) / self._RankingInfo['Games'])}%</span> draws, and <span class='info' title='{self._RankingInfo['BlackWins']} out of {self._RankingInfo['Games']} games'>{round(100 * self._RankingInfo['BlackWins'] / self._RankingInfo['Games'])}%</span> losses.\n\n")
					
					WebFile.write(f"The average berserk rate is <span class='info' title='{self._RankingInfo['Berserks']} berserks in {self._RankingInfo['Games']} games'>{round(500. * self._RankingInfo['Berserks'] / self._RankingInfo['Games']) / 10}%</span>, and the average rating is <span class='info' title='{self._RankingInfo['TotalRating']} over {self._RankingInfo['Participants']} participants'>{round(self._RankingInfo['TotalRating'] / self._RankingInfo['Participants'])}</span>.\n\n")

					WebFile.write("<table class='ArenasList'>\n")
					WebFile.write("\t<thead>\n")
					WebFile.write("\t<tr height='40px'>\n")
					WebFile.write("\t\t<td><span class='info' title='Ranking'><b>#</b></span></td>\n")
					WebFile.write("\t\t<td>ID</td>\n")
					WebFile.write("\t\t<td><b>Type</b></td>\n")
					WebFile.write("\t\t<td><b>Date</b></td>\n")
					WebFile.write("\t\t<td><span class='info' style='font-family: lichess;' title='Participants'>f</span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Average rating over all players'><b>Rtng</b></span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Average points per player'><b>Pts</b></span></td>\n")
					#WebFile.write("\t\t<td><span class='info' title='Average games per player'>Gms</span></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Average moves per player per game'><b>Mvs</b></span></td>\n")
					WebFile.write("\t\t<td><span class='info' style='font-family: lichess;' title='Berserk rate'>`</span></td>\n")
					#WebFile.write("\t\t<td><span class='info' title='White wins/draws/black wins'>Result</span></td>\n")
					WebFile.write("\t\t<td><b>Winner</b></td>\n")
					WebFile.write("\t\t<td><span class='info' title='Score of winner'><b>Max</b></span></td>\n")
					WebFile.write("\t</tr>\n")
					WebFile.write("\t</thead>\n")
					WebFile.write("\t<tbody>\n")
					
					with open(f"{self._PathRanking}{self._Prefix}_arenas_{SortArenaOrder}.ndjson", "r") as ArenasFile:
						for Index, Line in enumerate(ArenasFile):
							ArenaData = json.loads(Line)
							WebFile.write("\t<tr>\n")
							WebFile.write(f"\t\t<td>{Index + 1}.</td>\n")
							WebFile.write(f"\t\t<td><a href='https://lichess.org/tournament/{ArenaData['ID']}'>{ArenaData['ID']}</a></td>\n")
							WebFile.write(f"\t\t<td><span class='info V{ArenaData['Variant']}' title='{AllVariants[ArenaData['Variant']]['Name']}'>{AllVariants[ArenaData['Variant']]['Code']}</span>/")
							WebFile.write(f"<span class='info E{ArenaData['Event']}' title='{AllEvents[ArenaData['Event']]['Name']}'>{AllEvents[ArenaData['Event']]['Code']}</span></td>\n")
							WebFile.write(f"\t\t<td>{self.DateString(ArenaData['Start'])}</td>\n")
							WebFile.write(f"\t\t<td>{ArenaData['Players']}</td>\n")
							WebFile.write(f"\t\t<td>{round(ArenaData['TotalRating']/max(1, ArenaData['Players']))}</td>\n")
							WebFile.write(f"\t\t<td>{round(ArenaData['TotalPoints']/max(1, ArenaData['Players']))}</td>\n")
							#WebFile.write(f"\t\t<td>{round(ArenaData['Games']/max(1, ArenaData['Players']))}</td>\n")
							WebFile.write(f"\t\t<td>{round(ArenaData['Moves']/max(2, 2 * ArenaData['Games']))}</td>\n")
							WebFile.write(f"\t\t<td>{round(100*ArenaData['Berserks']/max(2, 2 * ArenaData['Games']))}%</td>\n")
							#Draws = ArenaData['Games'] - ArenaData['WhiteWins'] - ArenaData['BlackWins']
							#WebFile.write(f"\t\t<td>{round(100*ArenaData['WhiteWins']/max(1, ArenaData['Games']))}/")
							#WebFile.write(f"{round(100*Draws/max(1, ArenaData['Games']))}/{round(100*ArenaData['BlackWins']/max(1, ArenaData['Games']))}</td>\n")
							WebFile.write(f"\t\t<td><a href='https://lichess.org/@/{ArenaData['#1'].lower()}'>{ArenaData['#1'].lower()}</a></td>\n")
							WebFile.write(f"\t\t<td>{ArenaData['TopScore']}</td>\n")
							WebFile.write("\t</tr>\n")
							if Index == self._WebListLength - 1:
								break
					
					WebFile.write("\t</tbody>\n")
					WebFile.write("</table>\n")
			
				# Write after-code
				self._WritePost(WebFile)		
				
				
	# 4c. Write the global preamble independent of content (but checked boxes depending on current page)
	def _WritePre(self, File, Page, Type):
		File.write("<!DOCTYPE html>\n")
		File.write("<html lang='en-US'>\n")
		File.write("<!-- Rankings built using the Lichess API (https://lichess.org/api) and some manual (python-based) tournament scraping. -->\n")
		File.write("<!-- Source code available at https://github.com/tmmlaarhoven/lichess -->\n")
		File.write("<head>\n")
		File.write(f"<title>Lichess Arena Rankings &middot; {self._Name}</title>\n")
		File.write("<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>\n")
		File.write("<link rel='icon' type='image/png' href='../../../favicon.ico'>\n")
		File.write("<link rel='stylesheet' href='../../../style-new.css'>\n")
		File.write("<link rel='stylesheet' href='../../../style-colors.css'>\n")
		File.write("<meta property='og:type' content='website'>\n")
		File.write(f"<meta property='og:title' content='Lichess Arena Rankings &middot; {self._Name}' />\n")
		File.write("<meta property='og:description' content='Statistics and rankings built from official Lichess arenas, ranging from hourly bullet arenas to titled arenas to bundesliga events. See who scored the most tournament victories, who played in the most events, who holds the all-time record for the highest score in each type of arena, and more!' />\n")
		File.write(f"<meta property='og:url' content='https://tmmlaarhoven.github.io/lichess/rankings/{self._V}/{self._E}/{Type}_{Page}.html' />\n")
		File.write(f"<meta property='og:image' content='https://tmmlaarhoven.github.io/lichess/rankings/{self._V}/{self._E}/figures/{self._V}_{self._E}_players_points.png' />\n")
		#File.write("<link rel='stylesheet' href='style-new.css'>\n")
		File.write("</head>\n\n")
		File.write("<body>\n")
		File.write(f"<div class=\"title\">Lichess Arena Rankings &middot; {self._Name}</div>\n")
		
		# Begin menu
		File.write("<div class='menu'>\n")
		
		# Information icon
		File.write("\t<span class='VariantIcon' style='font-size: 16pt; position: absolute; left: 0px;'><a href='../../index.html'>&#xe005;</a></span>\n")
		
		# Variants menu
		File.write("\t<span class='dropdown-el' style='left: 30px; min-width: 190px; max-width: 190px;'>\n")
		for V, Val in sorted(AllVariants.items(), key = lambda item: item[1]["WebOrder"]):
			File.write(f"\t\t<input type='radio' name='Variant' value='{V}' id='variant-{V}'{' checked' if V == self._V else ''}><label class='V{V}' for='variant-{V}'><span class='VariantIcon'>{AllVariants[V]['Icon']}</span> {AllVariants[V]['Name'] if V != 'all' else 'All variants'}</label>\n")
		File.write("\t</span>\n")
		
		# Events menu
		File.write("\t<span class='dropdown-el' style='left: 230px; min-width: 170px; max-width: 170px;'>\n")
		for E, Val in sorted(AllEvents.items(), key = lambda item: item[1]["WebOrder"]):
			File.write(f"\t\t<input type='radio' name='Event' value='{E}' id='events-{E}'{' checked' if E == self._E else ''}><label class='E{E}' for='events-{E}'>{AllEvents[E]['Name'] + ' Arenas' if E not in ['marathon', 'liga'] else ('Marathons' if E == 'marathon' else 'Bundesliga')}</label>\n")
		File.write("\t</span>\n")
		
		# Sorting menu
		File.write("\t<span class='dropdown-el' style='left: 410px; min-width: 260px; max-width: 260px;'>\n")
		for O in self._FilePlayersSorts:
			File.write(f"\t\t<input type='radio' name='Page' value='players_{O}' id='players_{O}'{' checked' if ('players_' + O) == Page else ''}><label for='players_{O}'>{self._FilePlayersSorts[O]['Name']}</label>\n")
		for O in self._FileArenasSorts:
			File.write(f"\t\t<input type='radio' name='Page' value='arenas_{O}' id='arenas_{O}'{' checked' if ('arenas_' + O) == Page else ''}><label for='arenas_{O}'>{self._FileArenasSorts[O]['Name']}</label>\n")
		File.write("\t</span>\n")
		
		# List or graph?
		File.write("\t<span class='dropdown-el' style='left: 680px; min-width: 120px; max-width: 120px;'>\n")
		File.write(f"\t\t<input type='radio' name='Type' value='list' id='list'{' checked' if Type == 'list' else ''}><label for='list'><span class='VariantIcon'>?</span> List</label>\n")
		File.write(f"\t\t<input type='radio' name='Type' value='graph' id='graph'{' checked' if Type == 'graph' else ''}><label for='graph'><span class='VariantIcon'>9</span> Graph</label>\n")
		File.write("\t</span>\n")
		
		File.write("</div>\n\n")				
		# End menu
		
		File.write("<span class='maincontent'>\n")
		File.write("<!-- START OF ACTUAL CONTENT -->\n")
		
		
	# 4d. Write after-code regardless of content
	def _WritePost(self, File):
	
		File.write("<!-- END OF ACTUAL CONTENT -->\n")
		File.write("</span>\n")
		File.write("<script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>\n")
		File.write("<script src='../../../menu.js'></script>\n")
		File.write("</body>\n")
		File.write("</html>\n")
		
	# 4e. Write color scheme to file
	def _MakeColorCSS(self):
		self.PrintMessage("Saving new color scheme!")
		NewTab = '\t'		# Backslashes cannot occur in f-strings
		with open(f"{self._PathWebRoot}style-colors.css", "w") as WebFile:
			WebFile.write(":root{\n\n")
			WebFile.write("\t/* Variant colors */\n")
			for V in AllVariants:
				WebFile.write(f"\t--CV{V}: {NewTab * math.ceil((20 - 6 - len(V)) / 4)}rgb{AllVariants[V]['RGB']};\n")
			WebFile.write("\n\t/* Event colors */\n")
			for E in AllEvents:
				WebFile.write(f"\t--CE{E}: {NewTab * math.ceil((20 - 6 - len(E)) / 4)}rgb{AllEvents[E]['RGB']};\n")
			WebFile.write("}\n")

	# 4f. Make pages to redirect old URLs to new URLs
	def _MakeRedirects(self):
		self.PrintMessage("Building redirect pages...")
		Redirects = {
			"trophies.html": 	f"list_players_trophies.html", 
			"index.html":		f"list_players_points.html",
			"events.html":		f"list_players_events.html",
			"maximum.html":		f"list_players_maximum.html",
			"stats.html":		f"list_arenas_players.html"
		}
		for OldPage in Redirects:
			NewPage = Redirects[OldPage]
			with open(f"{self._PathWeb}{OldPage}", "w") as WebFile:
				WebFile.write("<!DOCTYPE html>\n")
				WebFile.write("<html>\n")
				WebFile.write("<head>\n")
				WebFile.write(f"<meta http-equiv=\"refresh\" content=\"1; url={NewPage}\" />\n")
				WebFile.write("</head>\n")
				WebFile.write("<body>\n")
				WebFile.write("Redirecting to new page...\n")
				WebFile.write("</body>\n")
				WebFile.write("</html>")
				
